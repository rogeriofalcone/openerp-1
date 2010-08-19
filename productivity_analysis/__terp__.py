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
    "name" : "Analyse the Productivity of Tiny ERP users",
    "version" : "1.0",
    "depends" : ["base"],
    "author" : "Tiny",
    "website" : "",
    "category" : "Generic Modules/Human Resources",
    "description": "A module that analyse the productivity of Tiny ERP users in terms of creation and modification of objects. It is able to render graphs, compare users, eso.",
    "init_xml" : [ ],
    "demo_xml" : [ ],
    "update_xml" : [
        "security/ir.model.access.csv",
        "productivity_analysis_view.xml",
        "productivity_analysis_wizard.xml",
        "productivity_analysis_report.xml",
    ],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

