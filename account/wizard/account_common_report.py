# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
from lxml import etree

from osv import fields, osv
from tools.translate import _
import tools

class account_common_report(osv.osv_memory):
    _name = "account.common.report"
    _description = "Account Common Report"

    _columns = {
        'chart_account_id': fields.many2one('account.account', 'Chart of account', help='Select Charts of Accounts', required=True, domain = [('parent_id','=',False)]),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal year', help='Keep empty for all open fiscal year'),
        'filter': fields.selection([('filter_no', 'No Filters'), ('filter_date', 'Date'), ('filter_period', 'Periods')], "Filter by:", required=True),
        'period_from': fields.many2one('account.period', 'Start period'),
        'period_to': fields.many2one('account.period', 'End period'),
        #not used. Do we really need it? 'period_ids': fields.many2many('account.period', 'ledger_period_rel', 'ledger_id', 'period_id', 'Periods'),
        'journal_ids': fields.many2many('account.journal', 'account_common_journal_rel', 'account_id', 'journal_id', 'Journals', required=True),
        'date_from': fields.date("Start Date"),
        'date_to': fields.date("End Date"),

        #'display_account': fields.selection([('bal_mouvement','With movements'), ('bal_all','All'), ('bal_solde','With balance is not equal to 0')],"Display accounts"),
        #'amount_currency': fields.boolean("With Currency"),
        #'company_id': fields.many2one('res.company', 'Company', required=True),
    }

#    def _get_company(self, cr, uid, context=None):
#        user_obj = self.pool.get('res.users')
#        company_obj = self.pool.get('res.company')
#        if context is None:
#            context = {}
#        user = user_obj.browse(cr, uid, uid, context=context)
#        if user.company_id:
#           return user.company_id.id
#        else:
#           return company_obj.search(cr, uid, [('parent_id', '=', False)])[0]

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        mod_obj = self.pool.get('ir.model.data')
        res = super(account_common_report, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=False)
        if context.get('active_model', False) == 'account.account' and view_id:
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//field[@name='chart_account_id']")
            for node in nodes:
                node.set('readonly', '1')
                node.set('help', 'If you print the report from Account list/form view it will not consider Charts of account')
            res['arch'] = etree.tostring(doc)
        return res

    def onchange_filter(self, cr, uid, ids, filter='filter_no', context=None):
        res = {}
        if filter == 'filter_no':
            res['value'] = {'period_from': False, 'period_to': False}
            return res
        return {}

    def onchange_period_from(self, cr, uid, ids, filter='filter_no', period_from=False, context=None):
        period_obj = self.pool.get('account.period')
        res = {}
        if filter == 'filter_period':
            period_date_start = period_obj.read(cr, uid, period_from, ['date_start'])['date_start']
            res['value'] = {'date_from': period_date_start}
            return res
        return res

    def onchange_period_to(self, cr, uid, ids, filter='filter_no', period_to=False, context=None):
        period_obj = self.pool.get('account.period')
        res = {}
        if filter == 'filter_period':
            period_date_to = period_obj.read(cr, uid, period_to, ['date_stop'])['date_stop']
            res['value'] = {'date_to': period_date_to}
            return res
        return res

    def _get_account(self, cr, uid, context=None):
        accounts = self.pool.get('account.account').search(cr, uid, [], limit=1 )
        if not accounts:
            return False
        return accounts[0]

    def _get_fiscalyear(self, cr, uid, context=None):
        now = time.strftime('%Y-%m-%d')
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<', now), ('date_stop', '>', now)], limit=1 )
        if not fiscalyears:
            return False
        return fiscalyears[0]

    def _get_all_journal(self, cr, uid, context=None):
        return self.pool.get('account.journal').search(cr, uid ,[])

    _defaults = {
            'date_from' : time.strftime('%Y-01-01'),
            'date_to' : time.strftime('%Y-%m-%d'),
#            'company_id' : _get_company,
#            'display_account' : 'bal_all',
            'fiscalyear_id' : _get_fiscalyear,
#            'amount_currency' : True,
            'journal_ids': _get_all_journal,
            'filter': 'filter_no',
            'chart_account_id': _get_account,
    }

    def _build_context(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        result = {}
        period_obj = self.pool.get('account.period')
        result['fiscalyear'] = 'fiscalyear_id' in data['form'] and data['form']['fiscalyear_id'] or False
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['chart_account_id'] = 'chart_account_id' in data['form'] and data['form']['chart_account_id'] or False
        if data['form']['filter'] == 'filter_date':
            result['date_from'] = data['form']['date_from']
            result['date_to'] = data['form']['date_to']
        elif data['form']['filter'] == 'filter_period':
            if not data['form']['period_from'] or not data['form']['period_to']:
                raise osv.except_osv(_('Error'),_('Select Start period and End period'))
            elif (data['form']['period_from'] > data['form']['period_to']):
                raise osv.except_osv(_('Error'),_('Start period should be smaller then End period'))
            period_date_start = period_obj.read(cr, uid, data['form']['period_from'], ['date_start'])['date_start']
            period_date_stop = period_obj.read(cr, uid, data['form']['period_to'], ['date_stop'])['date_stop']
            cr.execute('SELECT id FROM account_period WHERE date_start >= %s AND date_stop <= %s', (period_date_start, period_date_stop))
            result['periods'] = map(lambda x: x[0], cr.fetchall())
        return result

    def _print_report(self, cr, uid, ids, data, query_line, context=None):
        raise (_('Error'), _('not implemented'))

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'period_from', 'period_to',  'filter',  'chart_account_id'])[0]
        if data['form']['filter'] == 'filter_period': # FIX Me => on_change on period from and to is not working so did this ..but correct it!
            start_date = self.onchange_period_from(cr, uid, ids, data['form']['filter'], data['form']['period_from'])
            end_date = self.onchange_period_to(cr, uid, ids, data['form']['filter'], data['form']['period_to'])
            data['form']['date_from'] = start_date['value']['date_from']
            data['form']['date_to'] = end_date['value']['date_to']
        used_context = self._build_context(cr, uid, ids, data, context)
        query_line = self.pool.get('account.move.line')._query_get(cr, uid, obj='l', context=used_context)
        if used_context.get('periods', False):
            data['form']['periods'] = used_context['periods']
        else:
            data['form']['periods'] = []
        return self._print_report(cr, uid, ids, data, query_line, context=context)

account_common_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: