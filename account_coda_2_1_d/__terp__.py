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
    "name":"Account CODA Version 2.1 D - Helps to import bank statements from .csv file.",
    "version":"1.0.1",
    "author":"Open ERP",
    "category":"Account CODA",
    "description":"""Module provides functionality to import
    bank statements from .csv file.
    Import coda file wizard is used to import bank statements.""",
    "depends":["base", "account","account_report","base_iban"],
    "demo_xml":["coda_demo.xml"],
    "init_xml":[],
    "update_xml" : ["coda_wizard.xml","coda_view.xml"],
    "active":False,
    "installable":True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

