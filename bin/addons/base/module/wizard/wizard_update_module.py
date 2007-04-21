# -*- coding: iso-8859-1 -*-
##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import wizard
import netsvc
import pooler

class wizard_update_module(wizard.interface):

	arch = '''<?xml version="1.0"?>
<form string="Scan for new modules">
  <label string="This function will check for new modules in the 'addons' path and on module repository." colspan="4" />
</form>
	'''
	fields = {}

	def _update_module(self, cr, uid, data, context):
		pooler.get_pool(cr.dbname).get('ir.module.module').update_list(cr, uid)
		return {}

	def _action_module_open(self, cr, uid, data, context):
		return {
			'domain': "[]",
			'name': 'Open Module List',
			'view_type': 'tree',
			'res_model': 'ir.module.category',
			'domain': "[('parent_id', '=', False)]",
			'view_id': False,
			'type': 'ir.actions.act_window'
		}

	states = {
		'init': {
			'actions': [],
			'result': {'type': 'form', 'arch': arch, 'fields': fields, 'state': [('end', 'Cancel', 'gtk-cancel'), ('update', 'Check new modules', 'gtk-ok')]}
		},
		'update': {
			'actions': [_update_module], 
			'result': {'type':'state', 'state':'open_window'}
		},
		'open_window': {
			'actions': [],
			'result': {'type': 'action', 'action': _action_module_open, 'state':'end'}
		}
	}
wizard_update_module('module.module.update')

