# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY Pexego (<www.pexego.es>). All Rights Reserved
#    $Omar Castiñeira Saavedra$
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
from tools.misc import UpdateableStr, UpdateableDict
import pooler

import wizard
import tools
from tools.translate import _

_moves_arch = UpdateableStr()
_moves_fields = UpdateableDict()

_moves_arch_end = '''<?xml version="1.0"?>
<form string="Packing result">
    <label string="The packing has been successfully made !" colspan="4"/>
    <field name="back_order_notification" colspan="4" nolabel="1"/>
</form>'''
_moves_fields_end = {
    'back_order_notification': {'string':'Back Order' ,'type':'text', 'readonly':True}
                     }

def make_default(val):
    def fct(uid, data, state):
        return val
    return fct

def _to_xml(s):
    return (s or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def _get_moves(self, cr, uid, data, context):
    pick_obj = pooler.get_pool(cr.dbname).get('stock.picking')
    user_obj = pooler.get_pool(cr.dbname).get('res.users')
    pick = pick_obj.browse(cr, uid, [data['id']], context)[0]
    res = {}

    _moves_fields.clear()
    _moves_arch_lst = ['<?xml version="1.0"?>', _('<form string="Make packing">')]

    for m in pick.move_lines:
        if m.state in ('done', 'cancel'):
            continue
        quantity = m.product_qty
        if m.state<>'assigned':
            quantity = 0

        _moves_arch_lst.append('<field name="move%s" />' % (m.id,))
        _moves_fields['move%s' % m.id] = {
                'string': _to_xml(m.name),
                'type' : 'float', 'required' : True, 'default' : make_default(quantity)}

        currency=0
        user = user_obj.browse(cr, uid, uid)
        if (pick.type == 'in') and (m.product_id.cost_method == 'average'):
            price=m.product_id.standard_price
            if hasattr(m, 'purchase_line_id') and m.purchase_line_id:
                price=m.purchase_line_id.price_unit
                currency=m.purchase_line_id.order_id.pricelist_id.currency_id.id
            elif not m.purchase_line_id:
                price = m.price_unit or m.product_id.standard_price
                currency = user.company_id.currency_id.id

            _moves_arch_lst.append('<group col="6"><field name="uom%s" nolabel="1"/>\
                    <field name="price%s"/>' % (m.id,m.id,))

            _moves_fields['price%s' % m.id] = {'string': _('Unit Price'),
                    'type': 'float', 'required': True, 'default': make_default(price),'digits':(16, 4)}

            _moves_fields['uom%s' % m.id] = {'string': _('UOM'), 'type': 'many2one',
                    'relation': 'product.uom', 'required': True,
                    'default': make_default(m.product_uom.id)}

            _moves_arch_lst.append('<field name="currency%d" nolabel="1"/></group>' % (m.id,))
            _moves_fields['currency%s' % m.id] = {'string': _('Currency'),
                    'type': 'many2one', 'relation': 'res.currency',
                    'required': True, 'default': make_default(currency)}

        _moves_arch_lst.append('<newline/>')
        res.setdefault('moves', []).append(m.id)

    _moves_arch_lst.append('</form>')
    _moves_arch.string = '\n'.join(_moves_arch_lst)
    return res

def _do_split(self, cr, uid, data, context):
    """done the picking or done a partial picking when new draft picking"""
    pool = pooler.get_pool(cr.dbname)
    move_obj = pool.get('stock.move')
    pick_obj = pool.get('stock.picking')
    currency_obj = pool.get('res.currency')
    users_obj = pool.get('res.users')
    product_obj = pool.get('product.product')
    uom_obj = pool.get('product.uom')
    pick = pick_obj.browse(cr, uid, [data['id']])[0]
    user = users_obj.browse(cr, uid, [uid])[0]
    new_picking = None

    complete, too_many, too_few = [], [], []
    #total of delivery prices in invoice and external delivery expenses
    delivery_price = 0.0
    total_price = 0.0

    #sum external delivery expenses to delivery price
    if pick.freight_tbcollected_id:
        for dl in pick.freight_tbcollected_id:
            delivery_price += currency_obj.compute(cr, uid, dl.currency_id.id, user.company_id.currency_id.id, dl.price, round=True)

    #normal behavior
    for move in move_obj.browse(cr, uid, data['form'].get('moves',[])):
        if move.product_qty == data['form']['move%s' % move.id]:
            complete.append(move)
        elif move.product_qty > data['form']['move%s' % move.id]:
            too_few.append(move)
        else:
            too_many.append(move)

        if (pick.type == 'in'):
            if move.shipment_line:
                delivery_price += 'price%s' % move.id in data['form'] and (data['form']['price%s' % move.id] * data['form']['move%s' % move.id]) or (move.purchase_line_id and move.purchase_line_id.price_unit or (move.price_unit or move.product_id.standard_price or 0.0))
            else:
                total_price += 'price%s' % move.id in data['form'] and (data['form']['price%s' % move.id] * data['form']['move%s' % move.id]) or (move.purchase_line_id and move.purchase_line_id.price_unit or (move.price_unit or move.product_id.standard_price or 0.0))

        # Average price computation
        if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
            product = product_obj.browse(cr, uid, [move.product_id.id])[0]

            qty = data['form']['move%s' % move.id]
            uom = data['form']['uom%s' % move.id]
            price = data['form']['price%s' % move.id]
            currency = data['form']['currency%s' % move.id]

            qty = uom_obj._compute_qty(cr, uid, uom, qty, product.uom_id.id)

            if (qty > 0):
                new_price = currency_obj.compute(cr, uid, currency,
                        user.company_id.currency_id.id, price, False)
                new_price = uom_obj._compute_price(cr, uid, uom, new_price,
                        product.uom_id.id)
                if product.qty_available<=0:
                    new_std_price = new_price
                else:
                    new_std_price = ((product.standard_price * product.qty_available)\
                        + (new_price * qty))/(product.qty_available + qty)

                product_obj.write(cr, uid, [product.id],
                        {'standard_price': new_std_price})
                move_obj.write(cr, uid, [move.id], {'price_unit': new_price})

    #compute average delivery cost price
    if pick.type == 'in' and (move.product_id.cost_method == 'average'):
        for move in move_obj.browse(cr, uid, data['form'].get('moves',[])):
            if move.shipment_line:
                continue
            product = product_obj.browse(cr, uid, [move.product_id.id])[0]

            qty = data['form']['move%s' % move.id]
            uom = data['form']['uom%s' % move.id]
            price = data['form']['price%s' % move.id]
            currency = data['form']['currency%s' % move.id]

            qty = uom_obj._compute_qty(cr, uid, uom, qty, product.uom_id.id)

            if (qty > 0):
                new_price = currency_obj.compute(cr, uid, currency,
                        user.company_id.currency_id.id, price, False)
                new_price = uom_obj._compute_price(cr, uid, uom, new_price,
                        product.uom_id.id)

                average_delivery_price = (new_price / total_price) * delivery_price

                if product.qty_available<=0:
                    new_std_price = new_price + average_delivery_price
                else:
                    new_std_price = ((product.standard_delivery_price * product.qty_available)\
                        + ((new_price + average_delivery_price) * qty))/(product.qty_available + qty)

                product_obj.write(cr, uid, [product.id],
                        {'standard_delivery_price': new_std_price})


    for move in too_few:
        if not new_picking:

            new_picking = pick_obj.copy(cr, uid, pick.id,
                    {
                        'name': '/',
                        'move_lines' : [],
                        'state':'draft',
                    })
        if data['form']['move%s' % move.id] <> 0:
            new_obj = move_obj.copy(cr, uid, move.id,
                {
                    'product_qty' : data['form']['move%s' % move.id],
                    'product_uos_qty':data['form']['move%s' % move.id],
                    'picking_id' : new_picking,
                    'state': 'assigned',
                    'move_dest_id': False,
                    'price_unit': move.price_unit,
                })
        move_obj.write(cr, uid, [move.id],
                {
                    'product_qty' : move.product_qty - data['form']['move%s' % move.id],
                    'product_uos_qty':move.product_qty - data['form']['move%s' % move.id],
                })

    if new_picking:
        move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
        for move in too_many:
            move_obj.write(cr, uid, [move.id],
                    {
                        'product_qty' : data['form']['move%s' % move.id],
                        'product_uos_qty': data['form']['move%s' % move.id],
                        'picking_id': new_picking,
                    })
    else:
        for move in too_many:
            move_obj.write(cr, uid, [move.id],
                    {
                        'product_qty': data['form']['move%s' % move.id],
                        'product_uos_qty': data['form']['move%s' % move.id]
                    })

    # At first we confirm the new picking (if necessary)
    wf_service = netsvc.LocalService("workflow")
    if new_picking:
        wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
    # Then we finish the good picking
    if new_picking:
        pick_obj.write(cr, uid, [pick.id], {'backorder_id': new_picking})
        pick_obj.action_move(cr, uid, [new_picking])
        wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
        wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
    else:
        pick_obj.action_move(cr, uid, [pick.id])
        wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
    bo_name = ''
    if new_picking:
        bo_name = pick_obj.read(cr, uid, [new_picking], ['name'])[0]['name']
    return {'new_picking':new_picking or False, 'back_order':bo_name}

def _get_default(self, cr, uid, data, context):
    if data['form']['back_order']:
        data['form']['back_order_notification'] = _('Back Order %s Assigned to this Packing.') % (tools.ustr(data['form']['back_order']),)
    return data['form']

class partial_picking2(wizard.interface):

    states = {
        'init': {
            'actions': [ _get_moves ],
            'result': {'type': 'form', 'arch': _moves_arch, 'fields': _moves_fields,
                'state' : (
                    ('end', 'Cancel'),
                    ('split', 'Make Picking')
                )
            },
        },
        'split': {
            'actions': [ _do_split ],
            'result': {'type': 'state', 'state': 'end2'},
        },
        'end2': {
            'actions': [ _get_default ],
            'result': {'type': 'form', 'arch': _moves_arch_end,
                'fields': _moves_fields_end,
                'state': (
                    ('end', 'Close'),
                )
            },
        },
    }

partial_picking2('delivery_costs.partial.picking')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

