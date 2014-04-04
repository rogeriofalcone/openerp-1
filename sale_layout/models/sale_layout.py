# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today OpenERP SA (<http://www.openerp.com>).
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

from openerp.osv import osv, fields
from itertools import groupby


def grouplines(self, ordered_lines, sortkey):
    """Return lines from a specified invoice or sale order grouped by category"""
    grouped_lines = []
    for key, valuesiter in groupby(ordered_lines, sortkey):
        group = {}
        group['category'] = key
        group['lines'] = list(v for v in valuesiter)

        if 'subtotal' in key and key.subtotal is True:
            group['subtotal'] = sum(line.price_subtotal for line in group['lines'])
        grouped_lines.append(group)

    return grouped_lines


class SaleLayoutCategory(osv.Model):
    _name = 'sale_layout.category'
    _order = 'sequence'
    _columns = {
        'name': fields.char('Name', required=True),
        'sequence': fields.integer('Sequence', required=True),
        'subtotal': fields.boolean('Add subtotal'),
        'separator': fields.boolean('Add separator'),
        'pagebreak': fields.boolean('Add pagebreak')
    }

    _defaults = {
        'subtotal': True,
        'separator': True,
        'pagebreak': False,
        'sequence': 10
    }

    # We want to forbid edit of a category if it is already linked to a report.
    def _check(self, cr, uid, ids):
        for cat in self.browse(cr, uid, ids):
            invoice_obj = self.pool.get('account.invoice.line')
            sale_obj = self.pool.get('sale.order.line')
            ids = invoice_obj.search(cr, uid, [('sale_layout_cat_id', '=', cat.id)])
            ids += sale_obj.search(cr, uid, [('sale_layout_cat_id', '=', cat.id)])

            if len(ids) > 0:
                return False

        return True

    _constraints = [(
        _check,
        'This category could not be modified nor deleted because it is still used in an invoice or'
        ' a sale report.', ['name']
    )]


class AccountInvoice(osv.Model):
    _inherit = 'account.invoice'

    def sale_layout_lines(self, cr, uid, ids, context, invoice_id, *args, **kwargs):
        """
        Returns invoice lines from a specified invoice ordered by
        sale_layout_category sequence. Used in sale_layout module.

        :Parameters:
            -'invoice_id' (int): specify the concerned invoice.
        """
        ordered_lines = self.browse(cr, uid, invoice_id, context=context).invoice_line
        # We chose to group first by category model and, if not present, by invoice name
        sortkey = lambda x: x.sale_layout_cat_id if x.sale_layout_cat_id else ''

        return grouplines(self, ordered_lines, sortkey)


class AccountInvoiceLine(osv.Model):
    _inherit = 'account.invoice.line'
    _columns = {
        'sale_layout_cat_id': fields.many2one('sale_layout.category',
                                              'Layout Category'),
        'categ_sequence': fields.related('sale_layout_cat_id',
                                         'sequence', type='integer',
                                         string='Layout Sequence', store=True)
        #  Store is intentionally set in order to keep the "historic" order.
    }
    _order = 'invoice_id, categ_sequence, sequence, id'


class SaleOrder(osv.Model):
    _inherit = 'sale.order'

    def sale_layout_lines(self, cr, uid, ids, context, order_id, *args, **kwargs):
        """
        Returns order lines from a specified sale ordered by
        sale_layout_category sequence. Used in sale_layout module.

        :Parameters:
            -'order_id' (int): specify the concerned sale order.
        """
        ordered_lines = self.browse(cr, uid, order_id, context=context).order_line
        sortkey = lambda x: x.sale_layout_cat_id if x.sale_layout_cat_id else ''

        return grouplines(self, ordered_lines, sortkey)


class SaleOrderLine(osv.Model):
    _inherit = 'sale.order.line'
    _columns = {
        'sale_layout_cat_id': fields.many2one('sale_layout.category',
                                              'Layout Category'),
        'categ_sequence': fields.related('sale_layout_cat_id',
                                         'sequence', type='integer',
                                         string='Layout Sequence', store=True)
        #  Store is intentionally set in order to keep the "historic" order.
    }
    _order = 'order_id, categ_sequence, sequence, id'
