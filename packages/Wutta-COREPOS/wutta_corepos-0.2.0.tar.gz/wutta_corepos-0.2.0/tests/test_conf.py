# -*- coding: utf-8; -*-

from unittest import TestCase

from wuttjamaican.conf import WuttaConfig

from wutta_corepos import conf as mod


class TestWuttaCoreposConfigExtension(TestCase):

    def test_configure(self):
        config = WuttaConfig()

        # no engines by default
        self.assertFalse(hasattr(config, 'core_office_op_engine'))
        self.assertFalse(hasattr(config, 'core_office_trans_engine'))
        self.assertFalse(hasattr(config, 'core_office_arch_engine'))
        ext = mod.WuttaCoreposConfigExtension()
        ext.configure(config)
        self.assertIsNone(config.core_office_op_engine)
        self.assertIsNone(config.core_office_trans_engine)
        self.assertIsNone(config.core_office_arch_engine)

        # but config can change that
        config.setdefault('corepos.db.office_op.default.url', 'sqlite://')
        ext.configure(config)
        self.assertIsNotNone(config.core_office_op_engine)
        self.assertEqual(str(config.core_office_op_engine.url), 'sqlite://')
