# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from osv import fields, osv
from tools.translate import _

class mgmtsystem_audit(osv.osv):
    _name = "mgmtsystem.audit"
    _description = "Audit"
    _columns = {
        'id': fields.integer('ID', readonly=True),
        'name': fields.char('Name', size=50),
        'date': fields.date('Date'),
        'line_ids': fields.one2many('mgmtsystem.verification.line','audit_id','Verification List'),
	'auditor_user_ids': fields.many2many('res.users','mgmtsystem_auditor_user_rel','user_id','mgmtsystem_audit_id','Auditors'),
	'auditee_user_ids': fields.many2many('res.users','mgmtsystem_auditee_user_rel','user_id','mgmtsystem_audit_id','Auditees'),
        'strong_points': fields.text('Strong Points'),
        'to_improve_points': fields.text('Points To Improve'),
        'imp_opp_ids': fields.many2many('mgmtsystem.action','mgmtsystem_audit_imp_opp_rel','mgmtsystem_action_id','mgmtsystem_audit_id','Improvement Opportunities'),
        'nonconformity_ids': fields.many2many('mgmtsystem.nonconformity','mgmtsystem_audit_nonconformity_rel','mgmtsystem_action_id','mgmtsystem_audit_id','Nonconformities'),
        'state': fields.selection([('o','Open'),('c','Closed')], 'State')
    }

    _defaults = {
        'state': 'o'
    }

mgmtsystem_audit()

class mgmtsystem_verification_line(osv.osv):
    _name = "mgmtsystem.verification.line"
    _description = "Verification Line"
    _columns = {
        'id': fields.integer('ID', readonly=True),
	'name': fields.char('Question',size=300, required=True),
        'audit_id': fields.many2one('mgmtsystem.audit', 'Audit', ondelete='cascade', select=True),
	'is_conformed': fields.boolean('Is conformed'),
	'comments': fields.text('Comments'),
    }

mgmtsystem_verification_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
