# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

from osv import fields,osv
from osv import orm

class purchase_tender(osv.osv):
    _name = "purchase.tender"
    _description="Purchase Tender"
    _columns = {
        'name': fields.char('Tender Reference', size=32,required=True),
        'date_start': fields.datetime('Date Start'),
        'date_end': fields.datetime('Date End'),
        'description': fields.text('Description'),
        'purchase_ids' : fields.one2many('purchase.order','tender_id','Purchase Orders')
    }
    _defaults = {
        'date_start': lambda *args: time.strftime('%Y-%m-%d %H:%M:%S'),
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'purchase.order.tender'),
    }
purchase_tender()

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    _description = "purchase order"
    _columns = {
        'tender_id' : fields.many2one('purchase.tender','Purchase Tender')
    }
    def wkf_confirm_order(self, cr, uid, ids, context={}):
        res = super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context)
        for po in self.browse(cr, uid, ids, context):
            for order in po.tender_id.purchase_ids:
                if order.id<>po.id:
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'purchase.order', order.id, 'purchase_cancel', cr)
        return res
purchase_order()
