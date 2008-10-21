# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
#
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
import netsvc
from osv import fields, osv
from mx import DateTime


class pos_config_journal(osv.osv):
    _name = 'pos.config.journal'
    _description = "Point of Sale journal configuration."
    _columns = {
        'name': fields.char('Description', size=64),
        'code': fields.char('Code', size=64),
        'journal_id': fields.many2one('account.journal', "Journal")
    }

pos_config_journal()


class pos_order(osv.osv):
    _name = "pos.order"
    _description = "Point of Sale"
    _order = "date_order, create_date desc"
    _order = "date_order desc"

    wf_service = netsvc.LocalService("workflow")

    def _amount_total(self, cr, uid, ids, field_name, arg, context):
        id_set = ",".join(map(str, ids))
        cr.execute("""
        SELECT
            p.id,
            COALESCE(SUM(
                l.price_unit*l.qty*(1-(l.discount/100.0)))::decimal(16,2), 0
                ) AS amount
        FROM pos_order p
            LEFT OUTER JOIN pos_order_line l ON (p.id=l.order_id)
        WHERE p.id IN (""" + id_set  +""") GROUP BY p.id """)
        res = dict(cr.fetchall())

        for rec in self.browse(cr, uid, ids, context):
            if rec.partner_id and rec.partner_id.property_account_tax:
                res[rec.id] = res[rec.id] - rec.amount_tax
        return res

    def _amount_tax(self, cr, uid, ids, field_name, arg, context):
        res = {}
        tax_obj = self.pool.get('account.tax')
        for order in self.browse(cr, uid, ids):
            val = 0.0
            for line in order.lines:
                val = reduce(lambda x, y: x+round(y['amount'], 2),
                        tax_obj.compute_inv(cr, uid, line.product_id.taxes_id,
                            line.price_unit * \
                            (1-(line.discount or 0.0)/100.0), line.qty),
                            val)

            res[order.id] = val
        return res

    def _total_payment(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for order in self.browse(cr, uid, ids):
            val = 0.0
            for payment in order.payments:
                val += payment.amount
            res[order.id] = val
        return res

    def _total_return(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for order in self.browse(cr, uid, ids):
            val = 0.0
            for payment in order.payments:
                val += (payment.amount < 0 and payment.amount or 0)
            res[order.id] = val
        return res

    def payment_get(self, cr, uid, ids, context=None):
        cr.execute("select id from pos_payment where order_id in (%s)" % \
                    ','.join([str(i) for i in ids]))
        return [i[0] for i in cr.fetchall()]

    def _sale_journal_get(self, cr, uid, context):
        journal_obj = self.pool.get('account.journal')
        res = journal_obj.search(cr, uid,
            [('type', '=', 'sale')], limit=1)
        if res:
            return res[0]
        else:
            return False

    def _receivable_get(self, cr, uid, context=None):
        prop_obj = self.pool.get('ir.property')
        res = prop_obj.get(cr, uid, 'property_account_receivable', 'res.partner', context=context)
        return res

    def copy(self, cr, uid, id, default=None, context={}):
        if not default:
            default = {}
        default.update({
            'state': 'draft',
            'payments': [],
            'partner_id': False,
            'invoice_id': False,
            'account_move': False,
            'last_out_picking': False,
            'nb_print': 0,
            'pickings': []
        })
        return super(pos_order, self).copy(cr, uid, id, default, context)

    _columns = {
        'name': fields.char('Order Description', size=64, required=True,
            states={'draft': [('readonly', False)]}, readonly=True),
        'shop_id': fields.many2one('sale.shop', 'Shop', required=True,
            states={'draft': [('readonly', False)]}, readonly=True),
        'date_order': fields.date('Date Ordered', readonly=True),
        'date_validity': fields.date('Validity Date', required=True),
        'user_id': fields.many2one('res.users', 'Salesman',
            readonly=True),
        'amount_tax': fields.function(_amount_tax, method=True, string='Taxes'),
        'amount_total': fields.function(_amount_total, method=True,
            string='Total'),
        'amount_paid': fields.function(_total_payment, 'Paid',
            states={'draft': [('readonly', False)]}, readonly=True,
            method=True),
        'amount_return': fields.function(_total_return, 'Returned',
                                        method=True),
        'lines': fields.one2many('pos.order.line', 'order_id',
            'Order Lines', states={'draft': [('readonly', False)]},
            readonly=True),
        'payments': fields.one2many('pos.payment', 'order_id',
            'Order Payments', states={'draft': [('readonly', False)]},
            readonly=True),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist',
            required=True, states={'draft': [('readonly', False)]},
            readonly=True),
        'partner_id': fields.many2one(
            'res.partner', 'Partner', change_default=True,
            states={'draft': [('readonly', False)], 'paid': [('readonly', False)]},
            readonly=True),
        'state': fields.selection([('cancel', 'Cancel'), ('draft', 'Draft'),
            ('paid', 'Paid'), ('done', 'Done'), ('invoiced', 'Invoiced')], 'State',
            readonly=True, ),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', readonly=True),
        'account_move': fields.many2one('account.move', 'Account Entry',
            readonly=True),
        'pickings': fields.one2many('stock.picking', 'pos_order', 'Picking',
            readonly=True),
        'last_out_picking': fields.many2one('stock.picking',
                                            'Last output picking',
                                            readonly=True),
        'note': fields.text('Notes'),
        'nb_print': fields.integer('Number of print', readonly=True),
        'sale_journal': fields.many2one('account.journal', 'Journal',
            required=True, states={'draft': [('readonly', False)]},
            readonly=True, ),
        'account_receivable': fields.many2one('account.account',
            'Default Receivable', required=True, states={'draft': [('readonly', False)]},
            readonly=True, ),
        'invoice_wanted': fields.boolean('Create invoice')
        }

    def _journal_default(self, cr, uid, context={}):
        journal_list = self.pool.get('account.journal').search(cr, uid, [('type', '=', 'cash')])
        if journal_list:
            return journal_list[0]
        else:
            return False

    _defaults = {
        'user_id': lambda self, cr, uid, context: uid,
        'state': lambda *a: 'draft',
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence')\
            .get(cr, uid, 'pos.order'),
        'date_order': lambda *a: time.strftime('%Y-%m-%d'),
        'date_validity': lambda *a: (DateTime.now() + DateTime.RelativeDateTime(months=+6)).strftime('%Y-%m-%d'),
        'nb_print': lambda *a: 0,
        'sale_journal': _sale_journal_get,
        'account_receivable': _receivable_get,
        'invoice_wanted': lambda *a: False
    }

    def test_order_lines(self, cr, uid, order, context={}):
        if not order.lines:
            raise osv.except_osv("Error", "No order lines defined for this sale.")

        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'pos.order', order.id, 'paid', cr)
        return True

    def dummy_button(self, cr, uid, order, context={}):
        return True

    def test_paid(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context):
            if order.lines and not order.amount_total:
                return True
            if (not order.lines) or (not order.payments) or \
                (order.amount_paid != order.amount_total):
                return False
        return True

    def _get_qty_differences(self, orders, old_picking):
        """check if the customer changed the product quantity"""
        order_dict = {}
        for order in orders:
            for line in order.lines:
                order_dict[line.product_id.id] = line

        # check the quantity differences:
        diff_dict = {}
        for line in old_picking.move_lines:
            order_line = order_dict.get(line.product_id.id)
            if not order_line:
                deleted = True
                qty_to_delete_from_original_picking = line.product_qty
                diff_dict[line.product_id.id] = (deleted, qty_to_delete_from_original_picking)
            elif line.product_qty != order_line.qty:
                deleted = False
                qty_to_delete_from_original_picking = line.product_qty - order_line.qty
                diff_dict[line.product_id.id] = (deleted, qty_to_delete_from_original_picking)

        return diff_dict

    def _split_picking(self, cr, uid, ids, context, old_picking, diff_dict):
        """if the customer changes the product quantity, split the picking in two"""
        # create a copy of the original picking and adjust the product qty:
        picking_model = self.pool.get('stock.picking')
        defaults = {
            'note': "Partial picking from customer", # add a note to tell why we create a new picking
            'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out'), # increment the sequence
        }

        new_picking_id = picking_model.copy(cr, uid, old_picking.id, defaults) # state = 'draft'
        new_picking = picking_model.browse(cr, uid, new_picking_id, context)

        for line in new_picking.move_lines:
            p_id = line.product_id.id
            if p_id in diff_dict:
                diff = diff_dict[p_id]
                deleted = diff[0]
                qty_to_del = diff[1]
                if deleted: # product has been deleted (customer didn't took it):
                    # delete this product from old picking:
                    for old_line in old_picking.move_lines:
                        if old_line.product_id.id == p_id:
                            old_line.write(cr, uid, [old_line.id], {'state': 'draft'}) # cannot delete if not draft
                            old_line.unlink(cr, uid, [old_line.id], context)
                elif qty_to_del > 0: # product qty has been modified (customer took less than the ordered quantity):
                    # subtract qty from old picking:
                    for old_line in old_picking.move_lines:
                        if old_line.product_id.id == p_id:
                            old_line.write(cr, uid, [old_line.id], {'product_qty': old_line.product_qty - qty_to_del})
                    # add qty to new picking:
                    line.write(cr, uid, [line.id], {'product_qty': qty_to_del})
                else: # product hasn't changed (customer took it without any change):
                    # delete this product from new picking:
                    line.unlink(cr, uid, [line.id], context)
            else:
                # delete it in the new picking:
                line.unlink(cr, uid, [line.id], context)

    def create_picking(self, cr, uid, ids, context={}):
        """Create a picking for each order and validate it."""
        picking_obj = self.pool.get('stock.picking')

        orders = self.browse(cr, uid, ids, context)
        for order in orders:
            if not order.last_out_picking:
                new = True
                picking_id = picking_obj.create(cr, uid, {
                    'origin': order.name,
                    'type': 'out',
                    'state': 'draft',
                    'move_type': 'direct',
                    'note': 'POS notes ' + (order.note or ""),
                    'invoice_state': 'none',
                    'auto_picking': True,
                    'pos_order': order.id,
                    })
                self.write(cr, uid, [order.id], {'last_out_picking': picking_id})
            else:
                picking_id = order.last_out_picking.id
                picking_obj.write(cr, uid, [picking_id], {'auto_picking': True})
                picking = picking_obj.browse(cr, uid, [picking_id], context)[0]
                new = False

                # split the picking (if product quantity has changed):
                diff_dict = self._get_qty_differences(orders, picking)
                if diff_dict:
                    self._split_picking(cr, uid, ids, context, picking, diff_dict)

            if new:
                for line in order.lines:
                    prop_ids = self.pool.get("ir.property").search(cr, uid,
                            [('name', '=', 'property_stock_customer')])
                    val = self.pool.get("ir.property").browse(cr, uid,
                            prop_ids[0]).value
                    location_id = order.shop_id.warehouse_id.lot_stock_id.id
                    stock_dest_id = int(val.split(',')[1])
                    if line.qty < 0:
                        (location_id, stock_dest_id)= (stock_dest_id, location_id)

                    self.pool.get('stock.move').create(cr, uid, {
                        'name': 'Stock move (POS %d)' % (order.id, ),
                        'product_uom': line.product_id.uom_id.id,
                        'product_uos': line.product_id.uom_id.id,
                        'picking_id': picking_id,
                        'product_id': line.product_id.id,
                        'product_uos_qty': line.qty,
                        'product_qty': line.qty,
                        'tracking_id': False,
                        'state': 'waiting',
                        'location_id': location_id,
                        'location_dest_id': stock_dest_id,
                    })

            self.wf_service.trg_validate(uid, 'stock.picking',
                    picking_id, 'button_confirm', cr)
            self.pool.get('stock.picking').force_assign(cr,
                    uid, [picking_id], context)

        return True

    def set_to_draft(self, cr, uid, ids, *args):
        if not len(ids):
            return False

        self.write(cr, uid, ids, {'state': 'draft'})

        wf_service = netsvc.LocalService("workflow")
        for i in ids:
            wf_service.trg_create(uid, 'pos.order', i, cr)
        return True

    def cancel_order(self, cr, uid, ids, context=None):
        """Cancel each picking with an inverted one."""

        picking_obj = self.pool.get('stock.picking')
        stock_move_obj = self.pool.get('stock.move')
        payment_obj = self.pool.get('pos.payment')
        picking_ids = picking_obj.search(cr, uid, [('pos_order', 'in', ids), ('state', '=', 'done')])
        clone_list = []

        # Copy all the picking and blank the last_out_picking
        for order in self.browse(cr, uid, ids, context=context):
            if not order.last_out_picking:
                continue

            clone_id = picking_obj.copy(
                cr, uid, order.last_out_picking.id, {'type': 'in'})
            # Confirm the picking
            self.wf_service.trg_validate(uid, 'stock.picking',
                clone_id, 'button_confirm', cr)
            clone_list.append(clone_id)
            # Remove the ref to last picking and delete the payments
            self.write(cr, uid, ids, {'last_out_picking': False})
            payment_obj.unlink(cr, uid, [i.id for i in order.payments],
                context=context)

            # Switch all the moves
            move_ids = stock_move_obj.search(
                cr, uid, [('picking_id', '=', clone_id)])
            for move in stock_move_obj.browse(cr, uid, move_ids, context=context):
                stock_move_obj.write(
                    cr, uid, move.id, {'location_id': move.location_dest_id.id,
                                    'location_dest_id': move.location_id.id})

        self.pool.get('stock.picking').force_assign(cr,
            uid, clone_list, context)

        return True

    def add_payment(self, cr, uid, order_id, amount, journal, context=None):
        """Create a new payment for the order"""

        order = self.browse(cr, uid, order_id, context)
        if order.invoice_wanted and not order.partner_id:
            raise osv.except_osv("Error", "Cannot create invoice without a partner.")

        payment_id = self.pool.get('pos.payment').create(cr, uid, {
            'order_id': order_id,
            'journal_id': journal,
            'amount': amount,
            })

        self.wf_service.trg_validate(uid, 'pos.order', order_id, 'payment', cr)
        self.wf_service.trg_write(uid, 'pos.order', order_id, cr)
        return payment_id

    def add_product(self, cr, uid, order_id, product_id, qty, context=None):
        """Create a new order line the order"""
        line_obj = self.pool.get('pos.order.line')
        values = self.read(cr, uid, order_id, ['partner_id', 'pricelist_id'])

        pricelist = values['pricelist_id'] and values['pricelist_id'][0]
        product = values['partner_id'] and values['partner_id'][0]

        price = line_obj.price_by_product(cr, uid, [],
                pricelist, product_id, qty, product)

        order_line_id = line_obj.create(cr, uid, {
            'order_id': order_id,
            'product_id': product_id,
            'qty': qty,
            'price_unit': price,
            })
        self.wf_service.trg_write(uid, 'pos.order', order_id, cr)

        return order_line_id

    def refund(self, cr, uid, ids, context={}):
        clone_list = []
        line_obj = self.pool.get('pos.order.line')

        for order in self.browse(cr, uid, ids):
            clone_id = self.copy(cr, uid, order.id, {
                'name': order.name + ' REFUND',
                'date_order': time.strftime('%Y-%m-%d'),
                'state': 'draft',
                'note': 'REFUND\n'+ (order.note or ''),
                'invoice_id': False,
                'nb_print': 0,
                'payments': False,
                })
            clone_list.append(clone_id)


        for clone in self.browse(cr, uid, clone_list):
            for order_line in clone.lines:
                line_obj.write(cr, uid, [order_line.id], {
                    'qty': -order_line.qty
                    })
        return clone_list

    def action_invoice(self, cr, uid, ids, context={}):
        inv_ref = self.pool.get('account.invoice')
        inv_line_ref = self.pool.get('account.invoice.line')
        inv_ids = []

        for order in self.browse(cr, uid, ids, context):
            if order.invoice_id:
                inv_ids.append(order.invoice_id.id)
                continue

            if not order.partner_id:
                raise osv.except_osv('Error', 'Please provide a partner for the sale.')

            inv = {
                'name': 'Invoice from POS: '+order.name,
                'origin': order.name,
                'type': 'out_invoice',
                'reference': order.name,
                'partner_id': order.partner_id.id,
                'comment': order.note or '',
                'price_type': 'tax_included'
            }
            inv.update(inv_ref.onchange_partner_id(cr, uid, [], 'out_invoice', order.partner_id.id)['value'])
            inv_id = inv_ref.create(cr, uid, inv, context)

            self.write(cr, uid, [order.id], {'invoice_id': inv_id, 'state': 'invoiced'})
            inv_ids.append(inv_id)

            for line in order.lines:
                inv_line = {
                    'invoice_id': inv_id,
                    'product_id': line.product_id.id,
                    'quantity': line.qty,
                }
                inv_line.update(inv_line_ref.product_id_change(cr, uid, [],
                    line.product_id.id,
                    line.product_id.uom_id.id,
                    line.qty, partner_id = order.partner_id.id)['value'])
                inv_line['price_unit'] = line.price_unit
                inv_line['discount'] = line.discount

                inv_line['invoice_line_tax_id'] = ('invoice_line_tax_id' in inv_line)\
                    and [(6, 0, inv_line['invoice_line_tax_id'])] or []
                inv_line_ref.create(cr, uid, inv_line, context)

        for i in inv_ids:
            self.wf_service.trg_validate(uid, 'account.invoice', i, 'invoice_open', cr)
        return inv_ids

    def create_account_move(self, cr, uid, ids, context=None):
        account_move_obj = self.pool.get('account.move')
        account_move_line_obj = self.pool.get('account.move.line')
        account_period_obj = self.pool.get('account.period')
        account_tax_obj = self.pool.get('account.tax')
        period = account_period_obj.find(cr, uid, context=context)[0]

        for order in self.browse(cr, uid, ids, context=context):

            to_reconcile = []
            group_tax = {}

            if order.amount_total > 0:
                order_account = order.sale_journal.default_credit_account_id.id
            else:
                order_account = order.sale_journal.default_debit_account_id.id

            # Create an entry for the sale
            move_id = account_move_obj.create(cr, uid, {
                'journal_id': order.sale_journal.id,
                'period_id': period,
                }, context=context)

            # Create an move for each order line
            for line in order.lines:

                tax_amount = 0
                taxes = [t for t in line.product_id.taxes_id]
                computed_taxes = account_tax_obj.compute_inv(
                    cr, uid, taxes, line.product_id.list_price, line.qty)

                for tax in computed_taxes:
                    tax_amount += round(tax['amount'], 2)
                    group_key = (tax['tax_code_id'],
                                tax['base_code_id'],
                                tax['account_collected_id'])

                    if group_key in group_tax:
                        group_tax[group_key] += round(tax['amount'], 2)
                    else:
                        group_tax[group_key] = round(tax['amount'], 2)

                amount = line.price_subtotal - tax_amount

                # Search for the income account
                if  line.product_id.property_account_income.id:
                    income_account = line.\
                                    product_id.property_account_income.id
                elif line.product_id.categ_id.\
                        property_account_income_categ.id:
                    income_account = line.product_id.categ_id.\
                                    property_account_income_categ.id
                else:
                    raise osv.except_osv('Error !', 'There is no income '\
                        'account defined for this product: "%s" (id:%d)'\
                        % (line.product_id.name, line.product_id.id, ))


                # Empty the tax list as long as there is no tax code:
                tax_code_id = False
                tax_amount = 0
                while computed_taxes:
                    tax = computed_taxes.pop(0)
                    if amount > 0:
                        tax_code_id = tax['base_code_id']
                        tax_amount = line.price_subtotal * tax['base_sign']
                    else:
                        tax_code_id = tax['ref_base_code_id']
                        tax_amount = line.price_subtotal * tax['ref_base_sign']
                    # If there is one we stop
                    if tax_code_id:
                        break

                # Create a move for the line
                account_move_line_obj.create(cr, uid, {
                    'name': order.name,
                    'date': order.date_order,
                    'ref': order.name,
                    'move_id': move_id,
                    'account_id': income_account,
                    'credit': ((amount>0) and amount) or 0.0,
                    'debit': ((amount<0) and -amount) or 0.0,
                    'journal_id': order.sale_journal.id,
                    'period_id': period,
                    'tax_code_id': tax_code_id,
                    'tax_amount': tax_amount,
                }, context=context)

                # For each remaining tax with a code, whe create a move line
                for tax in computed_taxes:
                    if amount > 0:
                        tax_code_id = tax['base_code_id']
                        tax_amount = line.price_subtotal * tax['base_sign']
                    else:
                        tax_code_id = tax['ref_base_code_id']
                        tax_amount = line.price_subtotal * tax['ref_base_sign']
                    if not tax_code_id:
                        continue

                    account_move_line_obj.create(cr, uid, {
                        'name': order.name,
                        'date': order.date_order,
                        'ref': order.name,
                        'move_id': move_id,
                        'account_id': income_account,
                        'credit': 0.0,
                        'debit': 0.0,
                        'journal_id': order.sale_journal.id,
                        'period_id': period,
                        'tax_code_id': tax_code_id,
                        'tax_amount': tax_amount,
                    }, context=context)


            # Create a move for each tax group
            (tax_code_pos, base_code_pos, account_pos)= (0, 1, 2)
            for key, amount in group_tax.items():
                account_move_line_obj.create(cr, uid, {
                    'name': order.name,
                    'date': order.date_order,
                    'ref': order.name,
                    'move_id': move_id,
                    'account_id': key[account_pos],
                    'credit': ((amount>0) and amount) or 0.0,
                    'debit': ((amount<0) and -amount) or 0.0,
                    'journal_id': order.sale_journal.id,
                    'period_id': period,
                    'tax_code_id': key[tax_code_pos],
                    'tax_amount': amount,
                }, context=context)

            # counterpart
            to_reconcile.append(account_move_line_obj.create(cr, uid, {
                'name': order.name,
                'date': order.date_order,
                'ref': order.name,
                'move_id': move_id,
                'account_id': order_account,
                'credit': ((order.amount_total<0) and -order.amount_total)\
                    or 0.0,
                'debit': ((order.amount_total>0) and order.amount_total)\
                    or 0.0,
                'journal_id': order.sale_journal.id,
                'period_id': period,
            }, context=context))


            # search the account receivable for the payments:
            account_receivable = order.sale_journal.default_credit_account_id.id
            if not account_receivable:
                raise  osv.except_osv('Error !',
                    'There is no receivable account defined for this journal:'\
                    ' "%s" (id:%d)' % (order.sale_journal.name, order.sale_journal.id, ))

            for payment in order.payments:

                if payment.amount > 0:
                    payment_account = \
                        payment.journal_id.default_debit_account_id.id
                else:
                    payment_account = \
                        payment.journal_id.default_credit_account_id.id

                if payment.amount > 0:
                    order_account = \
                        order.sale_journal.default_credit_account_id.id
                else:
                    order_account = \
                        order.sale_journal.default_debit_account_id.id

                # Create one entry for the payment
                payment_move_id = account_move_obj.create(cr, uid, {
                    'journal_id': order.sale_journal.id,
                    'period_id': period,
                }, context=context)
                account_move_line_obj.create(cr, uid, {
                    'name': order.name,
                    'date': order.date_order,
                    'ref': order.name,
                    'move_id': payment_move_id,
                    'account_id': payment_account,
                    'credit': ((payment.amount<0) and -payment.amount) or 0.0,
                    'debit': ((payment.amount>0) and payment.amount) or 0.0,
                    'journal_id': order.sale_journal.id,
                    'period_id': period,
                }, context=context)
                to_reconcile.append(account_move_line_obj.create(cr, uid, {
                    'name': order.name,
                    'date': order.date_order,
                    'ref': order.name,
                    'move_id': payment_move_id,
                    'account_id': order_account,
                    'credit': ((payment.amount>0) and payment.amount) or 0.0,
                    'debit': ((payment.amount<0) and -payment.amount) or 0.0,
                    'journal_id': order.sale_journal.id,
                    'period_id': period,
                }, context=context))

            account_move_obj.button_validate(cr, uid, [move_id, payment_move_id], context=context)
            account_move_line_obj.reconcile(cr, uid, to_reconcile, type='manual', context=context)
        return True

    def action_paid(self, cr, uid, ids, context=None):
        self.create_picking(cr, uid, ids, context={})
        self.write(cr, uid, ids, {'state': 'paid'})
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        self.cancel_order(cr, uid, ids, context={})
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True

    def action_done(self, cr, uid, ids, context=None):
        self.create_account_move(cr, uid, ids, context={})
        self.write(cr, uid, ids, {'state': 'done'})
        return True

pos_order()


class pos_order_line(osv.osv):
    _name = "pos.order.line"
    _description = "Lines of Point of Sale"

    def _amount_line(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for line in self.browse(cr, uid, ids):
            res[line.id] = line.price_unit * line.qty * (1 - (line.discount or 0.0) / 100.0)
        return res

    def price_by_product(self, cr, uid, ids, pricelist, product_id, qty=0, partner_id=False):
        if not product_id:
            return 0.0
        if not pricelist:
            raise osv.except_osv('No Pricelist !',
                'You have to select a pricelist in the sale form !\n'
                'Please set one before choosing a product.')

        price = self.pool.get('product.pricelist').price_get(cr, uid,
            [pricelist], product_id, qty or 1.0, partner_id)[pricelist]
        if price is False:
            raise osv.except_osv('No valid pricelist line found !',
                "Couldn't find a pricelist line matching this product"
                " and quantity.\nYou have to change either the product,"
                " the quantity or the pricelist.")
        return price

    def onchange_product_id(self, cr, uid, ids, pricelist, product_id, qty=0, partner_id=False):
        price = self.price_by_product(cr, uid, ids, pricelist, product_id, qty, partner_id)

        return {'value': {'price_unit': price}}

    _columns = {
        'name': fields.char('Line Description', size=512),
        'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], required=True, change_default=True),
        'price_unit': fields.float('Unit Price', required=True),
        'qty': fields.float('Quantity'),
        'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal'),
        'discount': fields.float('Discount (%)', digits=(16, 2)),
        'order_id': fields.many2one('pos.order', 'Order Ref', ondelete='cascade'),
        'create_date': fields.datetime('Creation date', readonly=True),
        }

    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'pos.order.line'),
        'qty': lambda *a: 1,
        'discount': lambda *a: 0.0,
        }

    def create(self, cr, user, vals, context={}):
        if vals.get('product_id'):
            return super(pos_order_line, self).create(cr, user, vals, context)
        return False

    def write(self, cr, user, ids, values, context={}):
        if 'product_id' in values and not values['product_id']:
            return False
        return super(pos_order_line, self).write(cr, user, ids, values, context)

pos_order_line()


class pos_payment(osv.osv):
    _name = 'pos.payment'
    _description = 'Pos Payment'

    def _journal_get(self, cr, uid, context={}):
        obj = self.pool.get('account.journal')
        ids = obj.search(cr, uid, [('type', '=', 'cash')])
        res = obj.read(cr, uid, ids, ['id', 'name'], context)
        res = [(r['id'], r['name']) for r in res]
        return res

    def _journal_default(self, cr, uid, context={}):
        journal_list = self.pool.get('account.journal').search(cr, uid, [('type', '=', 'cash')])
        if journal_list:
            return journal_list[0]
        else:
            return False

    _columns = {
        'name': fields.char('Description', size=64),
        'order_id': fields.many2one('pos.order', 'Order Ref', required=True),
        'journal_id': fields.many2one('account.journal', "Journal", required=True),
        'amount': fields.float('Amount', required=True),
    }
    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'pos.payment'),
        'journal_id': _journal_default,
    }

    def create(self, cr, user, vals, context={}):
        if vals.get('journal_id') and vals.get('amount'):
            return super(pos_payment, self).create(cr, user, vals, context)
        return False

    def write(self, cr, user, ids, values, context={}):
        if 'amount' in values and not values['amount']:
            return False
        if 'journal_id' in values and not values['journal_id']:
            return False
        return super(pos_payment, self).write(cr, user, ids, values, context)

pos_payment()


class report_transaction_pos(osv.osv):
    _name = "report.transaction.pos"
    _description = "transaction for the pos"
    _auto = False
    _columns = {
        'date_create': fields.date('Date', readonly=True),
        'journal_id': fields.many2one('account.journal', 'Journal', readonly=True),
        'user_id': fields.many2one('res.users', 'User', readonly=True),
        'no_trans': fields.float('Number of transaction', readonly=True),
        'amount': fields.float('Amount', readonly=True),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', readonly=True),
    }

    def init(self, cr):
        cr.execute("""
            create or replace view report_transaction_pos as (
                select
                    min(pp.id) as id,
                    count(pp.id) as no_trans,
                    sum(amount) as amount,
                    pp.journal_id,
                    date_trunc('day',pp.create_date)::date as date_create,
                    ps.user_id,
                    ps.invoice_id
                from
                    pos_payment pp, pos_order ps
                WHERE ps.id = pp.order_id
                group by
                    pp.journal_id, date_trunc('day',pp.create_date), ps.user_id, ps.invoice_id
            )
            """)
report_transaction_pos()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

