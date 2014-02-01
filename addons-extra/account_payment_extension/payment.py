# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
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
from tools.translate import _

class payment_mode(osv.osv):
    _inherit = 'payment.mode'
    _columns = {
        'require_bank_account': fields.boolean('Require Bank Account', help='Ensure all lines in the payment order have a bank account when proposing lines to be added in the payment order.'),
    }
    _defaults = {
        'require_bank_account': lambda *a: False,
    }
payment_mode()

class payment_type(osv.osv):
    _inherit='payment.type'
    _description='Payment types'
    _columns = {
        'name': fields.char('Name', size=64, required=True, help='Payment Type', translate=True, select=True),
        'active': fields.boolean('Active', select=True),
        'note': fields.text('Description', translate=True, help="Description of the payment type that will be shown in the invoices"),
    }
    _defaults = {
        'active': lambda *a: 1,
    }
payment_type()


class res_partner(osv.osv):
    _inherit='res.partner'
    _columns={
        'payment_type_customer': fields.many2one('payment.type', 'Payment type', help="Payment type of the customer"),
        'payment_type_supplier': fields.many2one('payment.type', 'Payment type', help="Payment type of the supplier"),
    }
res_partner()


class res_partner_bank(osv.osv):

    def create(self, cr, uid, vals, context=None):
        if vals.get('default_bank') and vals.get('partner_id') and vals.get('state'):
            sql = "UPDATE res_partner_bank SET default_bank='0' WHERE partner_id=%i AND default_bank='1' AND state='%s'" % (vals['partner_id'], vals['state'])
            cr.execute(sql)
        return super(res_partner_bank, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if 'default_bank' in vals and vals['default_bank'] == True:
            partner_bank = self.pool.get('res.partner.bank').browse(cr, uid, ids)[0]
            partner_id = partner_bank.partner_id.id
            if 'state' in vals and vals['state']:
                state = vals['state']
            else:
                state = partner_bank.state
            sql = "UPDATE res_partner_bank SET default_bank='0' WHERE partner_id=%i AND default_bank='1' AND state='%s' AND id<>%i" % (partner_id, state, ids[0])
            cr.execute(sql)
        return super(res_partner_bank, self).write(cr, uid, ids, vals, context=context)

    _inherit="res.partner.bank"
    _columns = {
        'default_bank' : fields.boolean('Default'),
    }

res_partner_bank()


class payment_order(osv.osv):
    _name = 'payment.order'
    _inherit = 'payment.order'

    def _get_type(self, cr, uid, context=None):
        if context is None:
            context = {}
        return context.get('type', 'payable')

    def _get_reference(self, cr, uid, context=None):
        if context is None:
            context = {}
        type = context.get('type', 'payable')
        model = type == 'payable' and 'payment.order' or 'rec.payment.order'
        return self.pool.get('ir.sequence').get(cr, uid, model)

    def _get_period(self, cr, uid, context=None):
        try:
            # find() function will throw an exception if no period can be found for
            # current date. That should not be a problem because user would be notified
            # but as this model inherits an existing one, once installed it will create 
            # the new field and try to update existing records (even if there are no records yet)
            # So we must ensure no exception is thrown, otherwise the module can only be installed
            # once periods are created.
            periods = self.pool.get('account.period').find(cr, uid)
            return periods[0]
        except Exception, e:
            return False

    def _payment_type_name_get(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context):
            result[rec.id] = rec.mode and rec.mode.type.name or ""
        return result

    def _name_get(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context):
            result[rec.id] = rec.reference
        return result

    _columns = {
        'type': fields.selection([
            ('payable','Payable'),
            ('receivable','Receivable'),
            ],'Type', readonly=True, select=True),
        # invisible field to filter payment order lines by payment type
        'payment_type_name': fields.function(_payment_type_name_get, method=True, type="char", size=64, string="Payment type name"),
        # The field name is necessary to add attachement documents to payment orders
        'name': fields.function(_name_get, method=True, type="char", size=64, string="Name"),
        'create_account_moves': fields.selection([('bank-statement','Bank Statement'),('direct-payment','Direct Payment')],
                                                 'Create Account Moves',
                                                 required=True,
                                                 states={'done':[('readonly',True)]},
                                                 help='Indicates when account moves should be created for order payment lines. "Bank Statement" '\
                                                      'will wait until user introduces those payments in bank a bank statement. "Direct Payment" '\
                                                      'will mark all payment lines as payied once the order is done.'),
        'period_id': fields.many2one('account.period', 'Period', states={'done':[('readonly',True)]}),
    }
    _defaults = {
        'type': _get_type,
        'reference': _get_reference,
        'create_account_moves': lambda *a: 'bank-statement',
        'period_id': _get_period,
    }

    def unlink(self, cr, uid, ids, context=None):
        pay_orders = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for t in pay_orders:
            if t['state'] in ('draft', 'cancel'):
                unlink_ids.append(t['id'])
            else:
                raise osv.except_osv(_('Invalid action!'), _('You cannot delete payment order(s) which are already confirmed or done!'))
        result = super(payment_order, self).unlink(cr, uid, unlink_ids, context=context)
        return result

    def set_done(self, cr, uid, id, context=None):
        result = super(payment_order, self).set_done(cr, uid, id, context)

        company_currency_id = self.pool.get('res.users').browse(cr, uid, uid, context).company_id.currency_id.id

        order = self.browse(cr, uid, id, context)

        if order.create_account_moves != 'direct-payment':
            return result


        # This process creates a simple account move with bank and line accounts and line's amount. At the end
        # it will reconcile or partial reconcile both entries if that is possible.

        move_id = self.pool.get('account.move').create(cr, uid, {
            'name': '/',
            'journal_id': order.mode.journal.id,
            'period_id': order.period_id.id,
        }, context)

        total_amount = 0.0
        for line in order.line_ids:
            total_amount += line.amount

            if not line.amount:
                continue

            if not line.account_id:
                raise osv.except_osv(_('Error!'), _('Payment order should create account moves but line with amount %.2f for partner "%s" has no account assigned.') % (line.amount, line.partner_id.name ) )

            currency_id = order.mode.journal.currency and order.mode.journal.currency.id or company_currency_id

            if line.amount >= 0:
                account_id = order.mode.journal.default_credit_account_id.id
            else:
                account_id = order.mode.journal.default_debit_account_id.id
            acc_cur = ((line.amount<=0) and order.mode.journal.default_debit_account_id) or line.account_id

            amount = self.pool.get('res.currency').compute(cr, uid, currency_id, company_currency_id, line.amount, context=context, account=acc_cur)

            val = {
                'name': line.move_line_id and line.move_line_id.name or '/',
                'move_id': move_id,
                'date': order.date_done,
                'ref': line.move_line_id and line.move_line_id.ref or False,
                'partner_id': line.partner_id and line.partner_id.id or False,
                'account_id': line.account_id.id,
                'debit': ((amount>0) and amount) or 0.0,
                'credit': ((amount<0) and -amount) or 0.0,
                'journal_id': order.mode.journal.id,
                'period_id': order.period_id.id,
                'currency_id': currency_id,
            }
            
            amount = self.pool.get('res.currency').compute(cr, uid, currency_id, company_currency_id, line.amount, context=context, account=acc_cur)
            if currency_id <> company_currency_id:
                amount_cur = self.pool.get('res.currency').compute(cr, uid, company_currency_id, currency_id, amount, context=context, account=acc_cur)
                val['amount_currency'] = -amount_cur

            if line.account_id and line.account_id.currency_id and line.account_id.currency_id.id <> company_currency_id:
                val['currency_id'] = line.account_id.currency_id.id
                if company_currency_id == line.account_id.currency_id.id:
                    amount_cur = line.amount
                else:
                    amount_cur = self.pool.get('res.currency').compute(cr, uid, company_currency_id, line.account_id.currency_id.id, amount, context=context, account=acc_cur)
                val['amount_currency'] = amount_cur

            partner_line_id = self.pool.get('account.move.line').create(cr, uid, val, context, check=False)

            # Fill the secondary amount/currency
            # if currency is not the same than the company
            if currency_id <> company_currency_id:
                amount_currency = line.amount
                move_currency_id = currency_id
            else:
                amount_currency = False
                move_currency_id = False

            self.pool.get('account.move.line').create(cr, uid, {
                'name': line.move_line_id and line.move_line_id.name or '/',
                'move_id': move_id,
                'date': order.date_done,
                'ref': line.move_line_id and line.move_line_id.ref or False,
                'partner_id': line.partner_id and line.partner_id.id or False,
                'account_id': account_id,
                'debit': ((amount < 0) and -amount) or 0.0,
                'credit': ((amount > 0) and amount) or 0.0,
                'journal_id': order.mode.journal.id,
                'period_id': order.period_id.id,
                'amount_currency': amount_currency,
                'currency_id': move_currency_id,
            }, context)

            aml_ids = [x.id for x in self.pool.get('account.move').browse(cr, uid, move_id, context).line_id]
            for x in self.pool.get('account.move.line').browse(cr, uid, aml_ids, context):
                if x.state <> 'valid':
                    raise osv.except_osv(_('Error !'), _('Account move line "%s" is not valid') % x.name)

            if line.move_line_id and not line.move_line_id.reconcile_id:
                # If payment line has a related move line, we try to reconcile it with the move we just created.
                lines_to_reconcile = [
                    partner_line_id,
                ]

                # Check if payment line move is already partially reconciled and use those moves in that case.
                if line.move_line_id.reconcile_partial_id:
                    for rline in line.move_line_id.reconcile_partial_id.line_partial_ids:
                        lines_to_reconcile.append( rline.id )
                else:
                    lines_to_reconcile.append( line.move_line_id.id )

                amount = 0.0
                for rline in self.pool.get('account.move.line').browse(cr, uid, lines_to_reconcile, context):
                    amount += rline.debit - rline.credit

                currency = self.pool.get('res.users').browse(cr, uid, uid, context).company_id.currency_id

                if self.pool.get('res.currency').is_zero( cr, uid, currency, amount ):
                    self.pool.get('account.move.line').reconcile(cr, uid, lines_to_reconcile, 'payment', context=context)
                else:
                    self.pool.get('account.move.line').reconcile_partial(cr, uid, lines_to_reconcile, 'payment', context)

            if order.mode.journal.entry_posted:
                self.pool.get('account.move').write(cr, uid, [move_id], {
                    'state':'posted',
                }, context)

            self.pool.get('payment.line').write(cr, uid, [line.id], {
                'payment_move_id': move_id,
            }, context)

        return result

payment_order()


class payment_line(osv.osv):
    _name = 'payment.line'
    _inherit = 'payment.line'

    _columns = {
        'move_line_id': fields.many2one('account.move.line','Entry line', domain="[('reconcile_id','=', False), ('amount_to_pay','<>',0), ('account_id.type','=',parent.type),('payment_type','ilike',parent.payment_type_name or '%')]", help='This Entry Line will be referred for the information of the ordering customer.'),
        'payment_move_id': fields.many2one('account.move','Payment Move',readonly=True,help='Account move that pays this debt.'),
        'account_id': fields.many2one('account.account', 'Account'),
    }

    def onchange_move_line(self, cr, uid, ids, move_line_id, payment_type, date_prefered, date_planned, currency=False, company_currency=False, context=None):
        # Adds account.move.line name to the payment line communication
        res = super(payment_line, self).onchange_move_line(cr, uid, ids, move_line_id, payment_type, date_prefered, date_planned, currency, company_currency, context)
        if move_line_id:
            line = self.pool.get('account.move.line').browse(cr, uid, move_line_id)
            if line.name != '/':
                res['value']['communication'] = res['value']['communication'] + '. ' + line.name
            res['value']['account_id'] = line.account_id.id
        return res

payment_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
