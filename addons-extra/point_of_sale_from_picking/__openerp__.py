# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com)
#        All Rights Reserved, Jesús Martín <jmartin@zikzakmedia.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    "name": "Point Of Sale From Picking",
    "version": "0.1",
    "author": "Zikzakmedia SL",
    "website": "http://www.zikzakmedia.com",
    "license" : "AGPL-3",
    "category": "Generic Modules/Sales & Purchases",
    "description": "This module adds a wizard that allows get order lines from an existing picking.",
    "depends": [
        'point_of_sale',
    ],
    "init_xml" : [ ],
    "demo_xml" : [ ],
    "update_xml" : [
        'point_of_sale_view.xml',
        'sale_shop_view.xml',
        'wizard/get_sale_view.xml',
    ],
    "installable": True,
}
