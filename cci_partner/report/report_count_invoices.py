# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

import time
from report import report_sxw
import pooler

class cci_count_invoices(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(cci_count_invoices, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'partner_objects':self.partner_objects,
            'get_data': self.get_data,
        })

    def partner_objects(self,ids={}):
        if not ids:
            ids = self.ids
        partner_objects = pooler.get_pool(self.cr.dbname).get('res.partner').browse(self.cr, self.uid, ids)
        return partner_objects

    def get_data(self,object):

        result=[]
        obj_inv=pooler.get_pool(self.cr.dbname).get('account.invoice')
        obj_partner=pooler.get_pool(self.cr.dbname).get('res.partner')

        states=['draft','proforma','open','paid','cancel']
        types=['out_invoice','in_invoice']

        for type in types:
            res={}
            if type=='out_invoice':
                res['type']='Customer Invoice'
            else:
                res['type']='Supplier Invoice'

            for state in states:
                res[state]=0

            for state in states:
                find_ids=obj_inv.search(self.cr,self.uid,[('partner_id','=',object.id),('state','=',state),('type','=',type)])

                if find_ids:
                    res[state] +=len(find_ids)

            result.append(res)
        return result


report_sxw.report_sxw('report.cci.count.invoice', 'res.partner', 'addons/cci_partner/report/report_count_invoices.rml', parser=cci_count_invoices,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

