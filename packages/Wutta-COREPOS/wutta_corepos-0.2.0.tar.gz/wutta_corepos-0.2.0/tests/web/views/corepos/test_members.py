# -*- coding: utf-8; -*-

from sqlalchemy import orm

from corepos.db.office_op import model as op_model

from wuttaweb.testing import WebTestCase

from wutta_corepos.web.views.corepos import members as mod


class TestProductView(WebTestCase):

    def make_view(self):
        return mod.MemberView(self.request)

    def test_includeme(self):
        return mod.includeme(self.pyramid_config)

    def test_get_query(self):
        view = self.make_view()
        query = view.get_query()
        # TODO: not sure how to test the join other than doing data
        # setup and full runn-thru...and i'm feeling lazy
        self.assertIsInstance(query, orm.Query)

    def test_configure_grid(self):
        view = self.make_view()
        grid = view.make_grid(model_class=view.model_class)
        self.assertNotIn('first_name', grid.renderers)
        view.configure_grid(grid)
        self.assertIn('first_name', grid.renderers)

    def test_render_customer_attr(self):
        view = self.make_view()
        member = op_model.MemberInfo()
        customer = op_model.CustomerClassic(first_name="Fred")
        member.customers.append(customer)
        self.assertEqual(view.render_customer_attr(member, 'first_name', 'nope'), "Fred")
