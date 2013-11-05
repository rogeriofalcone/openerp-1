# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-Today OpenERP SA (<http://www.openerp.com>).
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
from openerp import SUPERUSER_ID


# defined for access rules
class product(osv.osv):
    _inherit = 'product.product'
    _columns = {
        'event_ticket_ids': fields.one2many('event.event.ticket', 'product_id', 'Event Tickets'),
    }


class event(osv.osv):
    _name = 'event.event'
    _inherit = ['event.event','website.seo.metadata']
    _columns = {
        'twitter_hashtag': fields.char('Twitter Hashtag'),
        'website_published': fields.boolean('Available in the website'),
        # TDE TODO FIXME: when website_mail/mail_thread.py inheritance work -> this field won't be necessary
        'website_message_ids': fields.one2many(
            'mail.message', 'res_id',
            domain=lambda self: [
                '&', ('model', '=', self._name), ('type', '=', 'comment')
            ],
            string='Website Messages',
            help="Website communication history",
        ),
    }
    _defaults = {
        'website_published': False,
    }

    def _check_organizer_id_published(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.website_published and obj.organizer_id and not obj.organizer_id.website_published:
                return False
        return True
    def _check_address_id_published(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.website_published and obj.address_id and not obj.address_id.website_published:
                return False
        return True
    _constraints = [
        (_check_organizer_id_published, "This event can't be published if the field Orginizer is not website published.", ['organizer_id','website_published']),
        (_check_address_id_published, "This event can't be published if the field Location is not website published.", ['address_id','website_published']),
    ]

    def google_map_img(self, cr, uid, ids, zoom=8, width=298, height=298, context=None):
        partner = self.browse(cr, uid, ids[0], context=context)
        if partner.address_id:
            return self.browse(cr, SUPERUSER_ID, ids[0], context=context).address_id.google_map_img()

    def google_map_link(self, cr, uid, ids, zoom=8, context=None):
        partner = self.browse(cr, uid, ids[0], context=context)
        if partner.address_id:
            return self.browse(cr, SUPERUSER_ID, ids[0], context=context).address_id.google_map_link()


class sale_order_line(osv.osv):
    _inherit = "sale.order.line"

    def _recalculate_product_values(self, cr, uid, ids, product_id=0, context=None):
        if not ids:
            return super(sale_order_line, self)._recalculate_product_values(cr, uid, ids, product_id, context=context)

        order_line = self.browse(cr, uid, ids[0], context=context)
        product = product_id and self.pool.get('product.product').browse(cr, uid, product_id, context=context) or order_line.product_id
        res = super(sale_order_line, self)._recalculate_product_values(cr, uid, ids, product.id, context=context)
        if product.event_type_id and order_line.event_ticket_id and order_line.event_ticket_id.price != product.lst_price:
            res.update({'price_unit': order_line.event_ticket_id.price})

        return res
