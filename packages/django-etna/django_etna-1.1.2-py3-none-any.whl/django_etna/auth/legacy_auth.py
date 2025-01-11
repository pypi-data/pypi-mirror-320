import json
import base64
import logging
import urllib
import requests
from typing import Dict, Optional

from OpenSSL import crypto
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from django.contrib.auth.backends import BaseBackend
from django.core.exceptions import ImproperlyConfigured
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.conf import settings

UserModel = get_user_model()

logger = logging.getLogger("django_etna.auth.legacy_auth")


class InvalidToken(Exception):
    pass


def _user_instance_from_identity(identity):
    if hasattr(UserModel, "from_identity"):
        user = UserModel.from_identity(identity)
    else:
        user = UserModel(id=identity["id"], login=identity["login"])
    user.identity = identity
    return user


def make_etna_token(identity: Dict, key: Optional[crypto.PKey] = None):
    identity = base64.b64encode(json.dumps(identity).encode())
    if key is None:
        signature = b""
    else:
        signed_identity = key.to_cryptography_key().sign(
            identity, padding.PKCS1v15(), hashes.SHA1()
        )
        signature = base64.b64encode(signed_identity)
    token = json.dumps({"identity": identity.decode(), "signature": signature.decode()})
    token = base64.b64encode(token.encode()).decode()
    return token


def _parse_and_validate_etna_token(raw_token: str, cert):
    try:
        decoded = json.loads(base64.b64decode(raw_token))
        identity = decoded["identity"]
        signature = decoded["signature"]
    except Exception as E:
        raise InvalidToken("cannot parse etna auth token") from E
    try:
        if cert is not None:
            cert.verify(
                base64.b64decode(signature),
                identity.encode(),
                padding.PKCS1v15(),
                hashes.SHA1(),
            )
    except Exception as E:
        raise InvalidToken("etna auth token verification failed") from E
    try:
        return json.loads(base64.b64decode(identity))
    except Exception as E:
        raise InvalidToken("cannot parse etna auth identity") from E


def extract_raw_token(request):
    auth_header = request.META.get("HTTP_AUTHORIZATION", None)
    if auth_header is not None:
        token = auth_header.split("Legacy ")[-1]
        if token and len(token) != len(auth_header):
            return token
    auth_cookie = request.COOKIES.get("authenticator", None)
    if auth_cookie is not None:
        token = urllib.parse.unquote_plus(auth_cookie)
        return token
    return None


class LegacyAuthTokenBackend(BaseBackend):
    def authenticate(
        self,
        request: HttpRequest,
        legacy_auth_token: str = None,
        legacy_auth_public_key=None,
        **ignored_other_credentials,
    ):
        if legacy_auth_token is None:
            return None
        try:
            identity = _parse_and_validate_etna_token(
                legacy_auth_token, legacy_auth_public_key
            )
        except InvalidToken as E:
            logger.warning(f"invalid legacy auth token, token=str(E)")
            return None
        user = _user_instance_from_identity(identity)
        user.legacy_auth_token = legacy_auth_token
        return user

    def get_user(self, user_id):
        """Return the User model corresponding to a given user_id.

        Session persistence works by storing only the user's primary key,
        and calling this method in each Auth Backends. We do not have a
        User table locally, as auth is delegated to a separate service.
        We could issue a call to that service, but it is faster to just
        reify the User model from the identity field of the decoded token.
        """
        return None


class LegacyAuthPasswordBackend(BaseBackend):
    def authenticate(
        self,
        request: HttpRequest,
        username=None,
        password=None,
        **ignored_other_credentials,
    ):
        logger.info(
            f"Authenticate with LegacyAuthPasswordBackend username={username}, password={password is not None}, ignored_other_credentials={repr(ignored_other_credentials)}"
        )
        if username is None or password is None:
            return None
        try:
            auth_url = settings.ETNA_AUTH_URL + "/identity"
            login_form = dict(login=username, password=password)
            response = requests.post(auth_url, data=login_form)
            logger.info(f"request status: {response.status_code}")
            if response.status_code == 200:
                identity = response.json()
                user = _user_instance_from_identity(identity)
                user.legacy_auth_token = response.cookies["authenticator"]
                return user
            else:
                logger.warning(f"auth login failed, status={response.status_code}")
        except Exception:
            logger.exception(f"failed to validate user/pasword against legacy auth")
        return None

    def get_user(self, user_id):
        "See LegacyAuthTokenBackend::get_user() above."
        return None


class LegacyAuthMiddleware:
    def __init__(self, get_response):
        # One-time configuration and initialization, at django startup.
        self._current_public_key_path = None
        self.get_response = get_response
        self._load_public_key(settings.ETNA_AUTH_PUBKEY_PATH)

    def _load_public_key(self, path):
        if path != self._current_public_key_path:
            logger.info(f"Loading auth signing certificates, path={path}")
            self._current_public_key_path = path
            if path == "/dev/null":
                self.public_key = None
                return
            with open(path, "r") as fp:
                content = fp.read()
                pubkey = crypto.load_publickey(crypto.FILETYPE_PEM, content)
            self.public_key = pubkey.to_cryptography_key()

    def __call__(self, request):
        # AuthenticationMiddleware is required so that request.user exists.
        self._load_public_key(settings.ETNA_AUTH_PUBKEY_PATH)
        if not hasattr(request, "user"):
            raise ImproperlyConfigured(
                "The Etna Legacy Auth middleware requires the authentication "
                " middleware to be installed. Edit your MIDDLEWARE setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the LegacyAuthMiddleware class."
            )
        raw_token = extract_raw_token(request)
        user = auth.authenticate(
            request, legacy_auth_token=raw_token, legacy_auth_public_key=self.public_key
        )
        if user:
            # User is valid. Set request.user
            request.user = user
            # We DO NOT persist the user in the session, unlike usual
            # auth middleware. See LegacyAuthMiddleware::get_user()
            # above for an # explanation.
            # auth.login(request,
        response = self.get_response(request)
        return response
