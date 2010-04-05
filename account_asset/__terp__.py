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
    "name" : "Asset management",
    "version" : "1.1",
    "depends" : ["account", "account_simulation"],
    "author" : "Tiny, Grzegorz Grzelak (Cirrus.pl)",
    "description": """Financial and accounting asset management.
    Allows to define
    * Asset category. 
    * Assets.
    * Asset usage period and method.
    * Asset method types
    * Default accounts for methods and categories
    * Depreciation methods:
        - Straight-Line
        - Declining-Balance
        - Sum of Year Digits
        - Units of Production
        - Progressive
    * Time methods:
        - Interval
        - End of Year
    """,
    "website" : "http://www.openerp.com",
    "category" : "Generic Modules/Accounting",
    "init_xml" : [
    ],
    "demo_xml" : [
    ],
    "update_xml" : [
        "security/ir.model.access.csv",
        "account_asset_wizard.xml",
        "account_asset_view.xml",
        "account_asset_invoice_view.xml"
    ],
#   "translations" : {
#       "fr": "i18n/french_fr.csv"
#   },
    "active": False,
    "installable": True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

