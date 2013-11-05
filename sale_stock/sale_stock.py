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
from openerp.tools.safe_eval import safe_eval as eval
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
        for move in self.browse(cr, uid, ids, context=context):
            if move.procurement_id and move.procurement_id.sale_line_id:
                res.add(move.procurement_id.sale_line_id.order_id.id)
        return list(res)
    
    def _get_orders_procurements(self, cr, uid, ids, context=None):
        res = set()
        for proc in self.pool.get('procurement.order').browse(cr, uid, ids, context=context):
            if proc.sale_line_id:
                res.add(proc.sale_line_id.order_id.id)
        return list(res)
    
    def _get_picking_ids(self, cr, uid, ids, name, args, context=None):
        res = {}
        for sale in self.browse(cr, uid, ids, context=context):
            if not sale.procurement_group_id:
                res[sale.id] = []
                continue
            picking_ids = set()
            for procurement in sale.procurement_group_id.procurement_ids:
                for move in procurement.move_ids:
                    if move.picking_id:
                        picking_ids.add(move.picking_id.id)
            res[sale.id] = list(picking_ids)
        return res

    def _prepare_order_line_procurement(self, cr, uid, order, line, group_id=False, context=None):
        vals = super(sale_order, self)._prepare_order_line_procurement(cr, uid, order, line, group_id=group_id, context=context)
        location_id = order.partner_shipping_id.property_stock_customer.id
        vals['location_id'] = location_id

        routes = line.route_id and [(4, line.route_id.id)] or []
        vals['route_ids'] = routes
        vals['warehouse_id'] = order.warehouse_id and order.warehouse_id.id or False
        return vals

    _columns = {
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
        'shipped': fields.function(_get_shipped, string='Delivered', type='boolean', store={
                'stock.move': (_get_orders, ['state'], 10),
                'procurement.order': (_get_orders_procurements, ['state'], 10)
            }),
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

        result = mod_obj.get_object_reference(cr, uid, 'stock', 'action_picking_tree_all')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]

        #compute the number of delivery orders to display
        pick_ids = []
        for so in self.browse(cr, uid, ids, context=context):
            pick_ids += [picking.id for picking in so.picking_ids]
            
        #choose the view_mode accordingly
        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, pick_ids)) + "])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'stock', 'view_picking_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = pick_ids and pick_ids[0] or False
        return result


    # TODO: FP Note: I guess it's better to do:
    # if order_policy<>picking: super()
    # else: call invoice_on_picking_method()
    def action_invoice_create(self, cr, uid, ids, grouped=False, states=['confirmed', 'done', 'exception'], date_invoice = False, context=None):
        move_obj = self.pool.get("stock.move")
        res = super(sale_order,self).action_invoice_create(cr, uid, ids, grouped=grouped, states=states, date_invoice = date_invoice, context=context)
        for order in self.browse(cr, uid, ids, context=context):
            if order.order_policy == 'picking':
                for picking in order.picking_ids:
                    move_obj.write(cr, uid, [x.id for x in picking.move_lines], {'invoice_state': 'invoiced'}, context=context)
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

    def _get_date_planned(self, cr, uid, order, line, start_date, context=None):
        date_planned = super(sale_order, self)._get_date_planned(cr, uid, order, line, start_date, context=context)
        date_planned = (date_planned - timedelta(days=order.company_id.security_lead)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return date_planned

    def _prepare_procurement_group(self, cr, uid, order, context=None):
        res = super(sale_order, self)._prepare_procurement_group(cr, uid, order, context=None)
        res.update({'move_type': order.picking_policy})
        return res

    def action_ship_end(self, cr, uid, ids, context=None):
        super(sale_order, self).action_ship_end(cr, uid, ids, context=context)
        for order in self.browse(cr, uid, ids, context=context):
            val = {'shipped': True}
            if order.state == 'shipping_except':
                val['state'] = 'progress'
                if (order.order_policy == 'manual'):
                    for line in order.order_line:
                        if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
                            val['state'] = 'manual'
                            break
            res = self.write(cr, uid, [order.id], val)
        return True




    def has_stockable_products(self, cr, uid, ids, *args):
        for order in self.browse(cr, uid, ids):
            for order_line in order.order_line:
                if order_line.product_id and order_line.product_id.type in ('product', 'consu'):
                    return True
        return False


class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    def need_procurement(self, cr, uid, ids, context=None):
        #when sale is installed alone, there is no need to create procurements, but with sale_stock
        #we must create a procurement for each product that is not a service.
        for line in self.browse(cr, uid, ids, context=context):
            if line.product_id and line.product_id.type != 'service':
                return True
        return super(sale_order_line, self).need_procurement(cr, uid, ids, context=context)

    def _number_packages(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            try:
                res[line.id] = int((line.product_uom_qty+line.product_packaging.qty-0.0001) / line.product_packaging.qty)
            except:
                res[line.id] = 1
        return res

    _columns = {
        'product_packaging': fields.many2one('product.packaging', 'Packaging'),
        'number_packages': fields.function(_number_packages, type='integer', string='Number Packages'),
        'route_id': fields.many2one('stock.location.route', 'Route', domain=[('sale_selectable', '=', True)]),
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


    def product_id_change_with_wh(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, warehouse_id=False, context=None):
        context = context or {}
        product_uom_obj = self.pool.get('product.uom')
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

        # Calling product_packaging_change function after updating UoM
        res_packing = self.product_packaging_change(cr, uid, ids, pricelist, product, qty, uom, partner_id, packaging, context=context)
        res['value'].update(res_packing.get('value', {}))
        warning_msgs = res_packing.get('warning') and res_packing['warning']['message'] or ''

        #determine if the product is MTO or not (for a further check)
        isMto = False
        if warehouse_id:
            warehouse = self.pool.get('stock.warehouse').browse(cr, uid, warehouse_id, context=context)
            for product_route in product_obj.route_ids:
                if warehouse.mto_pull_id and warehouse.mto_pull_id.route_id and warehouse.mto_pull_id.route_id.id == product_route.id:
                    isMto = True
                    break
        else:
            try:
                mto_route_id = self.pool.get('ir.model.data').get_object(cr, uid, 'stock', 'route_warehouse0_mto').id
            except:
                # if route MTO not found in ir_model_data, we treat the product as in MTS
                mto_route_id = False
            if mto_route_id:
                for product_route in product_obj.route_ids:
                    if product_route.id == mto_route_id:
                        isMto = True
                        break

        #check if product is available, and if not: raise a warning, but do this only for products that aren't processed in MTO
        if not isMto:
            uom2 = False
            if uom:
                uom2 = product_uom_obj.browse(cr, uid, uom)
                if product_obj.uom_id.category_id.id != uom2.category_id.id:
                    uom = False
            if not uom2:
                uom2 = product_obj.uom_id
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

class stock_move(osv.osv):
    _inherit = 'stock.move'

    def action_cancel(self, cr, uid, ids, context=None):
        sale_ids = []
        for move in self.browse(cr, uid, ids, context=context):
            if move.procurement_id and move.procurement_id.sale_line_id:
                sale_ids.append(move.procurement_id.sale_line_id.order_id.id)
        if sale_ids:
            self.pool.get('sale.order').signal_ship_except(cr, uid, sale_ids)
        return super(stock_move, self).action_cancel(cr, uid, ids, context=context)

    def _create_invoice_line_from_vals(self, cr, uid, move, invoice_line_vals, context=None):
        invoice_line_id = self.pool.get('account.invoice.line').create(cr, uid, invoice_line_vals, context=context)
        if move.procurement_id and move.procurement_id.sale_line_id:
            sale_line = move.procurement_id.sale_line_id
            self.pool.get('sale.order.line').write(cr, uid, [sale_line.id], {
                'invoice_lines': [(4, invoice_line_id)]
            }, context=context)
            self.pool.get('sale.order').write(cr, uid, [sale_line.order_id.id], {
                'invoice_ids': [(4, invoice_line_vals['invoice_id'])],
            })
        return invoice_line_id

    def _get_master_data(self, cr, uid, move, company, context=None):
        if move.procurement_id and move.procurement_id.sale_line_id:
            sale_order = move.procurement_id.sale_line_id.order_id
            return sale_order.partner_invoice_id, sale_order.user_id.id, sale_order.pricelist_id.currency_id.id
        return super(stock_move, self)._get_master_data(cr, uid, move, company, context=context)

    def _get_invoice_line_vals(self, cr, uid, move, partner, inv_type, context=None):
        res = super(stock_move, self)._get_invoice_line_vals(cr, uid, move, partner, inv_type, context=context)
        if move.procurement_id and move.procurement_id.sale_line_id:
            sale_line = move.procurement_id.sale_line_id
            res['invoice_line_tax_id'] = [(6, 0, [x.id for x in sale_line.tax_id])]
            res['account_analytic_id'] = sale_line.order_id.project_id and sale_line.order_id.project_id.id or False
            res['price_unit'] = sale_line.price_unit
            res['discount'] = sale_line.discount
        return res


class stock_location_route(osv.osv):
    _inherit = "stock.location.route"
    _columns = {
        'sale_selectable':fields.boolean("Applicable on Sales Order Line")
        }
