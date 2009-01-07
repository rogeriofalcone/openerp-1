# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
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
    "name":"Ampco",
    "version":"1.0",
    "author":"Tiny",
    "category":"Ampco",
    "description":'''Module for Quality information, Localisation''',
    "depends":[
        "base","product","sale"
       ],
    "demo_xml":[],
    "update_xml":[
            "security/ir.model.access.csv",
            "ampco_view.xml",
            "product_heatcode/product_heatcode_view.xml",
            "product_lot_foundary/product_lot_foundary.xml",
          ],
    "installable":True,
    "certificate": "475220159090247229"
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

