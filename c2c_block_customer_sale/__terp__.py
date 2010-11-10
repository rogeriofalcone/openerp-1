# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Block flow or warn user on Customer Sale',
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'description': """
     This module show a popup when confirming a SO on a customer that has reach his credit limit, but allow to confirm the SO. If the checkbox
     "Block this custmer" is ticked in the related partner form, then it raise a warning and forbid to confirm the SO.
    """,
    'author': 'camptocamp',
    'website': 'http://www.camptocamp.com',
    'depends': ['base', 'sale'],
    'init_xml': [],
    'update_xml': ['wizard/customer_credit_warning_view.xml',
                   'c2c_block_customer_sale_view.xml',
                   'sale_wkf.xml'],
    'demo_xml': [],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: