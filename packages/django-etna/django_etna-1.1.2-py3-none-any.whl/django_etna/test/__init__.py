import datetime
import logging
import os
from typing import Optional

import jinja2
import OpenSSL
from django.test import TestCase as DjangoTestCase
from django.test import TransactionTestCase as DjangoTransactionTestCase
from redgreenunittest.django.runner import RedGreenDiscoverRunner
from django.test.runner import DiscoverRunner
from django.test.signals import template_rendered
from django_etna.auth.test import IdentityMixin


def instrumented_render(original_render):
    def render(self, context, **more):
        """An instrumented Template render method, providing a signal that can be
        intercepted by the test Client.
        """
        c = dict(context)
        c.update(**more)
        template_rendered.send(sender=self, template=self, context=c)
        return original_render(self, context, **more)
    return render


if "DJANGO_ETNA_TEST_COLORS" in os.environ and os.environ["DJANGO_ETNA_TEST_COLORS"] == "true":
    DiscoverRunner = RedGreenDiscoverRunner


class Runner(DiscoverRunner):

    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        # monkey-patch jinja2 template render so that it emits a signal each time a template is rendered.
        self.original_j2_template_render = jinja2.Template.render
        jinja2.Template.render = instrumented_render(self.original_j2_template_render)

    def teardown_test_environment(self, **kwargs):
       jinja2.Template.render = self.original_j2_template_render
       super().teardown_test_environment(**kwargs)

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        logging.disable(logging.CRITICAL)
        return super().run_tests(test_labels, extra_tests, **kwargs)


class Loggable(IdentityMixin):
    def logged_as(self, user_id: int=None, login="", email=None, roles=[], key:Optional[OpenSSL.crypto.PKey] = None):
        return self.auth_identity({
            "id": user_id,
            "login": login,
            "email": email,
            "logas": False,
            "groups": roles,
            "login_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, key=key)


class TestCase(Loggable, DjangoTestCase):
    pass


class TransactionTestCase(Loggable, DjangoTransactionTestCase):
    pass
