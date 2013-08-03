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
            'picking_ids': []
        })
        return super(sale_order, self).copy(cr, uid, id, default, context=context)

    def _get_default_warehouse(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        warehouse_ids = self.pool.get('stock.warehouse').search(cr, uid, [('company_id', '=', company_id)], context=context)
        if not warehouse_ids:
            raise osv.except_osv(_('Error!'), _('There is no warehouse defined for selected company.'))
        return warehouse_ids[0]

    def _get_shipped(self, cr, uid, ids, name, args, context=None):
        res = {}
        for sale in self.browse(cr, uid, ids, context=context):
            group = sale.procurement_group_id
            if group:
                res[sale.id] = all([proc.state in ['cancel', 'done'] for proc in group.procurement_ids])
            else:
                res[sale.id] = False
        return res

    def _get_orders(self, cr, uid, ids, context=None):
        res = set()
        proc_obj = self.pool.get("procurement.order")
        procs = proc_obj.search(cr, uid, [('move_id', 'in', ids)], context=context)
        for proc in proc_obj.browse(cr, uid, procs, context=context):
            if proc.group_id and proc.group_id.sale_id:
                res.add(proc.group_id.sale_id.id)
        return list(res)

    def _get_picking_ids(self, cr, uid, ids, name, args, context=None):
        res = {}
        for sale in self.browse(cr, uid, ids, context=context):
            if not sale.procurement_group_id:
                res[sale.id] = []
                continue
            for procurement in sale.procurement_group_id.procurement_ids:
                if procurement.move_id and procurement.move_id.picking_id:
                    picking_ids.append(procurement.move_id.picking_id.id)
            res[sale.id] = list(set(picking_ids))
        return res

    def _prepare_order_line_procurement(self, cr, uid, order, line, group_id = False, context=None):
        vals = super(sale_order, self)._prepare_order_line_procurement(cr, uid, order, line, group_id=group_id, context=context)
        location_id = order.partner_shipping_id.property_stock_customer.id
        vals['location_id'] = location_id
        return vals

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
        'shipped': fields.function(_get_shipped, string='Delivered', type='boolean', store={'stock.move': (_get_orders, ['state'], 10)}),
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
            res = mod_obj.get_object_reference(cr, uid, 'stock', 'view_picking_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = pick_ids and pick_ids[0] or False
        return result

    # TODO: FP Note: I guess it's better to do:
    # if order_policy<>picking: super()
    # else: call invoice_on_picking_method()
    def action_invoice_create(self, cr, uid, ids, grouped=False, states=['confirmed', 'done', 'exception'], date_invoice = False, context=None):
        picking_obj = self.pool.get('stock.picking')
        res = super(sale_order,self).action_invoice_create(cr, uid, ids, grouped=grouped, states=states, date_invoice = date_invoice, context=context)
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
                 # FP Note: not sure we need this
                 #if pick.state == 'cancel':
                 #    for mov in pick.move_lines:
                 #        proc_ids = proc_obj.search(cr, uid, [('move_id', '=', mov.id)])
                 #        if proc_ids:
                 #            proc_obj.signal_button_check(cr, uid, proc_ids)
            stock_obj.signal_button_cancel(cr, uid, [p.id for p in sale.picking_ids])
        return super(sale_order, self).action_cancel(cr, uid, ids, context=context)

    def action_wait(self, cr, uid, ids, context=None):
        res = super(sale_order, self).action_wait(cr, uid, ids, context=context)
        for o in self.browse(cr, uid, ids):
            noprod = self.test_no_product(cr, uid, o, context)
            if noprod and o.order_policy=='picking':
                self.write(cr, uid, [o.id], {'order_policy': 'manual'}, context=context)
        return res

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

    def _number_packages(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            try:
                res[line.id] = int((line.product_uom_qty+line.product_packaging.qty-0.0001) / line.product_packaging.qty)
            except:
                res[line.id] = 1
        return res

    _columns = {
        'move_ids': fields.one2many('stock.move', 'sale_line_id', 'Inventory Moves', readonly=True),
        'product_packaging': fields.many2one('product.packaging', 'Packaging'),
        'number_packages': fields.function(_number_packages, type='integer', string='Number Packages'),
    }

    _defaults = {
        'product_packaging': False,
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

    def product_packaging_change(self, cr, uid, ids, pricelist, product, qty=0, uom=False,
                                   partner_id=False, packaging=False, flag=False, context=None):
        if not product:
            return {'value': {'product_packaging': False}}
        product_obj = self.pool.get('product.product')
        product_uom_obj = self.pool.get('product.uom')
        pack_obj = self.pool.get('product.packaging')
        warning = {}
        result = {}
        warning_msgs = ''
        if flag:
            res = self.product_id_change(cr, uid, ids, pricelist=pricelist,
                    product=product, qty=qty, uom=uom, partner_id=partner_id,
                    packaging=packaging, flag=False, context=context)
            warning_msgs = res.get('warning') and res['warning']['message']

        products = product_obj.browse(cr, uid, product, context=context)
        if not products.packaging:
            packaging = result['product_packaging'] = False
        elif not packaging and products.packaging and not flag:
            packaging = products.packaging[0].id
            result['product_packaging'] = packaging

        if packaging:
            default_uom = products.uom_id and products.uom_id.id
            pack = pack_obj.browse(cr, uid, packaging, context=context)
            q = product_uom_obj._compute_qty(cr, uid, uom, pack.qty, default_uom)
#            qty = qty - qty % q + q
            if qty and (q and not (qty % q) == 0):
                ean = pack.ean or _('(n/a)')
                qty_pack = pack.qty
                type_ul = pack.ul
                if not warning_msgs:
                    warn_msg = _("You selected a quantity of %d Units.\n"
                                "But it's not compatible with the selected packaging.\n"
                                "Here is a proposition of quantities according to the packaging:\n"
                                "EAN: %s Quantity: %s Type of ul: %s") % \
                                    (qty, ean, qty_pack, type_ul.name)
                    warning_msgs += _("Picking Information ! : ") + warn_msg + "\n\n"
                warning = {
                       'title': _('Configuration Error!'),
                       'message': warning_msgs
                }
            result['product_uom_qty'] = qty

        return {'value': result, 'warning': warning}


    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        context = context or {}
        product_uom_obj = self.pool.get('product.uom')
        partner_obj = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')
        warning = {}
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty=qty,
            uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)

        if not product:
            res['value'].update({'product_packaging': False})
            return res

        #update of result obtained in super function
        product_obj = product_obj.browse(cr, uid, product, context=context)
        res['value']['delay'] = (product_obj.sale_delay or 0.0)
        #res['value']['type'] = product_obj.procure_method

        #check if product is available, and if not: raise an error
        uom2 = False
        if uom:
            uom2 = product_uom_obj.browse(cr, uid, uom)
            if product_obj.uom_id.category_id.id != uom2.category_id.id:
                uom = False
        if not uom2:
            uom2 = product_obj.uom_id

        # Calling product_packaging_change function after updating UoM
        res_packing = self.product_packaging_change(cr, uid, ids, pricelist, product, qty, uom, partner_id, packaging, context=context)
        res['value'].update(res_packing.get('value', {}))
        warning_msgs = res_packing.get('warning') and res_packing['warning']['message'] or ''
        compare_qty = float_compare(product_obj.virtual_available * uom2.factor, qty * product_obj.uom_id.factor, precision_rounding=product_obj.uom_id.rounding)
        if (product_obj.type=='product') and int(compare_qty) == -1:
          #and (product_obj.procure_method=='make_to_stock'): --> need to find alternative for procure_method
            warn_msg = _('You plan to sell %.2f %s but you only have %.2f %s available !\nThe real stock is %.2f %s. (without reservations)') % \
                    (qty, uom2 and uom2.name or product_obj.uom_id.name,
                     max(0,product_obj.virtual_available), product_obj.uom_id.name,
                     max(0,product_obj.qty_available), product_obj.uom_id.name)
            warning_msgs += _("Not enough stock ! : ") + warn_msg + "\n\n"

        #update of warning messages
        if warning_msgs:
            warning = {
                       'title': _('Configuration Error!'),
                       'message' : warning_msgs
                    }
        res.update({'warning': warning})
        return res

