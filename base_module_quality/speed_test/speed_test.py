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

import netsvc
from osv import fields, osv
import os
from tools import config

from base_module_quality import base_module_quality


class quality_test(base_module_quality.abstract_quality_check):

    def __init__(self):
        self.result = """
Speed Test:
------------

    This test checks the speed of the module


        to be continued...
 
"""
        self.bool_installed_only = True
        return None

    def run_test(self, module_path):
        return None

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

