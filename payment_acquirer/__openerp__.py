# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-Today OpenERP SA (<http://www.openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Payment Acquirer',
    'category': 'Hidden',
    'summary': 'Payment Acquirer Base Module',
    'version': '0.1',
    'description': """Payment Acquirer Base Module""",
    'author': 'OpenERP SA',
    'depends': ['decimal_precision', 'mail'],
    'data': [
        'views/payment_acquirer.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
