# -*- coding: utf-8; -*-

from wuttaweb.testing import WebTestCase

from wutta_corepos.web.views.corepos import products as mod


class TestProductView(WebTestCase):

    def make_view(self):
        return mod.ProductView(self.request)

    def test_includeme(self):
        return mod.includeme(self.pyramid_config)

    def test_configure_grid(self):
        view = self.make_view()
        grid = view.make_grid(model_class=view.model_class)
        self.assertNotIn('upc', grid.linked_columns)
        view.configure_grid(grid)
        self.assertIn('upc', grid.linked_columns)
