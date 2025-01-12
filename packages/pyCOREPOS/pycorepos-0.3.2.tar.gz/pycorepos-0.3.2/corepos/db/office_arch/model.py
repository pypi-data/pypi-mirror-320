# -*- coding: utf-8; -*-
################################################################################
#
#  pyCOREPOS -- Python Interface to CORE POS
#  Copyright © 2018-2024 Lance Edgar
#
#  This file is part of pyCOREPOS.
#
#  pyCOREPOS is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  pyCOREPOS is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  pyCOREPOS.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
CORE Office "arch" data model
"""

from sqlalchemy import orm

from corepos.db.office_trans.model import DTransactionBase, DLogBase


Base = orm.declarative_base()


class BigArchive(DTransactionBase, Base):
    """
    Represents a record from ``bigArchive`` table.
    """
    __tablename__ = 'bigArchive'


# TODO: deprecate / remove this
TransactionDetail = BigArchive


class DLogBig(DLogBase, Base):
    """
    Represents a record from ``dlogBig`` view.
    """
    __tablename__ = 'dlogBig'
