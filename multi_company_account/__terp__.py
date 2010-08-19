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
    "name" : "Multi company for accounting module",
    "version" : "0.1",
    "author" : "Tiny",
    "depends" : ["base", "account_budget", "account",  "multi_company"],
    "category" : "Generic Modules/Accounting",
    "description" : """Module to handle multi company accounting.""",
    "init_xml" : [],
    "demo_xml" : ["multi_company_account_demo.xml",],
    "update_xml" : [
        "multi_company_account_data.xml", 
        "multi_company_account_view.xml"
    ],
    "active": False,
    "installable": True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

