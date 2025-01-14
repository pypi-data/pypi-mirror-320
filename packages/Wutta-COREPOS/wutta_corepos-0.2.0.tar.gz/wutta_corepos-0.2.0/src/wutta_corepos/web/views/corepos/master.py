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
CORE-POS master view base class
"""

from wuttaweb.views import MasterView

from wutta_corepos.web.db import CoreOpSession


class CoreOpMasterView(MasterView):
    """
    Base class for master views which use the CORE Office 'op' DB.
    """
    Session = CoreOpSession

    def __init__(self, request, context=None):
        super().__init__(request, context=context)
        self.corepos_handler = self.app.get_corepos_handler()
