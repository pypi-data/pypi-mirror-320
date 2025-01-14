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
Wutta-COREPOS -- wuttaweb DB sessions

See :mod:`wuttaweb:wuttaweb.db.sess` for more info on web app sessions
in general.

.. class:: CoreOpSession

   Primary web app :term:`db session` for CORE Office 'op' DB.

.. class:: CoreTransSession

   Primary web app :term:`db session` for CORE Office 'trans' DB.

.. class:: CoreArchSession

   Primary web app :term:`db session` for CORE Office 'arch' DB.

.. class:: ExtraCoreOpSessions

   Dict of secondary CORE Office 'op' DB sessions, if applicable.

.. class:: ExtraCoreTransSessions

   Dict of secondary CORE Office 'trans' DB sessions, if applicable.

.. class:: ExtraCoreArchSessions

   Dict of secondary CORE Office 'arch' DB sessions, if applicable.
"""

from sqlalchemy.orm import sessionmaker, scoped_session
from zope.sqlalchemy import register


CoreOpSession = scoped_session(sessionmaker())
register(CoreOpSession)

CoreTransSession = scoped_session(sessionmaker())
register(CoreTransSession)

CoreArchSession = scoped_session(sessionmaker())
register(CoreArchSession)

# nb. these start out empty but may be populated on app startup
ExtraCoreOpSessions = {}
ExtraCoreTransSessions = {}
ExtraCoreArchSessions = {}
