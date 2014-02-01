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

import wizard
import netsvc
import pooler

def _makePo(self, cr, uid, data, context):
    wf_service = netsvc.LocalService("workflow")
    for id in data['ids']:
        wf_service.trg_validate(uid, 'purchase.order', id, 'purchase_confirm', cr)
        wf_service.trg_validate(uid, 'purchase.order', id, 'purchase_approve', cr)
    return {}

class confirm_po(wizard.interface):
    states = {
        'init' : {
            'actions' : [_makePo],
            'result' : {
                'type' : 'state',
                'state' : 'end'
            }
        },
    }
confirm_po("purchase.order.confirm.all")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

