# -*- coding: utf-8 -*-

from openerp.osv import osv, fields


class hr(osv.osv):
    _inherit = 'hr.employee'
    _columns = {
        'website_published': fields.boolean('Available in the website'),
        'public_info': fields.text('Public Info'),
    }

    def img(self, cr, uid, ids, field='image_small', context=None):
        return "/website/image?model=%s&field=%s&id=%s" % (self._name, field, ids[0])
