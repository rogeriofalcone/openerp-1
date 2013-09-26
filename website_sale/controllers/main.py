# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import osv
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.website import website
import random
import werkzeug
import simplejson

def get_order(order_id=None):
    order_obj = request.registry.get('sale.order')
    # check if order allready exists
    context = {}
    if order_id:
        try:
            order = order_obj.browse(request.cr, SUPERUSER_ID, order_id, request.context)
            order.pricelist_id
        except:
            order_id = None
    if not order_id:
        fields = [k for k, v in order_obj._columns.items()]
        order_value = order_obj.default_get(request.cr, SUPERUSER_ID, fields, request.context)
        if request.httprequest.session.get('ecommerce_pricelist'):
            order_value['pricelist_id'] = request.httprequest.session['ecommerce_pricelist']
        order_value['partner_id'] = request.registry.get('res.users').browse(request.cr, SUPERUSER_ID, request.uid, request.context).partner_id.id
        order_value.update(order_obj.onchange_partner_id(request.cr, SUPERUSER_ID, [], order_value['partner_id'], context=request.context)['value'])
        order_id = order_obj.create(request.cr, SUPERUSER_ID, order_value, request.context)
        order = order_obj.browse(request.cr, SUPERUSER_ID, order_id, request.context)
        request.httprequest.session['ecommerce_order_id'] = order.id

    return order_obj.browse(request.cr, SUPERUSER_ID, order_id,
                            context=dict(request.context, pricelist=order.pricelist_id.id))

def get_current_order():
    if request.httprequest.session.get('ecommerce_order_id'):
        return get_order(request.httprequest.session.get('ecommerce_order_id'))
    else:
        return False

class Website(osv.osv):
    _inherit = "website"
    def preprocess_request(self, cr, uid, ids, *args, **kwargs):
        request.context.update({
            'website_sale_order': get_current_order(),
        })
        return super(Website, self).preprocess_request(cr, uid, ids, *args, **kwargs)

class Ecommerce(http.Controller):

    def get_categories(self):
        domain = [('parent_id', '=', False)]

        category_obj = request.registry.get('product.public.category')
        category_ids = category_obj.search(request.cr, SUPERUSER_ID, domain, context=request.context)
        categories = category_obj.browse(request.cr, SUPERUSER_ID, category_ids, context=request.context)

        product_obj = request.registry.get('product.product')
        groups = product_obj.read_group(request.cr, SUPERUSER_ID, [("sale_ok", "=", True), ('website_published', '=', True)], ['public_categ_id'], 'public_categ_id', context=request.context)
        full_category_ids = [group['public_categ_id'][0] for group in groups if group['public_categ_id']]

        for cat_id in category_obj.browse(request.cr, SUPERUSER_ID, full_category_ids, context=request.context):
            while cat_id.parent_id:
                cat_id = cat_id.parent_id
                full_category_ids.append(cat_id.id)
        full_category_ids.append(1)

        return (categories, full_category_ids)

    def get_bin_packing_products(self, product_ids, fill_hole, col_number=4):
        """
        Packing all products of the search into a table of #col_number columns in function of the product sizes
        The size datas of website_style_ids is use for fill table (default 1x1)
        The other website_style_ids datas are concatenate in a html class

        @values:

        product_ids: list of product template
        fill_hole: list of extra product template use to fill the holes
        col_number: number of columns

        @return:

        table (list of list of #col_number items)
        items: {
            'product': browse of product template,
            'x': size x,
            'y': size y,
            'class': html class
        }
        """
        product_obj = request.registry.get('product.template')
        data_obj = request.registry.get('ir.model.data')

        product_ids = product_obj.search(request.cr, request.uid, [("id", 'in', product_ids)], context=request.context)

        size_ids = {}
        data_domain = [('model', '=', 'website.product.style'), ('name', 'like', 'size%')]
        data_ids = data_obj.search(request.cr, SUPERUSER_ID, data_domain, context=request.context)
        for data in data_obj.read(request.cr, SUPERUSER_ID, data_ids, ['name', 'res_id'], context=request.context):
            size_ids[data['res_id']] = [int(data['name'][-3]), int(data['name'][-1])]

        product_list = []
        bin_packing = {}
        bin_packing[0] = {}

        for product in product_obj.browse(request.cr, SUPERUSER_ID, product_ids, context=request.context):
            index = len(product_list)

            # get size and all html classes
            _class = ""
            x = 1
            y = 1
            for style_id in product.website_style_ids:
                if style_id.id in size_ids:
                    size = size_ids[style_id.id]
                    x = size[0]
                    y = size[1]
                elif style_id.html_class:
                    _class += " " + style_id.html_class
            product_list.append({'product': product, 'x': x, 'y': y, 'class': _class })

            # bin packing products
            insert = False
            line = 0
            while not insert:
                # if not full column get next line
                if len(bin_packing.setdefault(line, {})) >= col_number:
                    line += 1
                    continue

                col = 0
                while col < col_number:
                    if bin_packing[line].get(col, None) != None:
                        col += 1
                        continue

                    insert = True

                    # check if the box can be inserted
                    copy_line = line
                    copy_y = y
                    while copy_y > 0:
                        copy_col = col
                        copy_x = x
                        while copy_x > 0:
                            if copy_col >= col_number or bin_packing.setdefault(copy_line, {}).get(copy_col, None) != None:
                                insert = False
                                break
                            copy_col += 1
                            copy_x -= 1
                        if not insert:
                            break
                        copy_line += 1
                        copy_y -= 1

                    if not insert:
                        col += 1
                        continue

                    # insert the box
                    copy_y = y
                    while copy_y > 0:
                        copy_y -= 1
                        copy_x = x
                        while copy_x > 0:
                            copy_x -= 1
                            bin_packing[line + copy_y][col + copy_x] = False
                    bin_packing[line + copy_y][col + copy_x] = product_list[index]
                    break
            
                if not insert:
                    line += 1
                else:
                    break

        length = len(bin_packing)

        # browse product to fill the holes
        if fill_hole:
            fill_hole_products = []
            fill_hole = product_obj.search(request.cr, request.uid, [("id", 'in', fill_hole)], context=request.context)
            for product in product_obj.browse(request.cr, SUPERUSER_ID, fill_hole, context=request.context):
                fill_hole_products.append(product)
            fill_hole_products.reverse()

        # packaging in list (from dict)
        bin_packing_list = []
        line = 0
        while line < length:
            bin_packing_list.append([])
            col = 0
            while col < col_number:
                if fill_hole and fill_hole_products and bin_packing[line].get(col) == None:
                    bin_packing[line][col] = {'product': fill_hole_products.pop(), 'x': 1, 'y': 1, 'class': _class }
                bin_packing_list[line].append(bin_packing[line].get(col))
                col += 1
            line += 1

        return bin_packing_list

    def get_products(self, product_ids):
        product_obj = request.registry.get('product.template')
        product_ids = product_obj.search(request.cr, request.uid, [("id", 'in', product_ids)], context=request.context)
        return product_obj.browse(request.cr, SUPERUSER_ID, product_ids, context=request.context)

    @website.route(['/shop/', '/shop/category/<cat_id>/', '/shop/category/<cat_id>/page/<int:page>/', '/shop/page/<int:page>/'], type='http', auth="public")
    def category(self, cat_id=0, page=0, **post):

        if 'promo' in post:
            self.change_pricelist(post.get('promo'))
        product_obj = request.registry.get('product.template')

        domain = [("sale_ok", "=", True)]
        #domain += [('website_published', '=', True)]

        if post.get("search"):
            domain += ['|', '|', '|',
                ('name', 'ilike', "%%%s%%" % post.get("search")), 
                ('description', 'ilike', "%%%s%%" % post.get("search")),
                ('website_description', 'ilike', "%%%s%%" % post.get("search")),
                ('product_variant_ids.public_categ_id.name', 'ilike', "%%%s%%" % post.get("search"))]
        if cat_id:
            cat_id = int(cat_id)
            domain += [('product_variant_ids.public_categ_id.id', 'child_of', cat_id)] + domain

        step = 20
        product_count = len(product_obj.search(request.cr, request.uid, domain, context=request.context))
        pager = request.website.pager(url="/shop/category/%s/" % cat_id, total=product_count, page=page, step=step, scope=7, url_args=post)

        request.context['pricelist'] = self.get_pricelist()
        
        product_ids = product_obj.search(request.cr, request.uid, domain, limit=step, offset=pager['offset'], context=request.context)
        fill_hole = product_obj.search(request.cr, request.uid, domain, limit=step, offset=pager['offset']+step, context=request.context)

        values = {
            'get_categories': self.get_categories,
            'category_id': cat_id,
            'product_ids': product_ids,
            'product_ids_for_holes': fill_hole,
            'get_bin_packing_products': self.get_bin_packing_products,
            'get_products': self.get_products,
            'search': post.get("search"),
            'pager': pager,
        }
        return request.website.render("website_sale.products", values)

    @website.route(['/shop/product/<product_id>/'], type='http', auth="public")
    def product(self, cat_id=0, product_id=0, **post):

        if 'promo' in post:
            self.change_pricelist(post.get('promo'))

        product_id = product_id and int(product_id) or 0
        product_obj = request.registry.get('product.template')
        category_obj = request.registry.get('product.public.category')

        category_ids = category_obj.search(request.cr, request.uid, [(1, '=', 1)], context=request.context)
        category_list = category_obj.name_get(request.cr, request.uid, category_ids, request.context)
        category_list = sorted(category_list, key=lambda category: category[1])

        request.context['pricelist'] = self.get_pricelist()

        category = None
        if post.get('category_id') and int(post.get('category_id')):
            category = category_obj.browse(request.cr, request.uid, int(post.get('category_id')), context=request.context)

        product = product_obj.browse(request.cr, request.uid, product_id, context=request.context)
        values = {
            'category_id': post.get('category_id') and int(post.get('category_id')) or None,
            'category': category,
            'search': post.get("search"),
            'get_categories': self.get_categories,
            'category_list': category_list,
            'product': product,
        }
        return request.website.render("website_sale.product", values)

    @website.route(['/shop/add_product/', '/shop/category/<cat_id>/add_product/'], type='http', auth="public")
    def add_product(self, cat_id=0, **post):
        product_id = request.registry.get('product.product').create(request.cr, request.uid, 
            {'name': 'New Product', 'public_categ_id': cat_id}, request.context)
        return werkzeug.utils.redirect("/shop/product/%s/?unable_editor=1" % product_id)

    @website.route(['/shop/change_category/<product_id>/'], type='http', auth="public")
    def edit_product(self, product_id=0, **post):
        request.registry.get('product.template').write(
            request.cr, request.uid, [int(product_id)],
            {'public_categ_id': int(post.get('public_categ_id', 0))}, request.context)
        return "1"

    def get_pricelist(self):
        if not request.httprequest.session.get('ecommerce_pricelist'):
            self.change_pricelist(None)
        return request.httprequest.session.get('ecommerce_pricelist')

    def change_pricelist(self, code):
        request.httprequest.session.setdefault('ecommerce_pricelist', False)

        pricelist_id = False
        if code:
            pricelist_obj = request.registry.get('product.pricelist')
            pricelist_ids = pricelist_obj.search(request.cr, SUPERUSER_ID, [('code', '=', code)], context=request.context)
            if pricelist_ids:
                pricelist_id = pricelist_ids[0]

        if not pricelist_id:
            partner_id = request.registry.get('res.users').browse(request.cr, SUPERUSER_ID, request.uid, request.context).partner_id.id
            pricelist_id = request.registry['sale.order'].onchange_partner_id(request.cr, SUPERUSER_ID, [], partner_id, context=request.context)['value']['pricelist_id']
        
        request.httprequest.session['ecommerce_pricelist'] = pricelist_id

        order = get_current_order()
        if order:
            values = {'pricelist_id': pricelist_id}
            values.update(order.onchange_pricelist_id(pricelist_id, None)['value'])
            order.write(values)
            for line in order.order_line:
                self.add_product_to_cart(order_line_id=line.id, number=0)

    def add_product_to_cart(self, product_id=0, order_line_id=0, number=1, set_number=-1):
        order_line_obj = request.registry.get('sale.order.line')

        product_id = product_id and int(product_id) or 0

        order = get_current_order()
        if not order:
            order = get_order()

        context = dict(request.context, pricelist=self.get_pricelist())

        quantity = 0

        # values initialisation
        values = {}

        domain = [('order_id', '=', order.id)]
        if order_line_id:
            domain += [('id', '=', order_line_id)]
        else:
            domain += [('product_id', '=', product_id)]

        order_line_ids = order_line_obj.search(request.cr, SUPERUSER_ID, domain, context=context)
        if order_line_ids:
            order_line = order_line_obj.read(request.cr, SUPERUSER_ID, order_line_ids, [], context=context)[0]
            if not product_id:
                product_id = order_line['product_id'][0]
            if set_number >= 0:
                quantity = set_number
            else:
                quantity = order_line['product_uom_qty'] + number
            if quantity < 0:
                quantity = 0
        else:
            fields = [k for k, v in order_line_obj._columns.items()]
            values = order_line_obj.default_get(request.cr, SUPERUSER_ID, fields, context=context)
            quantity = 1

        # change and record value
        vals = order_line_obj._recalculate_product_values(request.cr, request.uid, order_line_ids, product_id, context=context)
        values.update(vals)

        values['product_uom_qty'] = quantity
        values['product_id'] = product_id
        values['order_id'] = order.id

        if order_line_ids:
            order_line_obj.write(request.cr, SUPERUSER_ID, order_line_ids, values, context=context)
            if not quantity:
                order_line_obj.unlink(request.cr, SUPERUSER_ID, order_line_ids, context=context)
        else:
            order_line_id = order_line_obj.create(request.cr, SUPERUSER_ID, values, context=context)
            order.write({'order_line': [(4, order_line_id)]}, context=context)

        return [quantity, order.get_total_quantity()]

    @website.route(['/shop/mycart/'], type='http', auth="public")
    def mycart(self, **post):
        order = get_current_order()
        prod_obj = request.registry.get('product.product')

        if 'promo' in post:
            self.change_pricelist(post.get('promo'))

        suggested_ids = []
        if order:
            for line in order.order_line:
                suggested_ids += [p.id for p in line.product_id and line.product_id.suggested_product_ids or [] for line in order.order_line]
        suggested_ids = prod_obj.search(request.cr, request.uid, [('id', 'in', suggested_ids)], context=request.context)

        # select 3 random products
        suggested_products = []
        while len(suggested_products) < 3 and suggested_ids:
            index = random.randrange(0, len(suggested_ids))
            suggested_products.append(suggested_ids.pop(index))

        values = {
            'get_categories': self.get_categories,
            'suggested_products': prod_obj.browse(request.cr, request.uid, suggested_products, request.context),
        }
        return request.website.render("website_sale.mycart", values)

    @website.route(['/shop/<path:path>/add_cart/', '/shop/add_cart/'], type='http', auth="public")
    def add_cart(self, path=None, product_id=None, order_line_id=None, remove=None, json=None):
        quantity = self.add_product_to_cart(product_id=product_id, order_line_id=order_line_id, number=(remove and -1 or 1))
        if json:
            return simplejson.dumps(quantity)
        if path:
            return werkzeug.utils.redirect("/shop/%s/" % path)
        else:
            return werkzeug.utils.redirect("/shop/")

    @website.route(['/shop/remove_cart/', '/shop/<path:path>/remove_cart/'], type='http', auth="public")
    def remove_cart(self, path=None, product_id=None, order_line_id=None, json=None):
        return self.add_cart(product_id=product_id, order_line_id=order_line_id, path=path, remove=True, json=json)

    @website.route(['/shop/set_cart/', '/shop/<path:path>/set_cart/'], type='http', auth="public")
    def set_cart(self, path=None, product_id=None, order_line_id=None, set_number=0, json=None):
        quantity = self.add_product_to_cart(product_id=product_id, order_line_id=order_line_id, set_number=set_number)
        if json:
            return simplejson.dumps(quantity)
        if path:
            return werkzeug.utils.redirect("/shop/%s/" % path)
        else:
            return werkzeug.utils.redirect("/shop/")

    @website.route(['/shop/checkout/'], type='http', auth="public")
    def checkout(self, **post):
        classic_fields = ["name", "phone", "fax", "email", "street", "city", "state_id", "zip"]
        rel_fields = ['country_id', 'state_id']

        order = get_current_order()

        if not order or order.state != 'draft' or not order.order_line:
            return self.mycart(**post)

        partner_obj = request.registry.get('res.partner')
        user_obj = request.registry.get('res.users')
        country_obj = request.registry.get('res.country')
        country_state_obj = request.registry.get('res.country.state')

        values = {
            'shipping': post.get("shipping"),
            'error': post.get("error") and dict.fromkeys(post.get("error").split(","), 'error') or {}
        }

        checkout = dict((field_name, '') for field_name in classic_fields + rel_fields)
        if not request.context['is_public_user']:
            partner = user_obj.browse(request.cr, request.uid, request.uid, request.context).partner_id
            checkout.update(dict((field_name, getattr(partner, field_name)) for field_name in classic_fields if getattr(partner, field_name)))
            checkout['state_id'] = partner.state_id and partner.state_id.id or ''
            checkout['country_id'] = partner.country_id and partner.country_id.id or ''
            checkout['company'] = partner.parent_id and partner.parent_id.name or ''

            shipping_ids = partner_obj.search(request.cr, request.uid, [("parent_id", "=", partner.id), ('type', "=", 'delivery')], context=request.context)
            if shipping_ids:
                for k, v in partner_obj.read(request.cr, request.uid, shipping_ids[0], request.context).items():
                    checkout['shipping_'+k] = v or ''

        values['checkout'] = checkout
        countries_ids = country_obj.search(request.cr, SUPERUSER_ID, [(1, "=", 1)], context=request.context)
        values['countries'] = country_obj.browse(request.cr, SUPERUSER_ID, countries_ids, request.context)
        states_ids = country_state_obj.search(request.cr, SUPERUSER_ID, [(1, "=", 1)], context=request.context)
        values['states'] = country_state_obj.browse(request.cr, SUPERUSER_ID, states_ids, request.context)

        return request.website.render("website_sale.checkout", values)

    @website.route(['/shop/confirm_order/'], type='http', auth="public")
    def confirm_order(self, **post):
        order = get_current_order()

        error = []
        partner_obj = request.registry.get('res.partner')
        user_obj = request.registry.get('res.users')

        if order.state != 'draft':
            return werkzeug.utils.redirect("/shop/checkout/")
        if not order.order_line:
            error.append("empty_cart")
            return werkzeug.utils.redirect("/shop/checkout/")

        # check values
        request.session['checkout'] = post
        required_field = ['phone', 'zip', 'email', 'street', 'city', 'name', 'country_id']
        for key in required_field:
            if not post.get(key):
                error.append(key)
            if post.get('shipping_different') and key != 'email' and not post.get("shipping_%s" % key):
                error.append("shipping_%s" % key)
        if error:
            return werkzeug.utils.redirect("/shop/checkout/?error=%s&shipping=%s" % (",".join(error), post.get('shipping_different') and 'on' or ''))

        # search or create company
        company_id = None
        if post['company']:
            company_ids = partner_obj.search(request.cr, SUPERUSER_ID, [("name", "ilike", post['company']), ('is_company', '=', True)], context=request.context)
            company_id = company_ids and company_ids[0] or None
            if not company_id:
                company_id = partner_obj.create(request.cr, SUPERUSER_ID, {'name': post['company'], 'is_company': True}, request.context)

        partner_value = {
            'fax': post['fax'],
            'phone': post['phone'],
            'zip': post['zip'],
            'email': post['email'],
            'street': post['street'],
            'city': post['city'],
            'name': post['name'],
            'parent_id': company_id,
            'country_id': post['country_id'],
            'state_id': post['state_id'],
        }
        if not request.context['is_public_user']:
            partner_id = user_obj.browse(request.cr, request.uid, request.uid, request.context).partner_id.id
            partner_obj.write(request.cr, request.uid, [partner_id], partner_value, request.context)
        else:
            partner_id = partner_obj.create(request.cr, SUPERUSER_ID, partner_value, request.context)

        shipping_id = None
        if post.get('shipping_different'):
            shipping_value = {
                'fax': post['shipping_fax'],
                'phone': post['shipping_phone'],
                'zip': post['shipping_zip'],
                'street': post['shipping_street'],
                'city': post['shipping_city'],
                'name': post['shipping_name'],
                'type': 'delivery',
                'parent_id': partner_id,
                'country_id': post['shipping_country_id'],
                'state_id': post['shipping_state_id'],
            }
            domain = [(key, '_id' in key and '=' or 'ilike', '_id' in key and value and int(value) or False)
                for key, value in shipping_value.items() if key in required_field + ["type", "parent_id"]]

            shipping_ids = partner_obj.search(request.cr, SUPERUSER_ID, domain, context=request.context)
            if shipping_ids:
                shipping_id = shipping_ids[0]
                partner_obj.write(request.cr, SUPERUSER_ID, [shipping_id], shipping_value, request.context)
            else:
                shipping_id = partner_obj.create(request.cr, SUPERUSER_ID, shipping_value, request.context)

        order_value = {
            'partner_id': partner_id,
            'partner_invoice_id': partner_id,
            'partner_shipping_id': shipping_id or partner_id
        }
        order_value.update(request.registry.get('sale.order').onchange_partner_id(request.cr, SUPERUSER_ID, [], order.partner_id.id, context=request.context)['value'])
        order.write(order_value)

        return werkzeug.utils.redirect("/shop/payment/")

    @website.route(['/shop/payment/'], type='http', auth="public")
    def payment(self, **post):
        order = get_current_order()

        if not order or not order.order_line:
            return self.mycart(**post)

        values = {
            'partner': False,
            'order': order
        }

        payment_obj = request.registry.get('portal.payment.acquirer')
        payment_ids = payment_obj.search(request.cr, SUPERUSER_ID, [('visible', '=', True)], context=request.context)
        values['payments'] = payment_obj.browse(request.cr, SUPERUSER_ID, payment_ids, request.context)
        for payment in values['payments']:
            content = payment_obj.render(request.cr, SUPERUSER_ID, payment.id, order, order.name, order.pricelist_id.currency_id, order.amount_total)
            payment._content = content

        return request.website.render("website_sale.payment", values)

    @website.route(['/shop/payment_validate/'], type='http', auth="public")
    def payment_validate(self, **post):
        request.httprequest.session['ecommerce_order_id'] = False
        request.httprequest.session['ecommerce_pricelist'] = False
        return werkzeug.utils.redirect("/shop/")

# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4:
