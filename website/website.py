# -*- coding: utf-8 -*-
import simplejson

import openerp
from openerp.osv import osv
from openerp.addons.web import http
from openerp.addons.web.controllers import main
from openerp.addons.web.http import request
import urllib
import math


def auth_method_public():
    registry = openerp.modules.registry.RegistryManager.get(request.db)
    if not request.session.uid:
        request.uid = registry['website'].get_public_user().id
    else:
        request.uid = request.session.uid
http.auth_methods['public'] = auth_method_public


def urlplus(url, params):
    if not params:
        return url
    url += "?"
    for k,v in params.items():
        url += "%s=%s&" % (k, urllib.quote_plus(v))
    return url

class website(osv.osv):
    _name = "website" # Avoid website.website convention for conciseness (for new api). Got a special authorization from xmo and rco
    _description = "Website"

    public_user = None

    def get_public_user(self):
        if not self.public_user:
            ref = request.registry['ir.model.data'].get_object_reference(request.cr, openerp.SUPERUSER_ID, 'website', 'public_user')
            self.public_user = request.registry[ref[0]].browse(request.cr, openerp.SUPERUSER_ID, ref[1])
        return self.public_user

    def get_rendering_context(self, additional_values=None):
        debug = 'debug' in request.params
        is_public_user = request.uid == self.get_public_user().id
        values = {
            'debug': debug,
            'is_public_user': is_public_user,
            'editable': not is_public_user,
            'request': request,
            'registry': request.registry,
            'cr': request.cr,
            'uid': request.uid,
            'host_url': request.httprequest.host_url,
            'res_company': request.registry['res.company'].browse(request.cr, openerp.SUPERUSER_ID, 1),
            'json': simplejson,
        }
        if values['editable']:
            values.update({
                'script': "\n".join(['<script type="text/javascript" src="%s"></script>' % i for i in main.manifest_list('js', db=request.db, debug=debug)]),
                'css': "\n".join('<link rel="stylesheet" href="%s">' % i for i in main.manifest_list('css', db=request.db, debug=debug))
            })
        if additional_values:
            values.update(additional_values)
        return values

    def render(self, template, values={}):
        context = {
            'inherit_branding': values.get('editable', False),
        }
        return request.registry.get("ir.ui.view").render(request.cr, request.uid, template, values, context=context)

    def pager(self, url, total, page=1, step=30, scope=5):
        # Compute Pager
        d = {}
        d["page_count"] = int(math.ceil(total / step))

        page = max(1, min(int(page), d["page_count"]))

        d["offset"] = (page-1) * step
        scope -= 1

        pmin = max(page - int(math.floor(scope/2)), 1)
        pmax = min(pmin + scope, d["page_count"])

        if pmax - pmin < scope:
            pmin = pmax - scope > 0 and pmax - scope or 1


        d["page"] = {'url': "%spage/%s/" % (url, page), 'num': page}
        d["page_start"] = {'url': "%spage/%s/" % (url, pmin), 'num': pmin}
        d["page_end"] = {'url': "%spage/%s/" % (url, min(pmax, page+1)), 'num': min(pmax, page+1)}
        d["pages"] = []
        for page in range(pmin, pmax+1):
            d["pages"].append({'url': "%spage/%s/" % (url, page), 'num': page})

        return d