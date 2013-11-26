# -*- coding: utf-8 -*-
import traceback
import werkzeug.routing
import openerp
from openerp.addons.base import ir
from openerp.http import request
from openerp.osv import orm

from ..utils import slugify
from website import get_current_website

class ir_http(orm.AbstractModel):
    _inherit = 'ir.http'

    def _get_converters(self):
        return dict(
            super(ir_http, self)._get_converters(),
            model=ModelConverter,
            page=PageConverter,
        )

    def _auth_method_public(self):
        if not request.session.uid:
            request.uid = request.registry['website'].get_public_user(
                request.cr, openerp.SUPERUSER_ID, request.context).id
        else:
            request.uid = request.session.uid

    def _handle_403(self, exception):
        return self._render_error(403, {
            'error': exception.message
        })

    def _handle_404(self, exception):
        return self._render_error(404)

    def _handle_500(self, exception):
        # TODO: proper logging
        return self._render_error(500, {
            'exception': exception,
            'traceback': traceback.format_exc(),
            'qweb_template': getattr(exception, 'qweb_template', None),
            'qweb_node': getattr(exception, 'qweb_node', None),
            'qweb_eval': getattr(exception, 'qweb_eval', None),
        })

    def _render_error(self, code, values=None):
        self._auth_method_public()
        if not hasattr(request, 'website'):
            request.website = get_current_website()
            request.website.preprocess_request(request)
        return werkzeug.wrappers.Response(
            request.website._render('website.%s' % code, values),
            status=code,
            content_type='text/html;charset=utf-8')

class ModelConverter(ir.ir_http.ModelConverter):
    def __init__(self, url_map, model=False):
        super(ModelConverter, self).__init__(url_map, model)
        self.regex = r'(?:[A-Za-z0-9-_]+?-)?(\d+)(?=$|/)'

    def to_url(self, value):
        if isinstance(value, orm.browse_record):
            [(id, name)] = value.name_get()
        else:
            # assume name_search result tuple
            id, name = value
        return "%s-%d" % (slugify(name), id)

    def generate(self, cr, uid, query=None, context=None):
        return request.registry[self.model].name_search(
            cr, uid, name=query or '', context=context)

class PageConverter(werkzeug.routing.PathConverter):
    """ Only point of this converter is to bundle pages enumeration logic

    Sads got: no way to get the view's human-readable name even if one exists
    """
    def generate(self, cr, uid, query=None, context=None):
        View = request.registry['ir.ui.view']
        views = View.search_read(
            cr, uid, [['page', '=', True]],
            fields=[], order='name', context=context)
        xids = View.get_external_id(
            cr, uid, [view['id'] for view in views], context=context)

        for view in views:
            xid = xids[view['id']]
            if xid and (not query or query in xid):
                yield xid
