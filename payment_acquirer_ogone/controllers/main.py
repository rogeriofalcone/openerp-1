# -*- coding: utf-8 -*-
import logging
import pprint

from openerp.addons.web import http
from openerp.addons.web.http import request

_logger = logging.getLogger(__name__)


class OgoneController(http.Controller):
    _accept_url = '/payment/ogone/test/accept'
    _decline_url = '/payment/ogone/test/decline'
    _exception_url = '/payment/ogone/test/exception'
    _cancel_url = '/payment/ogone/test/cancel'

    @http.route([
        '/payment/ogone/accept', '/payment/ogone/test/accept',
        '/payment/ogone/decline', '/payment/ogone/test/decline',
        '/payment/ogone/exception', '/payment/ogone/test/exception',
        '/payment/ogone/cancel', '/payment/ogone/test/cancel',
    ], type='http', auth='admin', website=True)
    def ogone_form_feedback(self, **post):
        """ Ogone contacts using GET, at least for accept """
        _logger.info('Ogone: entering form_feedback with post data %s', pprint.pformat(post))  # debug
        cr, uid, context = request.cr, request.uid, request.context
        request.registry['payment.transaction'].form_feedback(cr, uid, post, 'ogone', context=context)
        return request.redirect(post.pop('return_url', '/'))
