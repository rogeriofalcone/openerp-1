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
    "name" : "Payement Term with Cash Discount",
    "version" : "1.0",
    "depends" : ["account",],
    "author" : "Tiny",
    "description" : "",
    "website" : "http://tinyerp.com/",
    "category" : "Generic Modules/Accounting",
    "description": """
    This module adds cash discounts on payment terms. Cash discounts
    for a payment term can be configured with:
        * A number of days,
        * A discount (%),
        * A debit and a credit account
    """,
    "init_xml" : [
    ],
    "demo_xml" : [
    ],
    "update_xml" : [
        "security/ir.model.access.csv",
        "account_cash_discount_view.xml",
    ],
    "active": False,
    "installable": True,
    "certificate": "814663129982322269"
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

