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
Views for CORE-POS Members
"""

import sqlalchemy as sa
from sqlalchemy import orm

from corepos.db.office_op.model import MemberInfo

from wutta_corepos.web.views.corepos import CoreOpMasterView


class MemberView(CoreOpMasterView):
    """
    Master view for
    :class:`~pycorepos:corepos.db.office_op.model.MemberInfo`; route
    prefix is ``corepos_members``.

    Notable URLs provided by this class:

    * ``/corepos/members/``
    * ``/corepos/members/XXX``
    """
    model_class = MemberInfo
    model_title = "CORE-POS Member"
    route_prefix = 'corepos_members'
    url_prefix = '/corepos/members'

    # nb. this is just for readonly lookup
    creatable = False
    editable = False
    deletable = False

    grid_columns = [
        'card_number',
        'first_name',
        'last_name',
        'street',
        'city',
        'state',
        'zip',
        'phone',
        'email',
    ]

    filter_defaults = {
        'card_number': {'active': True, 'verb': 'equal'},
        'first_name': {'active': True, 'verb': 'contains'},
        'last_name': {'active': True, 'verb': 'contains'},
    }

    sort_defaults = 'card_number'

    def get_query(self, session=None):
        """ """
        query = super().get_query(session=session)

        op_model = self.corepos_handler.get_model_office_op()
        query = query.outerjoin(op_model.CustomerClassic,
                                sa.and_(
                                    op_model.CustomerClassic.card_number == op_model.MemberInfo.card_number,
                                    op_model.CustomerClassic.person_number == 1,
                                ))\
                     .options(orm.joinedload(op_model.MemberInfo.customers))

        return query

    def configure_grid(self, g):
        """ """
        super().configure_grid(g)
        op_model = self.corepos_handler.get_model_office_op()

        # first_name
        g.set_renderer('first_name', self.render_customer_attr)
        g.set_sorter('first_name', op_model.CustomerClassic.first_name)

        # last_name
        g.set_renderer('last_name', self.render_customer_attr)
        g.set_sorter('last_name', op_model.CustomerClassic.last_name)

    def render_customer_attr(self, member, key, value):
        """ """
        customer = member.customers[0]
        return getattr(customer, key)


def defaults(config, **kwargs):
    base = globals()

    MemberView = kwargs.get('MemberView', base['MemberView'])
    MemberView.defaults(config)


def includeme(config):
    defaults(config)
