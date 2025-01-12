# -*- coding: utf-8; -*-
################################################################################
#
#  Wutta-COREPOS -- Wutta Framework integration for CORE-POS
#  Copyright © 2024 Lance Edgar
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
App Configuration
"""

from wuttjamaican.conf import WuttaConfigExtension
from wuttjamaican.db.conf import get_engines


class WuttaCoreposConfigExtension(WuttaConfigExtension):
    """
    App :term:`config extension` for Wutta-COREPOS.

    This does some CORE DB connection setup based on config.  It will
    create three sets of DB engines, and establish one primary engine
    for each set.  The sets correspond to CORE Office DB types:

    * ``office_op`` (default name ``core_op``)
    * ``office_trans`` (default name ``core_trans``)
    * ``office_arch`` (default name ``trans_archive``)

    The config object will be given the following attributes:

    .. data:: core_office_op_engine

       Primary engine for the ``office_op`` DB.  May be null if no
       config is found.

    .. data:: core_office_op_engines

       Dict of ``office_op`` DB engines.  May be empty if no config is
       found; otherwise there should at least be a ``default`` key
       defined, corresonding to :data:`core_office_op_engine`.

    .. data:: core_office_trans_engine

       Primary engine for the ``office_trans`` DB.  May be null if no
       config is found.

    .. data:: core_office_trans_engines

       Dict of ``office_trans`` DB engines.  May be empty if no config
       is found; otherwise there should at least be a ``default`` key
       defined, corresonding to :data:`core_office_trans_engine`.

    .. data:: core_office_arch_engine

       Primary engine for the ``office_arch`` DB.  May be null if no
       config is found.

    .. data:: core_office_arch_engines

       Dict of ``office_arch`` DB engines.  May be empty if no config
       is found; otherwise there should at least be a ``default`` key
       defined, corresonding to :data:`core_office_arch_engine`.
    """
    key = 'wutta_corepos'

    def configure(self, config):
        """ """

        # office_op
        from corepos.db.office_op import Session
        engines = get_engines(config, 'corepos.db.office_op')
        config.core_office_op_engines = engines
        config.core_office_op_engine = engines.get('default')
        Session.configure(bind=config.core_office_op_engine)

        # office_trans
        from corepos.db.office_trans import Session
        engines = get_engines(config, 'corepos.db.office_trans')
        config.core_office_trans_engines = engines
        config.core_office_trans_engine = engines.get('default')
        Session.configure(bind=config.core_office_trans_engine)

        # office_arch
        from corepos.db.office_arch import Session
        engines = get_engines(config, 'corepos.db.office_arch')
        config.core_office_arch_engines = engines
        config.core_office_arch_engine = engines.get('default')
        Session.configure(bind=config.core_office_arch_engine)
