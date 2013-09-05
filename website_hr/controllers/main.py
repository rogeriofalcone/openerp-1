# -*- coding: utf-8 -*-

from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.website import website

class website_hr(http.Controller):

    @website.route(['/page/website.aboutus'], type='http', auth="public")
    def blog(self, **post):
        hr_obj = request.registry['hr.employee']
        employee_ids = hr_obj.search(request.cr, request.uid, [(1, "=", 1)],
                                     context=request.context)
        values = {
            'employee_ids': hr_obj.browse(request.cr, request.uid, employee_ids,
                                          request.context)
        }
        return request.webcontext.render("website.aboutus", values)
