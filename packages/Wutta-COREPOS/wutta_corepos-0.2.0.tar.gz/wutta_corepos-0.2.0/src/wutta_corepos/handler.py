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
CORE-POS Integration Handler
"""

from wuttjamaican.app import GenericHandler


class CoreposHandler(GenericHandler):
    """
    Base class and default implementation for the CORE-POS integration
    :term:`handler`.
    """

    def get_model_office_op(self):
        """
        Returns the :term:`data model` module for CORE Office 'op' DB,
        i.e. :mod:`pycorepos:corepos.db.office_op.model`.
        """
        from corepos.db.office_op import model

        return model

    def get_model_office_trans(self):
        """
        Returns the :term:`data model` module for CORE Office 'trans'
        DB, i.e. :mod:`pycorepos:corepos.db.office_trans.model`.
        """
        from corepos.db.office_trans import model

        return model

    def get_model_office_arch(self):
        """
        Returns the :term:`data model` module for CORE Office 'arch'
        DB, i.e. :mod:`pycorepos:corepos.db.office_arch.model`.
        """
        from corepos.db.office_arch import model

        return model

    def make_session_office_op(self, dbkey='default', **kwargs):
        """
        Make a new :term:`db session` for the CORE Office 'op' DB.

        :returns: Instance of
           :class:`pycorepos:corepos.db.office_op.Session`.
        """
        from corepos.db.office_op import Session

        if 'bind' not in kwargs:
            kwargs['bind'] = self.config.core_office_op_engines[dbkey]
        return Session(**kwargs)

    def make_session_office_trans(self, dbkey='default', **kwargs):
        """
        Make a new :term:`db session` for the CORE Office 'trans' DB.

        :returns: Instance of
           :class:`pycorepos:corepos.db.office_trans.Session`.
        """
        from corepos.db.office_trans import Session

        if 'bind' not in kwargs:
            kwargs['bind'] = self.config.core_office_trans_engines[dbkey]
        return Session(**kwargs)

    def make_session_office_arch(self, dbkey='default', **kwargs):
        """
        Make a new :term:`db session` for the CORE Office 'arch' DB.

        :returns: Instance of
           :class:`pycorepos:corepos.db.office_arch.Session`.
        """
        from corepos.db.office_arch import Session

        if 'bind' not in kwargs:
            kwargs['bind'] = self.config.core_office_arch_engines[dbkey]
        return Session(**kwargs)

    def get_office_url(self, require=False):
        """
        Returns the base URL for the CORE Office web app.

        Note that the return value is stripped of final slash.

        :param require: If true, an error is raised when URL cannot be
           determined.

        :returns: URL as string.
        """
        url = self.config.get('corepos.office.url', require=require)
        if url:
            return url.rstrip('/')

    def get_office_department_url(
            self,
            dept_id,
            office_url=None,
            require=False):
        """
        Returns the CORE Office URL for a Department.

        :param dept_id: Department ID for the URL.

        :param office_url: Root URL from :meth:`get_office_url()`.

        :param require: If true, an error is raised when URL cannot be
           determined.

        :returns: URL as string.
        """
        if not office_url:
            office_url = self.get_office_url(require=require)
        if office_url:
            return f'{office_url}/item/departments/DepartmentEditor.php?did={dept_id}'

    def get_office_likecode_url(
            self,
            likecode_id,
            office_url=None,
            require=False):
        """
        Returns the CORE Office URL for a Like Code.

        :param likecode_id: Like Code ID for the URL.

        :param office_url: Root URL from :meth:`get_office_url()`.

        :param require: If true, an error is raised when URL cannot be
           determined.

        :returns: URL as string.
        """
        if not office_url:
            office_url = self.get_office_url(require=require)
        if office_url:
            return f'{office_url}/item/likecodes/LikeCodeEditor.php?start={likecode_id}'

    def get_office_product_url(
            self,
            upc,
            office_url=None,
            require=False):
        """
        Returns the CORE Office URL for a Product.

        :param upc: UPC for the URL.

        :param office_url: Root URL from :meth:`get_office_url()`.

        :param require: If true, an error is raised when URL cannot be
           determined.

        :returns: URL as string.
        """
        if not office_url:
            office_url = self.get_office_url(require=require)
        if office_url:
            return f'{office_url}/item/ItemEditorPage.php?searchupc={upc}'

    def get_office_vendor_url(
            self,
            vend_id,
            office_url=None,
            require=False):
        """
        Returns the CORE Office URL for a Vendor.

        :param vend_id: Vendor ID for the URL.

        :param office_url: Root URL from :meth:`get_office_url()`.

        :param require: If true, an error is raised when URL cannot be
           determined.

        :returns: URL as string.
        """
        if not office_url:
            office_url = self.get_office_url(require=require)
        if office_url:
            return f'{office_url}/item/vendors/VendorIndexPage.php?vid={vend_id}'
