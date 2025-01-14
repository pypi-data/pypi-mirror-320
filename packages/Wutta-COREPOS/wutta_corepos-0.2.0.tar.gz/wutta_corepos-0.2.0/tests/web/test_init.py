# -*- coding: utf-8; -*-

from wuttaweb.testing import WebTestCase

from wutta_corepos import web as mod


class TestIncludeme(WebTestCase):

    def test_coverage(self):
        return mod.includeme(self.pyramid_config)
