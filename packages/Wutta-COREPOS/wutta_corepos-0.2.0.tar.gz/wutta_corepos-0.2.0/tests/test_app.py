# -*- coding: utf-8; -*-

from wuttjamaican.testing import ConfigTestCase

from wutta_corepos import app as mod
from wutta_corepos.handler import CoreposHandler


class TestWuttaCoreposAppProvider(ConfigTestCase):

    def make_provider(self):
        return mod.WuttaCoreposAppProvider(self.config)

    def test_get_report_handler(self):
        handler = self.app.get_corepos_handler()
        self.assertIsInstance(handler, CoreposHandler)
