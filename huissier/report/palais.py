# -*- encoding: utf-8 -*-
# -*-encoding: iso8859-1 -*-
##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

from report.interface import report_rml
import pooler
from osv import osv

class huissier_palais(report_rml):
    def create(self, cr, uid, ids, datas, context):
        pool = pooler.get_pool(cr.dbname)
        new_ids = pool.get('huissier.dossier').search(cr, uid, [('tolist', '=', True), ('date_reelle','>=',datas['form']['date1']), ('date_reelle','<=',datas['form']['date2'])])
        return report_rml.create(self, cr,uid, new_ids, datas, context)

huissier_palais('report.huissier.palais', 'huissier.dossier', 'addons/huissier/report/palais.xml', 'addons/huissier/report/palais.xsl')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

