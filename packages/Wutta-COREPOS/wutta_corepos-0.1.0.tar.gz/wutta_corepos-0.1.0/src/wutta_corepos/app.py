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
App Provider
"""

from wuttjamaican.app import AppProvider


class WuttaCoreposAppProvider(AppProvider):
    """
    The :term:`app provider` for Wutta-COREPOS.

    This adds the :meth:`get_corepos_handler()` method for the
    :term:`app handler`.
    """

    def get_corepos_handler(self, **kwargs):
        if not hasattr(self, 'corepos_handler'):
            spec = self.config.get(f'{self.appname}.corepos_handler',
                                   default='wutta_corepos.handler:CoreposHandler')
            factory = self.app.load_object(spec)
            self.corepos_handler = factory(self.config, **kwargs)
        return self.corepos_handler
