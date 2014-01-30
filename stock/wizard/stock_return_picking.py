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

from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class stock_return_picking_line(osv.osv_memory):
    _name = "stock.return.picking.line"
    _rec_name = 'product_id'

    _columns = {
        'product_id': fields.many2one('product.product', string="Product", required=True),
        'quantity': fields.float("Quantity", digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
        'wizard_id': fields.many2one('stock.return.picking', string="Wizard"),
        'move_id': fields.many2one('stock.move', "Move"),
        'lot_id': fields.related('move_id', 'quant_ids', 'lot_id', type="many2one", relation='stock.production.lot', string='Serial Number', readonly=True),
    }


class stock_return_picking(osv.osv_memory):
    _name = 'stock.return.picking'
    _description = 'Return Picking'
    _columns = {
        'product_return_moves': fields.one2many('stock.return.picking.line', 'wizard_id', 'Moves'),
        'move_dest_exists': fields.boolean('Chained Move Exists', readonly = True),
        'move_dest_method': fields.selection([('nothing', 'Do Nothing'), ('cancel', 'Split and Cancel Next Moves => Do not receive returned products again'), 
                                              ('create', 'Split and Create New Original Move => Receive returned products again later')], 
                                             string="With Chained Moves"),
    }
    
    _defaults = {
        'move_dest_method': 'nothing',
            }

    def default_get(self, cr, uid, fields, context=None):
        """
         To get default values for the object.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary with default values for all field in ``fields``
        """
        result1 = []
        if context is None:
            context = {}
        res = super(stock_return_picking, self).default_get(cr, uid, fields, context=context)
        record_id = context and context.get('active_id', False) or False
        pick_obj = self.pool.get('stock.picking')
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        quant_obj = self.pool.get("stock.quant")
        move_obj = self.pool.get("stock.move")
        move_dest = False
        if pick:
            if pick.state != 'done':
                raise osv.except_osv(_('Warning!'), _("You may only return pickings that are Done!"))

            #Check if chained moves are not done already.  In the mean time, sum the quants in that location
            for move in pick.move_lines:
                if move.move_dest_id:
                    move_dest = True
                    #Backorder moves
                    moves = move_obj.search(cr, uid, [('split_from', '=', move.move_dest_id.id)], context=context)
                    moves = [move.move_dest_id] + move_obj.browse(cr, uid, moves, context=context)
                    if all([x.state in ['done'] for x in moves]):
                        raise osv.except_osv(_('Warning!'), _('You can not reverse when the chained moves are done!'))
                #Search quants
                quant_search = quant_obj.search(cr, uid, ['&', '&', ('history_ids', 'in', move.id), ('qty', '>', 0.0), 
                                                            ('location_id', 'child_of', move.location_dest_id.id)], context=context)
                qty = 0
                for quant in quant_obj.browse(cr, uid, quant_search, context=context):
                    if not quant.reservation_id or quant.reservation_id.origin_returned_move_id.id != move.id:
                        qty += quant.qty
                result1.append({'product_id': move.product_id.id, 'quantity': qty, 'move_id': move.id})

            if len(result1) == 0:
                raise osv.except_osv(_('Warning!'), _("No products to return (only lines in Done state and not fully returned yet can be returned)!"))
            if 'product_return_moves' in fields:
                res.update({'product_return_moves': result1})
            if 'move_dest_exists' in fields:
                res.update({'move_dest_exists': move_dest})
        return res

    def _create_returns(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('stock.picking')
        uom_obj = self.pool.get('product.uom')
        data_obj = self.pool.get('stock.return.picking.line')
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        data = self.read(cr, uid, ids[0], context=context)
        returned_lines = 0

        #Create new picking for returned products
        pick_type_id = pick.picking_type_id.return_picking_type_id and pick.picking_type_id.return_picking_type_id.id or pick.picking_type_id.id
        
        # Cancel assignment of existing chained assigned moves
        moves_to_unreserve = [x.move_dest_id.id for x in pick.move_lines if x.move_dest_id and x.move_dest_id.state == "assigned"]
        if moves_to_unreserve:
            move_obj.do_unreserve(cr, uid, moves_to_unreserve, context=context)
        
        new_picking = pick_obj.copy(cr, uid, pick.id, {
            'move_lines': [],
            'picking_type_id': pick_type_id,
            'state': 'draft',
            'origin': pick.name,
        },context=context)
        
        for data_get in data_obj.browse(cr, uid, data['product_return_moves'], context=context):
            move = data_get.move_id
            if not move:
                raise osv.except_osv(_('Warning !'), _("You have manually created product lines, please delete them to proceed"))
            new_qty = data_get.quantity
            if new_qty:
                returned_lines += 1
                return_move = move_obj.copy(cr, uid, move.id, {
                    'product_id': data_get.product_id.id,
                    'product_uom_qty': new_qty,
                    'product_uos_qty': uom_obj._compute_qty(cr, uid, move.product_uom.id, new_qty, move.product_uos.id),
                    'picking_id': new_picking,
                    'state': 'draft',
                    'location_id': move.location_dest_id.id,
                    'location_dest_id': move.location_id.id,
                    'origin_returned_move_id': move.id,
                    'procure_method': 'make_to_stock',
                })
                if data['move_dest_method'] == 'cancel':
                    if move.move_dest_id and move.move_dest_id.state not in ['done', 'cancel']:
                        res = move_obj.split(cr, uid, move.move_dest_id, new_qty, context=context)
                        move_obj.action_cancel(cr, uid, [res], context=context)
                if data['move_dest_method'] == 'create':
                    if move.move_dest_id and move.move_dest_id.state not in ['done', 'cancel']:
                        res = move_obj.split(cr, uid, move.move_dest_id, new_qty, context=context)
                        new_move = move_obj.copy(cr, uid, move.id, {
                                       'location_id': move.location_id.id,
                                       'location_dest_id': move.location_dest_id.id,
                                       'product_uom_qty': new_qty, 
                                       'product_uos_qty': uom_obj._compute_qty(cr, uid, move.product_uom.id, new_qty, move.product_uos.id),
                                       'move_dest_id': res,
                                       'picking_id': False, 
                                       })
                        move_obj.action_confirm(cr, uid, [new_move], context=context)
        if not returned_lines:
            raise osv.except_osv(_('Warning!'), _("Please specify at least one non-zero quantity."))

        pick_obj.action_confirm(cr, uid, [new_picking], context=context)
        pick_obj.action_assign(cr, uid, [new_picking], context)
        return new_picking, pick_type_id

    def create_returns(self, cr, uid, ids, context=None):
        """
         Creates return picking.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param ids: List of ids selected
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        new_picking_id, pick_type_id = self._create_returns(cr, uid, ids, context=context)
        # Override the context to disable all the potential filters that could have been set previously
        ctx = {
               'search_default_picking_type_id': pick_type_id,
               'search_default_draft': False,
               'search_default_assigned': False,
               'search_default_confirmed': False,
               'search_default_ready': False,
               'search_default_late': False,
               'search_default_available': False,
        }
        return {
            'domain': "[('id', 'in', [" + str(new_picking_id) + "])]",
            'name': _('Returned Picking'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'context': ctx,
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
