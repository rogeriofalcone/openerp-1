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
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from dateutil.relativedelta import relativedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _
import pytz
from openerp import SUPERUSER_ID

class sale_order(osv.osv):
    _inherit = "sale.order"
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'shipped': False,
        })
        return super(sale_order, self).copy(cr, uid, id, default, context=context)

    #Might have been deleted before for a reason     
    def shipping_policy_change(self, cr, uid, ids, policy, context=None):
        if not policy:
            return {}
        inv_qty = 'order'
        if policy == 'prepaid':
            inv_qty = 'order'
        elif policy == 'picking':
            inv_qty = 'procurement'
        return {'value': {'invoice_quantity': inv_qty}}


    def _get_default_warehouse(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        warehouse_ids = self.pool.get('stock.warehouse').search(cr, uid, [('company_id', '=', company_id)], context=context)
        if not warehouse_ids:
            raise osv.except_osv(_('Error!'), _('There is no warehouse defined for current company.'))
        return warehouse_ids[0]

    def _get_picking_ids(self, cr, uid, ids, name, args, context=None):
        res = {}
        if not ids: return res
        for id in ids:
            res.setdefault(id, [])
        '''SQL request that does exactly the same as the code below'''
        cr.execute('''SELECT sol.order_id, sm.picking_id from sale_order_line as sol \
                   LEFT JOIN procurement_order as po on (po.id = sol.procurement_id) \
                   LEFT JOIN stock_move as sm on (sm.id = po.move_id) \
                   LEFT JOIN stock_picking as sp on (sp.id = sm.picking_id) \
                   WHERE sol.order_id in %s and sp.type = 'out'\
                   GROUP BY sol.order_id, sm.picking_id ORDER BY sol.order_id''',(tuple(ids),))
        result = cr.fetchall()
        for r in result:
           res[r[0]].append(r[1])
        return res

        '''for element in self.browse(cr, uid, ids, context=context):
            procu_ids = []
            for line in element.order_line:
                if line.procurement_id:
                    procu_ids.append(line.procurement_id.id)
            picking_ids = []
            for procurement in self.pool.get('procurement.order').browse(cr, uid, list(set(procu_ids)), context=context):
                if procurement.move_id and procurement.move_id.picking_id and procurement.move_id.picking_id.type == 'out':
                    picking_ids.append(procurement.move_id.picking_id.id)
            res[element.id] = list(set(picking_ids))
        return res'''

    _columns = {
          'state': fields.selection([
            ('draft', 'Draft Quotation'),
            ('sent', 'Quotation Sent'),
            ('cancel', 'Cancelled'),
            ('waiting_date', 'Waiting Schedule'),
            ('progress', 'Sales Order'),
            ('manual', 'Sale to Invoice'),
            ('shipping_except', 'Shipping Exception'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ], 'Status', readonly=True, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
        'incoterm': fields.many2one('stock.incoterms', 'Incoterm', help="International Commercial Terms are a series of predefined commercial terms used in international transactions."),
        'picking_policy': fields.selection([('direct', 'Deliver each product when available'), ('one', 'Deliver all products at once')],
            'Shipping Policy', required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
            help="""Pick 'Deliver each product when available' if you allow partial delivery."""),
        'order_policy': fields.selection([
                ('manual', 'On Demand'),
                ('picking', 'On Delivery Order'),
                ('prepaid', 'Before Delivery'),
            ], 'Create Invoice', required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
            help="""On demand: A draft invoice can be created from the sales order when needed. \nOn delivery order: A draft invoice can be created from the delivery order when the products have been delivered. \nBefore delivery: A draft invoice is created from the sales order and must be paid before the products can be delivered."""),
        'shipped': fields.boolean('Delivered', readonly=True, help="It indicates that the sales order has been delivered. This field is updated only after the scheduler(s) have been launched."),
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse', required=True),
        'picking_ids': fields.function(_get_picking_ids, method=True, type='one2many', relation='stock.picking', string='Picking associated to this sale'),
    }
    _defaults = {
        'warehouse_id': _get_default_warehouse,
        'picking_policy': 'direct',
        'order_policy': 'manual',
    }
    def onchange_warehouse_id(self, cr, uid, ids, warehouse_id, context=None):
        val = {}
        if warehouse_id:
            warehouse = self.pool.get('stock.warehouse').browse(cr, uid, warehouse_id, context=context)
            if warehouse.company_id:
                val['company_id'] = warehouse.company_id.id
        return {'value': val}

    # FP Note: to change, take the picking related to the moves related to the
    # procurements related to SO lines

    def action_view_delivery(self, cr, uid, ids, context=None):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(cr, uid, 'stock', 'action_picking_tree')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]

        #compute the number of delivery orders to display
        pick_ids = []
        for so in self.browse(cr, uid, ids, context=context):
            pick_ids += [picking.id for picking in so.picking_ids]

        #choose the view_mode accordingly
        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',["+','.join(map(str, pick_ids))+"])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'stock', 'view_picking_out_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = pick_ids and pick_ids[0] or False
        return result

    def action_invoice_create(self, cr, uid, ids, grouped=False, states=['confirmed', 'done', 'exception'], date_invoice = False, context=None):
        picking_obj = self.pool.get('stock.picking')
        res = super(sale_order,self).action_invoice_create( cr, uid, ids, grouped=grouped, states=states, date_invoice = date_invoice, context=context)
        for order in self.browse(cr, uid, ids, context=context):
            if order.order_policy == 'picking':
                picking_obj.write(cr, uid, map(lambda x: x.id, order.picking_ids), {'invoice_state': 'invoiced'})
        return res

    def action_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        sale_order_line_obj = self.pool.get('sale.order.line')
        proc_obj = self.pool.get('procurement.order')
        stock_obj = self.pool.get('stock.picking')
        for sale in self.browse(cr, uid, ids, context=context):
            for pick in sale.picking_ids:
                if pick.state not in ('draft', 'cancel'):
                    raise osv.except_osv(
                        _('Cannot cancel sales order!'),
                        _('You must first cancel all delivery order(s) attached to this sales order.'))
                if pick.state == 'cancel':
                    for mov in pick.move_lines:
                        proc_ids = proc_obj.search(cr, uid, [('move_id', '=', mov.id)])
                        if proc_ids:
                            proc_obj.signal_button_check(cr, uid, proc_ids)
            for r in self.read(cr, uid, ids, ['picking_ids']):
                stock_obj.signal_button_cancel(cr, uid, r['picking_ids'])
        return super(sale_order, self).action_cancel(cr, uid, ids, context=context)

    def action_wait(self, cr, uid, ids, context=None):
        res = super(sale_order, self).action_wait(cr, uid, ids, context=context)
        for o in self.browse(cr, uid, ids):
            noprod = self.test_no_product(cr, uid, o, context)
            if noprod and o.order_policy=='picking':
                self.write(cr, uid, [o.id], {'order_policy': 'manual'}, context=context)
        return res


    def date_to_datetime(self, cr, uid, userdate, context=None):
        """ Convert date values expressed in user's timezone to
        server-side UTC timestamp, assuming a default arbitrary
        time of 12:00 AM - because a time is needed.
    
        :param str userdate: date string in in user time zone
        :return: UTC datetime string for server-side use
        """
        # TODO: move to fields.datetime in server after 7.0
        user_date = datetime.strptime(userdate, DEFAULT_SERVER_DATE_FORMAT)
        if context and context.get('tz'):
            tz_name = context['tz']
        else:
            tz_name = self.pool.get('res.users').read(cr, SUPERUSER_ID, uid, ['tz'])['tz']
        if tz_name:
            utc = pytz.timezone('UTC')
            context_tz = pytz.timezone(tz_name)
            user_datetime = user_date + relativedelta(hours=12.0)
            local_timestamp = context_tz.localize(user_datetime, is_dst=False)
            user_datetime = local_timestamp.astimezone(utc)
            return user_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return user_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    # if mode == 'finished':
    #   returns True if all lines are done, False otherwise
    # if mode == 'canceled':
    #   returns True if there is at least one canceled line, False otherwise
    def test_state(self, cr, uid, ids, mode, *args):
        assert mode in ('finished', 'canceled'), _("invalid mode for test_state")
        finished = True
        canceled = False
        write_done_ids = []
        write_cancel_ids = []
        for order in self.browse(cr, uid, ids, context={}):
            for line in order.order_line:
                if (not line.procurement_id) or (line.procurement_id.state=='done'):
                    if line.state != 'done':
                        write_done_ids.append(line.id)
                else:
                    finished = False
                if line.procurement_id:
                    if (line.procurement_id.state == 'cancel'):
                        canceled = True
                        if line.state != 'exception':
                            write_cancel_ids.append(line.id)
        if write_done_ids:
            self.pool.get('sale.order.line').write(cr, uid, write_done_ids, {'state': 'done'})
        if write_cancel_ids:
            self.pool.get('sale.order.line').write(cr, uid, write_cancel_ids, {'state': 'exception'})

        if mode == 'finished':
            return finished
        elif mode == 'canceled':
            return canceled


    def action_ship_end(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context=context):
            val = {'shipped': True}
            if order.state == 'shipping_except':
                val['state'] = 'progress'
                if (order.order_policy == 'manual'):
                    for line in order.order_line:
                        if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
                            val['state'] = 'manual'
                            break
            for line in order.order_line:
                towrite = []
                if line.state == 'exception':
                    towrite.append(line.id)
                if towrite:
                    self.pool.get('sale.order.line').write(cr, uid, towrite, {'state': 'done'}, context=context)
            res = self.write(cr, uid, [order.id], val)
        return True

    def has_stockable_products(self, cr, uid, ids, *args):
        for order in self.browse(cr, uid, ids):
            for order_line in order.order_line:
                if order_line.product_id and order_line.product_id.type in ('product', 'consu'):
                    return True
        return False
    
    def procurement_lines_get(self, cr, uid, ids, *args):
        res = []
        for order in self.browse(cr, uid, ids, context={}):
            for line in order.order_line:
                if line.procurement_id:
                    res.append(line.procurement_id.id)
        return res

class stock_move(osv.osv):
    _inherit = 'stock.move'
    _columns = {
        'sale_line_id': fields.many2one('sale.order.line', 'Sale Line'),
    }


class sale_order_line(osv.osv):



    _inherit = 'sale.order.line'
    _columns = { 
        'move_ids': fields.one2many('stock.move', 'sale_line_id', 'Inventory Moves', readonly=True),
    }

    def button_cancel(self, cr, uid, ids, context=None):
        res = super(sale_order_line, self).button_cancel(cr, uid, ids, context=context)
        for line in self.browse(cr, uid, ids, context=context):
            for move_line in line.move_ids:
                if move_line.state != 'cancel':
                    raise osv.except_osv(
                            _('Cannot cancel sales order line!'),
                            _('You must first cancel stock moves attached to this sales order line.'))   
        return res

    def copy_data(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({'move_ids': []})
        return super(sale_order_line, self).copy_data(cr, uid, id, default, context=context)


class sale_advance_payment_inv(osv.osv_memory):
    _inherit = "sale.advance.payment.inv"

    def _create_invoices(self, cr, uid, inv_values, sale_id, context=None):
        result = super(sale_advance_payment_inv, self)._create_invoices(cr, uid, inv_values, sale_id, context=context)
        sale_obj = self.pool.get('sale.order')
        sale_line_obj = self.pool.get('sale.order.line')
        wizard = self.browse(cr, uid, [result], context)
        sale = sale_obj.browse(cr, uid, sale_id, context=context)

        # If invoice on picking: add the cost on the SO
        # If not, the advance will be deduced when generating the final invoice
        line_name = inv_values.get('invoice_line') and inv_values.get('invoice_line')[0][2].get('name') or ''
        line_tax = inv_values.get('invoice_line') and inv_values.get('invoice_line')[0][2].get('invoice_line_tax_id') or False
        if sale.order_policy == 'picking':
            vals = {
                'order_id': sale.id,
                'name': line_name,
                'price_unit': -inv_amount,
                'product_uom_qty': wizard.qtty or 1.0,
                'product_uos_qty': wizard.qtty or 1.0,
                'product_uos': res.get('uos_id', False),
                'product_uom': res.get('uom_id', False),
                'product_id': wizard.product_id.id or False,
                'discount': False,
                'tax_id': line_tax,
            }
            sale_line_obj.create(cr, uid, vals, context=context)
        return result
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
