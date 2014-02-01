##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
    "name" : "Carriers and deliveries For Purchase Order",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Generic Modules/Sales & Purchases",
    "description": "Allows to add delivery methods in purchase order and packings. You can define your own carrier and delivery grids for prices. When creating invoices from pickings, Tiny ERP is able to add and compute the shipping line.",
    "depends" : ["sale","purchase", "stock",'delivery'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["delivery_view.xml","delivery_wizard.xml"],
    "active": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

