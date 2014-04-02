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

from openerp.osv import fields, osv
from openerp.tools.translate import _

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
from datetime import datetime
import openerp

class procurement_group(osv.osv):
    _inherit = 'procurement.group'
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner')
    }

class procurement_rule(osv.osv):
    _inherit = 'procurement.rule'

    def _get_action(self, cr, uid, context=None):
        result = super(procurement_rule, self)._get_action(cr, uid, context=context)
        return result + [('move', 'Move From Another Location')]

    def _get_rules(self, cr, uid, ids, context=None):
        res = []
        for route in self.browse(cr, uid, ids):
            res += [x.id for x in route.pull_ids]
        return res

    def _get_route(self, cr, uid, ids, context=None):
        #WARNING TODO route_id is not required, so a field related seems a bad idea >-< 
        if context is None:
            context = {}
        result = {}
        if context is None:
            context = {}
        context_with_inactive = context.copy()
        context_with_inactive['active_test']=False
        for route in self.pool.get('stock.location.route').browse(cr, uid, ids, context=context_with_inactive):
            for pull_rule in route.pull_ids:
                result[pull_rule.id] = True
        return result.keys()

    _columns = {
        'location_id': fields.many2one('stock.location', 'Procurement Location'),
        'location_src_id': fields.many2one('stock.location', 'Source Location',
            help="Source location is action=move"),
        'route_id': fields.many2one('stock.location.route', 'Route',
            help="If route_id is False, the rule is global"),
        'procure_method': fields.selection([('make_to_stock', 'Make to Stock'), ('make_to_order', 'Make to Order')], 'Procure Method', required=True, help="'Make to Stock': When needed, take from the stock or wait until re-supplying. 'Make to Order': When needed, purchase or produce for the procurement request."),
        'route_sequence': fields.related('route_id', 'sequence', string='Route Sequence',
            store={
                'stock.location.route': (_get_rules, ['sequence'], 10),
                'procurement.rule': (lambda self, cr, uid, ids, c={}: ids, ['route_id'], 10),
        }),
        'picking_type_id': fields.many2one('stock.picking.type', 'Picking Type',
            help="Picking Type determines the way the picking should be shown in the view, reports, ..."),
        'active': fields.related('route_id', 'active', type='boolean', string='Active', store={
                    'stock.location.route': (_get_route, ['active'], 20),
                    'procurement.rule': (lambda self, cr, uid, ids, c={}: ids, ['route_id'], 20)},
                help="If the active field is set to False, it will allow you to hide the rule without removing it."),
        'delay': fields.integer('Number of Days'),
        'partner_address_id': fields.many2one('res.partner', 'Partner Address'),
        'propagate': fields.boolean('Propagate cancel and split', help='If checked, when the previous move of the move (which was generated by a next procurement) is cancelled or split, the move generated by this move will too'),
        'warehouse_id': fields.many2one('stock.warehouse', 'Served Warehouse', help='The warehouse this rule is for'),
        'propagate_warehouse_id': fields.many2one('stock.warehouse', 'Warehouse to Propagate', help="The warehouse to propagate on the created move/procurement, which can be different of the warehouse this rule is for (e.g for resupplying rules from another warehouse)"),
    }

    _defaults = {
        'procure_method': 'make_to_stock',
        'active': True,
        'propagate': True,
        'delay': 0,
    }

class procurement_order(osv.osv):
    _inherit = "procurement.order"
    _columns = {
        'location_id': fields.many2one('stock.location', 'Procurement Location'),  # not required because task may create procurements that aren't linked to a location with project_mrp
        'partner_dest_id': fields.many2one('res.partner', 'Customer Address', help="In case of dropshipping, we need to know the destination address more precisely"),
        'move_ids': fields.one2many('stock.move', 'procurement_id', 'Moves', help="Moves created by the procurement"),
        'move_dest_id': fields.many2one('stock.move', 'Destination Move', help="Move which caused (created) the procurement"),
        'route_ids': fields.many2many('stock.location.route', 'stock_location_route_procurement', 'procurement_id', 'route_id', 'Preferred Routes', help="Preferred route to be followed by the procurement order. Usually copied from the generating document (SO) but could be set up manually."),
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse', help="Warehouse to consider for the route selection"),
    }

    def propagate_cancel(self, cr, uid, procurement, context=None):
        if procurement.rule_id.action == 'move' and procurement.move_ids:
            self.pool.get('stock.move').action_cancel(cr, uid, [m.id for m in procurement.move_ids], context=context)

    def cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        to_cancel_ids = self.get_cancel_ids(cr, uid, ids, context=context)
        ctx = context.copy()
        #set the context for the propagation of the procurement cancelation
        ctx['cancel_procurement'] = True
        for procurement in self.browse(cr, uid, to_cancel_ids, context=ctx):
            if procurement.rule_id and procurement.rule_id.propagate:
                self.propagate_cancel(cr, uid, procurement, context=ctx)
        return super(procurement_order, self).cancel(cr, uid, to_cancel_ids, context=ctx)

    def _find_parent_locations(self, cr, uid, procurement, context=None):
        location = procurement.location_id
        res = [location.id]
        while location.location_id:
            location = location.location_id
            res.append(location.id)
        return res

    def change_warehouse_id(self, cr, uid, ids, warehouse_id, context=None):
        if warehouse_id:
            warehouse = self.pool.get('stock.warehouse').browse(cr, uid, warehouse_id, context=context)
            return {'value': {'location_id': warehouse.lot_stock_id.id}}
        return {}

    def _search_suitable_rule(self, cr, uid, procurement, domain, context=None):
        '''we try to first find a rule among the ones defined on the procurement order group and if none is found, we try on the routes defined for the product, and finally we fallback on the default behavior'''
        pull_obj = self.pool.get('procurement.rule')
        warehouse_route_ids = []
        if procurement.warehouse_id:
            domain += ['|', ('warehouse_id', '=', procurement.warehouse_id.id), ('warehouse_id', '=', False)]
            warehouse_route_ids = [x.id for x in procurement.warehouse_id.route_ids]
        product_route_ids = [x.id for x in procurement.product_id.route_ids + procurement.product_id.categ_id.total_route_ids]
        procurement_route_ids = [x.id for x in procurement.route_ids]
        res = pull_obj.search(cr, uid, domain + [('route_id', 'in', procurement_route_ids)], order='route_sequence, sequence', context=context)
        if not res:
            res = pull_obj.search(cr, uid, domain + [('route_id', 'in', product_route_ids)], order='route_sequence, sequence', context=context)
            if not res:
                res = warehouse_route_ids and pull_obj.search(cr, uid, domain + [('route_id', 'in', warehouse_route_ids)], order='route_sequence, sequence', context=context) or []
                if not res:
                    res = pull_obj.search(cr, uid, domain + [('route_id', '=', False)], order='sequence', context=context)
        return res

    def _find_suitable_rule(self, cr, uid, procurement, context=None):
        rule_id = super(procurement_order, self)._find_suitable_rule(cr, uid, procurement, context=context)
        if not rule_id:
            #a rule defined on 'Stock' is suitable for a procurement in 'Stock\Bin A'
            all_parent_location_ids = self._find_parent_locations(cr, uid, procurement, context=context)
            rule_id = self._search_suitable_rule(cr, uid, procurement, [('location_id', 'in', all_parent_location_ids)], context=context)
            rule_id = rule_id and rule_id[0] or False
        return rule_id

    def _run_move_create(self, cr, uid, procurement, context=None):
        ''' Returns a dictionary of values that will be used to create a stock move from a procurement.
        This function assumes that the given procurement has a rule (action == 'move') set on it.

        :param procurement: browse record
        :rtype: dictionary
        '''
        newdate = (datetime.strptime(procurement.date_planned, '%Y-%m-%d %H:%M:%S') - relativedelta(days=procurement.rule_id.delay or 0)).strftime('%Y-%m-%d %H:%M:%S')
        group_id = False
        if procurement.rule_id.group_propagation_option == 'propagate':
            group_id = procurement.group_id and procurement.group_id.id or False
        elif procurement.rule_id.group_propagation_option == 'fixed':
            group_id = procurement.rule_id.group_id and procurement.rule_id.group_id.id or False
        #it is possible that we've already got some move done, so check for the done qty and create
        #a new move with the correct qty
        already_done_qty = 0
        already_done_qty_uos = 0
        for move in procurement.move_ids:
            already_done_qty += move.product_uom_qty if move.state == 'done' else 0
            already_done_qty_uos += move.product_uos_qty if move.state == 'done' else 0
        qty_left = max(procurement.product_qty - already_done_qty, 0)
        qty_uos_left = max(procurement.product_uos_qty - already_done_qty_uos, 0)
        vals = {
            'name': procurement.name,
            'company_id': procurement.company_id.id,
            'product_id': procurement.product_id.id,
            'product_qty': qty_left,
            'product_uom': procurement.product_uom.id,
            'product_uom_qty': qty_left,
            'product_uos_qty': (procurement.product_uos and qty_uos_left) or qty_left,
            'product_uos': (procurement.product_uos and procurement.product_uos.id) or procurement.product_uom.id,
            'partner_id': procurement.group_id and procurement.group_id.partner_id and procurement.group_id.partner_id.id or False,
            'location_id': procurement.rule_id.location_src_id.id,
            'location_dest_id': procurement.rule_id.location_id.id,
            'move_dest_id': procurement.move_dest_id and procurement.move_dest_id.id or False,
            'procurement_id': procurement.id,
            'rule_id': procurement.rule_id.id,
            'procure_method': procurement.rule_id.procure_method,
            'origin': procurement.origin,
            'picking_type_id': procurement.rule_id.picking_type_id.id,
            'group_id': group_id,
            'route_ids': [(4, x.id) for x in procurement.route_ids],
            'warehouse_id': procurement.rule_id.propagate_warehouse_id and procurement.rule_id.propagate_warehouse_id.id or procurement.rule_id.warehouse_id.id,
            'date': newdate,
            'date_expected': newdate,
            'propagate': procurement.rule_id.propagate,
        }
        return vals

    def _run(self, cr, uid, procurement, context=None):
        if procurement.rule_id and procurement.rule_id.action == 'move':
            if not procurement.rule_id.location_src_id:
                self.message_post(cr, uid, [procurement.id], body=_('No source location defined!'), context=context)
                return False
            move_obj = self.pool.get('stock.move')
            move_dict = self._run_move_create(cr, uid, procurement, context=context)
            move_obj.create(cr, uid, move_dict, context=context)
            self.message_post(cr, uid, [procurement.id], body=_("Supply Move created"), context=context)
            return True
        return super(procurement_order, self)._run(cr, uid, procurement, context=context)

    def run(self, cr, uid, ids, context=None):
        res = super(procurement_order, self).run(cr, uid, ids, context=context)
        #after all the procurements are run, check if some created a draft stock move that needs to be confirmed
        #(we do that in batch because it fasts the picking assignation and the picking state computation)
        move_to_confirm_ids = []
        for procurement in self.browse(cr, uid, ids, context=context):
            if procurement.state == "running" and procurement.rule_id and procurement.rule_id.action == "move":
                move_to_confirm_ids += [m.id for m in procurement.move_ids if m.state == 'draft']
        if move_to_confirm_ids:
            self.pool.get('stock.move').action_confirm(cr, uid, move_to_confirm_ids, context=context)
        return res

    def _check(self, cr, uid, procurement, context=None):
        ''' Implement the procurement checking for rules of type 'move'. The procurement will be satisfied only if all related
            moves are done/cancel and if the requested quantity is moved.
        '''
        if procurement.rule_id and procurement.rule_id.action == 'move':
            uom_obj = self.pool.get('product.uom')
            done_test_list = []
            done_cancel_test_list = []
            qty_done = 0
            for move in procurement.move_ids:
                done_test_list.append(move.state == 'done')
                done_cancel_test_list.append(move.state in ('done', 'cancel'))
                qty_done += move.product_qty if move.state == 'done' else 0
            qty_done = uom_obj._compute_qty(cr, uid, procurement.product_id.uom_id.id, qty_done, procurement.product_uom.id)
            at_least_one_done = any(done_test_list)
            all_done_or_cancel = all(done_cancel_test_list)
            if not all_done_or_cancel:
                return False
            elif all_done_or_cancel and procurement.product_qty == qty_done:
                return True
            elif at_least_one_done:
                #some move cancelled and some validated
                self.message_post(cr, uid, [procurement.id], body=_('Some stock moves have been cancelled for this procurement. Run the procurement again to trigger a move for the remaining quantity or change the procurement quantity to finish it directly'), context=context)
            else:
                #all move are cancelled
                self.message_post(cr, uid, [procurement.id], body=_('All stock moves have been cancelled for this procurement.'), context=context)
            self.write(cr, uid, [procurement.id], {'state': 'exception'}, context=context)    
            return False

        return super(procurement_order, self)._check(cr, uid, procurement, context)

    def do_view_pickings(self, cr, uid, ids, context=None):
        '''
        This function returns an action that display the pickings of the procurements belonging
        to the same procurement group of given ids.
        '''
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.get_object_reference(cr, uid, 'stock', 'do_view_pickings')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        group_ids = set([proc.group_id.id for proc in self.browse(cr, uid, ids, context=context) if proc.group_id])
        result['domain'] = "[('group_id','in',[" + ','.join(map(str, list(group_ids))) + "])]"
        return result

    #
    # Scheduler
    # When stock is installed, it should also check for the different confirmed stock moves
    # if they can not be installed
    #
    #
    def run_scheduler(self, cr, uid, use_new_cursor=False, context=None):
        '''
        Call the scheduler in order to 

        @param self: The object pointer
        @param cr: The current row, from the database cursor,
        @param uid: The current user ID for security checks
        @param ids: List of selected IDs
        @param use_new_cursor: False or the dbname
        @param context: A standard dictionary for contextual values
        @return:  Dictionary of values
        '''

        super(procurement_order, self).run_scheduler(cr, uid, use_new_cursor=use_new_cursor, context=context)
        if context is None:
            context = {}
        try:
            if use_new_cursor:
                cr = openerp.registry(use_new_cursor).db.cursor()

            company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
            move_obj = self.pool.get('stock.move')
            #Minimum stock rules
            self. _procure_orderpoint_confirm(cr, uid, use_new_cursor=False, context=context, user_id=False)

            #Search all confirmed stock_moves and try to assign them
            confirmed_ids = move_obj.search(cr, uid, [('state', '=', 'confirmed'), ('company_id','=', company.id)], limit=None, order='picking_priority desc, date_expected asc', context=context)
            for x in xrange(0, len(confirmed_ids), 100):
                move_obj.action_assign(cr, uid, confirmed_ids[x:x+100], context=context)
                if use_new_cursor:
                    cr.commit()
            
            
            if use_new_cursor:
                cr.commit()
        finally:
            if use_new_cursor:
                try:
                    cr.close()
                except Exception:
                    pass
        return {}


    def _get_orderpoint_date_planned(self, cr, uid, orderpoint, start_date, context=None):
        date_planned = start_date
        return date_planned.strftime(DEFAULT_SERVER_DATE_FORMAT)

    def _prepare_orderpoint_procurement(self, cr, uid, orderpoint, product_qty, context=None):
        return {'name': orderpoint.name,
                'date_planned': self._get_orderpoint_date_planned(cr, uid, orderpoint, datetime.today(), context=context),
                'product_id': orderpoint.product_id.id,
                'product_qty': product_qty,
                'company_id': orderpoint.company_id.id,
                'product_uom': orderpoint.product_uom.id,
                'location_id': orderpoint.location_id.id,
                'origin': orderpoint.name,
                'warehouse_id': orderpoint.warehouse_id.id}

    def _product_virtual_get(self, cr, uid, order_point):
        product_obj = self.pool.get('product.product')
        return product_obj._product_available(cr, uid,
                [order_point.product_id.id],
                context = {'location': order_point.location_id.id})[order_point.product_id.id]['virtual_available']

    def _procure_orderpoint_confirm(self, cr, uid, \
            use_new_cursor=False, context=None, user_id=False):
        '''
        Create procurement based on Orderpoint
        use_new_cursor: False or the dbname

        @param self: The object pointer
        @param cr: The current row, from the database cursor,
        @param user_id: The current user ID for security checks
        @param context: A standard dictionary for contextual values
        @param param: False or the dbname
        @return:  Dictionary of values
        """
        '''
        if context is None:
            context = {}
        if use_new_cursor:
            cr = openerp.registry(use_new_cursor).db.cursor()
        orderpoint_obj = self.pool.get('stock.warehouse.orderpoint')
        
        procurement_obj = self.pool.get('procurement.order')
        offset = 0
        ids = [1]
        while ids:
            ids = orderpoint_obj.search(cr, uid, [], offset=offset, limit=100)
            for op in orderpoint_obj.browse(cr, uid, ids, context=context):
                prods = self._product_virtual_get(cr, uid, op)
                if prods is None:
                    continue
                if prods < op.product_min_qty:
                    qty = max(op.product_min_qty, op.product_max_qty)-prods

                    reste = qty % op.qty_multiple
                    if reste > 0:
                        qty += op.qty_multiple - reste

                    if qty <= 0:
                        continue
                    if op.product_id.type not in ('consu'):
                        procurement_draft_ids = orderpoint_obj.get_draft_procurements(cr, uid, op. id, context=context)
                        if procurement_draft_ids:
                            # Check draft procurement related to this order point
                            procure_datas = procurement_obj.read(
                                cr, uid, procurement_draft_ids, ['id', 'product_qty'], context=context)
                            to_generate = qty
                            for proc_data in procure_datas:
                                if to_generate >= proc_data['product_qty']:
                                    self.signal_button_confirm(cr, uid, [proc_data['id']])
                                    procurement_obj.write(cr, uid, [proc_data['id']],  {'origin': op.name}, context=context)
                                    to_generate -= proc_data['product_qty']
                                if not to_generate:
                                    break
                            qty = to_generate

                    if qty:
                        proc_id = procurement_obj.create(cr, uid,
                                                         self._prepare_orderpoint_procurement(cr, uid, op, qty, context=context),
                                                         context=context)
                        self.check(cr, uid, [proc_id])
                        self.run(cr, uid, [proc_id])
                        orderpoint_obj.write(cr, uid, [op.id],
                                {'procurement_id': proc_id}, context=context)
            offset += len(ids)
            if use_new_cursor:
                cr.commit()
        if use_new_cursor:
            cr.commit()
            cr.close()
        return {}
