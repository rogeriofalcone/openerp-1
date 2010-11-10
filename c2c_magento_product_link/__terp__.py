# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Nicolas Bessi. Copyright Camptocamp SA
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
    'name' : 'Magento product link',
    'version' : '0.1',
    'depends' : ['base','account', 'product','magentoerpconnect'],
    'author' : 'Camptocamp',
    'description': """Add support for cross selling, equivalences, related product 
    No support for multi store. 
    TO DO :
    - Do real sychronisation not push pull
    - Access Rules
    
    """,
    'website': 'http://www.camptocamp.com',
    'init_xml': [],
    'update_xml': ['product_view.xml','shop_view.xml'],
    'demo_xml': [],
    'installable': True,
    'active': False,
}