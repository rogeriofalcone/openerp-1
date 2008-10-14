# -*- encoding: utf-8 -*-
from osv import fields,osv
import ir
import pooler
import datetime
import time
from tools import config
import netsvc
import ir

class ecommerce_sale_order(osv.osv):

    _name='ecommerce.saleorder'
    _description = 'ecommerce sale order'
    _columns = {
        'name': fields.char('Order Description',size=64, required=True),
        'date_order':fields.date('Date Ordered', required=True),
        'epartner_id':fields.many2one('ecommerce.partner', 'Ecommerce Partner', required=True),
        'epartner_add_id':fields.many2one('ecommerce.partner.address', 'Contact Address'),
        'epartner_shipping_id':fields.many2one('ecommerce.partner.address', 'Shipping Address'),
        'epartner_invoice_id':fields.many2one('ecommerce.partner.address', 'Invoice Address'),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', required=True),
        'web_id':fields.many2one('ecommerce.shop', 'Web Shop', required=True),
        'order_lines': fields.one2many('ecommerce.order.line', 'order_id', 'Order Lines'),
        'order_id': fields.many2one('sale.order', 'Sale Order'),
        'note': fields.text('Notes'),
    }
    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'ecommerce.saleorder'),
        'date_order': lambda *a: time.strftime('%Y-%m-%d'),
        'epartner_invoice_id': lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('ecommerce.partner').address_get(cr, uid, [context['partner_id']], ['invoice'])['invoice'],
        'epartner_add_id': lambda self, cr, uid, context: context.get('partner_id', False) and  self.pool.get('ecommerce.partner').address_get(cr, uid, [context['partner_id']], ['contact'])['contact'],
        'epartner_shipping_id': lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('ecommerce.partner').address_get(cr, uid, [context['partner_id']], ['delivery'])['deliver']
    }
    
    def order_create_function(self, cr, uid, ids, context={}):
       
        get_ids = []
        for order in self.browse(cr, uid, ids, context):
            addid = []  
            if not (order.epartner_id and order.epartner_invoice_id and order.epartner_shipping_id):
                raise osv.except_osv('No addresses !', 'You must assign addresses before creating the order.')
          
            res_prt = self.pool.get('res.partner')
            prt_id = res_prt.search(cr, uid, [('name','=',order.epartner_id.name)])
            res = res_prt.read(cr, uid, prt_id, ['id'], context)
            res_add = self.pool.get('res.partner.address')
            
            if res:
                partner_id = res[0]['id']
                
                prt_add_id =res_add.search(cr,uid,[('partner_id','=',partner_id)])
                res_prt_add = res_add.read(cr,uid,prt_add_id,['id'],context)
                addid = res_prt_add[0]['id']
           
            if not prt_id:     
                partner_id = self.pool.get('res.partner').create(cr, uid, {
                    'name': order.epartner_id.name,
                    'lang':order.epartner_id.lang,
                   })
                order.epartner_id.address
                for addr_type in order.epartner_id.address:
                     addid = self.pool.get('res.partner.address').create(cr, uid, {
                    'name': addr_type.username,
                    'type':addr_type.type,
                    'street':addr_type.street,
                    'street2':addr_type.street2,
                    'partner_id':partner_id,
                    'zip':addr_type.zip,
                    'city':addr_type.city,
                    'state_id':addr_type.state_id.id,
                    'country_id':addr_type.country_id.id,
                    'email':addr_type.email,
                    'phone':addr_type.phone,
                    'fax':addr_type.fax,
                    'mobile':addr_type.mobile,
                })
            data_partner = res_prt.browse(cr,uid,partner_id)
            address_contact = False
            address_invoice = False
            address_delivery = False

            for tmp_addr_var in data_partner.address:
                if tmp_addr_var.type == 'contact':
                    address_contact = tmp_addr_var.id
                  
                if tmp_addr_var.type == 'invoice':
                    address_invoice = tmp_addr_var.id
                   
                if tmp_addr_var.type == 'delivery':
                    address_delivery = tmp_addr_var.id
                 
                if (not address_contact) and (tmp_addr_var.type == 'default'):
                    address_contact = tmp_addr_var.id
                   
                if (not address_invoice) and (tmp_addr_var.type == 'default'):
                    address_invoice = tmp_addr_var.id
                    
                if (not address_delivery) and (tmp_addr_var.type == 'default'):
                     address_delivery = tmp_addr_var.id
           
            if (not address_contact) or (not address_invoice) or (not address_delivery) :
                     raise osv.except_osv('Error','Please Enter Default Address!'); 
               
            pricelist_id=order.pricelist_id.id
            order_lines = []
            for line in order.order_lines:
                val = {
                    'name': line.name,
                    'product_uom_qty': line.product_qty,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom_id.id,
                    'price_unit': line.price_unit,
                }
                val_new = self.pool.get('sale.order.line').product_id_change(cr, uid, None, pricelist_id, line.product_id.id, line.product_qty, line.product_uom_id.id, name=line.name)['value']
                del val_new['price_unit']
                del val_new['th_weight']
                val_new['product_uos'] = 'product_uos' in val_new and val_new['product_uos'] and val_new['product_uos'][0] or False
                val.update( val_new )
                val['tax_id'] = 'tax_id' in val and [(6,0,val['tax_id'])] or False
                order_lines.append((0,0,val))
           
            search_shop_id = self.pool.get('ecommerce.shop').browse(cr, uid, order.web_id.id)
            order_id = self.pool.get('sale.order').create(cr, uid, {
                'name': order.name,
                'shop_id': search_shop_id.shop_id.id,
                'user_id': uid,
                'note': order.note or '',
                'partner_id': partner_id,
                'partner_invoice_id':address_invoice,  
                'partner_order_id':address_contact,  
                'partner_shipping_id':address_delivery,  
                'pricelist_id': order.pricelist_id.id,
                'order_line':order_lines
            })      
            get_ids.extend(ids)
            get_ids.append(order_id)

        return get_ids

    def address_set(self, cr, uid, ids, *args):
        
        done = []
        for order in self.browse(cr, uid, ids):
            for a in [order.epartner_shipping_id.id,order.epartner_invoice_id.id]:
                if a not in done:
                    done.append(a)
                    self.pool.get('ecommerce.partner').address_set(cr, uid, [a] )
            self.write(cr, uid, [order.id], {
                'partner_shipping_id': order.epartner_invoice_id.address_id.id,
                'partner_id': order.epartner_invoice_id.address_id.partner_id.id,
                'partner_invoice_id': order.epartner_shipping_id.address_id.id,
           })
        return True
    
    def onchange_epartner_id(self, cr, uid, ids, part):
    
        if not part:
            return {'value':{'epartner_invoice_id': False, 'epartner_shipping_id':False, 'epartner_add_id':False}}
        addr = self.pool.get('ecommerce.partner').address_get(cr, uid, [part], ['delivery','invoice','contact'])
        return {'value':{'epartner_invoice_id': addr['invoice'], 'epartner_add_id':addr['contact'], 'epartner_shipping_id':addr['delivery']}}
    
    def confirm_sale_order(self, cr, uid, so_ids, email_id, shipping_charge, context={}):
       
        wf_service = netsvc.LocalService("workflow")
        ids = []
        inv_id = []
        datas = {}
        ids.append(so_ids)
        create_wf = self.order_create_function(cr, uid, ids, context={})
        ecom_soid = create_wf[0]
        sale_orderid = create_wf[1]
     
        wf_service.trg_validate(uid, 'sale.order', sale_orderid, 'order_confirm', cr)
        wf_service.trg_validate(uid, 'sale.order', sale_orderid, 'manual_invoice', cr)
        
        get_data = self.pool.get('sale.order').browse(cr,uid,sale_orderid)
        invoice_id = get_data.invoice_ids[0].id
        wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
        inv_id.append(invoice_id)
     
        id = uid
        get_uiddata = self.pool.get('res.users').browse(cr,uid,id)
        
        key = ('dbname', cr.dbname)
        datas = {'model' : 'account.invoice', 'id' : invoice_id, 'report_type': 'pdf'}
     
        obj = netsvc.LocalService('report.'+'account.invoice.ecom')
        context={'price':shipping_charge}
        (result, format) = obj.create(cr, uid, inv_id, datas, context)
    
        subject = str('Send Invoice')
        body =     str('Dear  Subscriber,' + '\n'+'\n' + 
                   'Your Payment Process finish..'+'\n' +
                   'Your invoice send it to you.' + '\n' + '\n' +'\n' +
                   'Thank you for using Ecommerce!' + '\n' +
                   'The Ecommerce Team')

        data = self.pool.get('ecommerce.partner')
        data.ecom_send_email(cr, uid, email_id, subject, body, attachment=result, context={})
        
        return dict(inv_id=invoice_id, so_id=sale_orderid)
   
ecommerce_sale_order()

class ecommerce_order_line(osv.osv):
    _name = 'ecommerce.order.line'
    _description = 'ecommerce order line'
    _columns = {
        'name': fields.char('Order Line', size=64, required=True),
        'order_id': fields.many2one('ecommerce.saleorder', 'eOrder Ref'),
        'product_qty': fields.float('Quantity', digits=(16,2), required=True),
        'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok','=',True)], change_default=True),
        'product_uom_id': fields.many2one('product.uom', 'Unit of Measure',required=True),
        'price_unit': fields.float('Unit Price',digits=(16, int(config['price_accuracy'])), required=True),
    }
   
ecommerce_order_line()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

