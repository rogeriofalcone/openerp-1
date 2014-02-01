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
#    but WITHOUT ANY WARRANTY; without even the implied warranty ofbusiness
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name" : "Purchase - Purchase Tender",
    "version" : "0.1",
    "author" : "Tiny",
    "category" : "Generic Modules/Purchase",
    "website" : "http://www.openerp.com",
    "description": """ This module allows you to manage your Purchase Tenders. When a purchase order is created, you now have the opportunity to save the related tender. 
    This new object will regroup and will allow you to easily keep track and order all your purchase orders.
""",
    "depends" : ["purchase"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["purchase_tender_view.xml","purchase_tender_sequence.xml"],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

