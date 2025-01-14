# -*- coding: utf-8; -*-
################################################################################
#
#  Wutta-COREPOS -- Wutta Framework integration for CORE-POS
#  Copyright © 2025 Lance Edgar
#
#  This file is part of Wutta Framework.
#
#  Wutta Framework is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option) any
#  later version.
#
#  Wutta Framework is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  Wutta Framework.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Views for CORE-POS Products
"""

from corepos.db.office_op.model import Product

from wutta_corepos.web.views.corepos import CoreOpMasterView


class ProductView(CoreOpMasterView):
    """
    Master view for
    :class:`~pycorepos:corepos.db.office_op.model.Product`; route
    prefix is ``corepos_products``.

    Notable URLs provided by this class:

    * ``/corepos/products/``
    * ``/corepos/products/XXX``
    """
    model_class = Product
    model_title = "CORE-POS Product"
    route_prefix = 'corepos_products'
    url_prefix = '/corepos/products'

    # nb. this is just for readonly lookup
    creatable = False
    editable = False
    deletable = False

    labels = {
        'upc': "UPC",
    }

    grid_columns = [
        'upc',
        'brand',
        'description',
        'size',
        'department',
        'vendor',
        'normal_price',
    ]

    filter_defaults = {
        'upc': {'active': True, 'verb': 'contains'},
        'brand': {'active': True, 'verb': 'contains'},
        'description': {'active': True, 'verb': 'contains'},
    }

    sort_defaults = 'upc'

    def configure_grid(self, g):
        """ """
        super().configure_grid(g)

        # normal_price
        g.set_renderer('normal_price', 'currency')

        # links
        g.set_link('upc')
        g.set_link('brand')
        g.set_link('description')
        g.set_link('size')


def defaults(config, **kwargs):
    base = globals()

    ProductView = kwargs.get('ProductView', base['ProductView'])
    ProductView.defaults(config)


def includeme(config):
    defaults(config)
