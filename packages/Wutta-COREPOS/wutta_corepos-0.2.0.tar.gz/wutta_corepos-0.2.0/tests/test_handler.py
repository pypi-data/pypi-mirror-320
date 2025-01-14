# -*- coding: utf-8; -*-

from unittest.mock import patch

import sqlalchemy as sa
from sqlalchemy import orm

from wuttjamaican.testing import ConfigTestCase
from wuttjamaican.exc import ConfigurationError

from wutta_corepos import handler as mod


class TestCoreposHandler(ConfigTestCase):

    def make_handler(self):
        return mod.CoreposHandler(self.config)

    def test_get_model_office_op(self):
        from corepos.db.office_op import model
        handler = self.make_handler()
        op_model = handler.get_model_office_op()
        self.assertIs(op_model, model)

    def test_get_model_office_trans(self):
        from corepos.db.office_trans import model
        handler = self.make_handler()
        trans_model = handler.get_model_office_trans()
        self.assertIs(trans_model, model)

    def test_get_model_office_arch(self):
        from corepos.db.office_arch import model
        handler = self.make_handler()
        arch_model = handler.get_model_office_arch()
        self.assertIs(arch_model, model)

    def test_make_session_office_op(self):
        handler = self.make_handler()
        engine = sa.create_engine('sqlite://')
        with patch.object(self.config, 'core_office_op_engines', create=True,
                          new={'default': engine}):
            op_session = handler.make_session_office_op()
            self.assertIsInstance(op_session, orm.Session)
            self.assertIs(op_session.bind, engine)

    def test_make_session_office_trans(self):
        handler = self.make_handler()
        engine = sa.create_engine('sqlite://')
        with patch.object(self.config, 'core_office_trans_engines', create=True,
                          new={'default': engine}):
            trans_session = handler.make_session_office_trans()
            self.assertIsInstance(trans_session, orm.Session)
            self.assertIs(trans_session.bind, engine)

    def test_make_session_office_arch(self):
        handler = self.make_handler()
        engine = sa.create_engine('sqlite://')
        with patch.object(self.config, 'core_office_arch_engines', create=True,
                          new={'default': engine}):
            arch_session = handler.make_session_office_arch()
            self.assertIsInstance(arch_session, orm.Session)
            self.assertIs(arch_session.bind, engine)

    def test_get_office_url(self):
        handler = self.make_handler()

        # null by default
        self.assertIsNone(handler.get_office_url())

        # error if required
        self.assertRaises(ConfigurationError, handler.get_office_url, require=True)

        # config can specify (traliing slash is stripped)
        self.config.setdefault('corepos.office.url', 'http://localhost/fannie/')
        self.assertEqual(handler.get_office_url(), 'http://localhost/fannie')
        self.assertEqual(handler.get_office_url(require=True), 'http://localhost/fannie')

    def test_get_office_department_url(self):
        handler = self.make_handler()

        # null
        self.assertIsNone(handler.get_office_department_url(7))

        # typical
        self.config.setdefault('corepos.office.url', 'http://localhost/fannie/')
        self.assertEqual(handler.get_office_department_url(7), 'http://localhost/fannie/item/departments/DepartmentEditor.php?did=7')

    def test_get_office_likecode_url(self):
        handler = self.make_handler()

        # null
        self.assertIsNone(handler.get_office_likecode_url(7))

        # typical
        self.config.setdefault('corepos.office.url', 'http://localhost/fannie/')
        self.assertEqual(handler.get_office_likecode_url(7), 'http://localhost/fannie/item/likecodes/LikeCodeEditor.php?start=7')

    def test_get_office_product_url(self):
        handler = self.make_handler()

        # null
        self.assertIsNone(handler.get_office_product_url('07430500132'))

        # typical
        self.config.setdefault('corepos.office.url', 'http://localhost/fannie/')
        self.assertEqual(handler.get_office_product_url('07430500132'), 'http://localhost/fannie/item/ItemEditorPage.php?searchupc=07430500132')

    def test_get_office_vendor_url(self):
        handler = self.make_handler()

        # null
        self.assertIsNone(handler.get_office_vendor_url(7))

        # typical
        self.config.setdefault('corepos.office.url', 'http://localhost/fannie/')
        self.assertEqual(handler.get_office_vendor_url(7), 'http://localhost/fannie/item/vendors/VendorIndexPage.php?vid=7')
