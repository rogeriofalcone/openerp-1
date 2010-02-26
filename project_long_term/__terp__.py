# -*- coding: utf-8 -*-
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
    "name" : "Long Term Project Management",
    "version": "1.1",
    "author" : "Tiny",
    "website" : "http://www.openerp.com",
    "category" : "Generic Modules/Projects & Services",
    "depends" : ["project"],
    "description": """Long Term Project management module that track planning, scheduling, resources allocation.
    """,
    "init_xml" : [],
    "demo_xml" : [#"project_demo.xml"
],
    "update_xml": [
        "project_wizard.xml" ,
        "project_view.xml",
        "project_phase_workflow.xml"
    ],
    'installable': True,
    'active': False,
    'certificate': None,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
