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
CORE-POS Handler
"""

from wuttjamaican.app import GenericHandler


class CoreposHandler(GenericHandler):
    """
    Base class and default implementation for the CORE-POS integration
    :term:`handler`.
    """

    def get_office_url(self, require=False):
        """
        Returns the base URL for the CORE Office web app.

        Note that the return value is stripped of final slash.
        """
        url = self.config.get('corepos.office.url', require=require)
        if url:
            return url.rstrip('/')

    def get_office_department_url(
            self,
            number,
            office_url=None,
            require=False,
            **kwargs):
        """
        Returns the CORE Office URL for a Department.
        """
        if not office_url:
            office_url = self.get_office_url(require=require)
        if office_url:
            return f'{office_url}/item/departments/DepartmentEditor.php?did={number}'

    def get_office_likecode_url(
            self,
            id,
            office_url=None,
            require=False,
            **kwargs):
        """
        Returns the CORE Office URL for a Like Code.
        """
        if not office_url:
            office_url = self.get_office_url(require=require)
        if office_url:
            return f'{office_url}/item/likecodes/LikeCodeEditor.php?start={id}'

    def get_office_product_url(
            self,
            upc,
            office_url=None,
            require=False,
            **kwargs):
        """
        Returns the CORE Office URL for a Product.
        """
        if not office_url:
            office_url = self.get_office_url(require=require)
        if office_url:
            return f'{office_url}/item/ItemEditorPage.php?searchupc={upc}'

    def get_office_vendor_url(
            self,
            id,
            office_url=None,
            require=False,
            **kwargs):
        """
        Returns the CORE Office URL for a Vendor.
        """
        if not office_url:
            office_url = self.get_office_url(require=require)
        if office_url:
            return f'{office_url}/item/vendors/VendorIndexPage.php?vid={id}'
