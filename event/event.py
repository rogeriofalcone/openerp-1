# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import fields, osv
import time
import netsvc
import pooler
import tools

class crm_case_log(osv.osv):
    _inherit = 'crm.case.log'
    _description = 'crm.case.log'
    def create(self, cr, uid, vals, *args, **kwargs):
            if not 'name' in vals:
                vals['name']='Historize'
            return super(osv.osv,self).create(cr, uid, vals, *args, **kwargs)
    _defaults = {
        'user_id': lambda self,cr,uid,context: uid,
    }
crm_case_log()

class one2many_mod_task(fields.one2many):
    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
        if not context:
            context = {}
        if not values:
                values = {}
        res = {}
        for id in ids:
            res[id] = []
        for id in ids:
            query = "select project_id from event_event where id = %i" %id
            cr.execute(query)
            project_ids = [ x[0] for x in cr.fetchall()]
            ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',project_ids),('state','<>','done')], limit=self._limit)
            for r in obj.pool.get(self._obj)._read_flat(cr, user, ids2, [self._fields_id], context=context, load='_classic_write'):
                res[id].append( r['id'] )
        return res

class event_type(osv.osv):
    _name = 'event.type'
    _description= 'Event type'
    _columns = {
        'name': fields.char('Event type', size=64, required=True),
    }
event_type()

class event(osv.osv):
    _name = 'event.event'
    _description = 'Event'
    _inherits = {'crm.case.section': 'section_id'}
    _order = 'date_begin'

    def copy(self, cr, uid, id, default=None, context=None):
        return super(event, self).copy(cr, uid,id, default={'code': self.pool.get('ir.sequence').get(cr, uid, 'event.event'),})

    def button_draft(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'draft'})
    def button_cancel(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'cancel'})
    def button_done(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'done'})
    def button_confirm(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'confirm'})

    def _get_register(self, cr, uid, ids, name, args, context=None):
        res={}
        for event in self.browse(cr, uid, ids, context):
            query = """select sum(nb_register) from crm_case c left join crm_case_section s on (c.section_id=s.id) right join event_event e on (e.section_id=s.id) right join event_registration r on (r.case_id=c.id) where e.section_id = %s and c.state in ('open','done')""" % event.section_id.id
            cr.execute(query)
            res2 = cr.fetchone()
            if res2 and res2[0]:
                res[event.id] = res2[0]
            else:
                res[event.id] = 0
        return res

    def _get_prospect(self, cr, uid, ids, name, args, context=None):
        res={}
        for event in self.browse(cr, uid, ids, context):
            query = """select sum(nb_register) from crm_case c left join crm_case_section s on (c.section_id=s.id) right join event_event e on (e.section_id=s.id) right join event_registration r on (r.case_id=c.id) where e.section_id = %s and c.state = 'draft'""" % event.section_id.id
            cr.execute(query)
            res2 = cr.fetchone()
            if res2 and res2[0]:
                res[event.id] = res2[0]
            else:
                res[event.id] = 0
        return res

    def write(self, cr, uid, ids,vals, *args, **kwargs):
        res = super(event,self).write(cr, uid, ids,vals, *args, **kwargs)
        if 'date_begin' in vals and vals['date_begin']:
            data_event = self.browse(cr, uid, ids)
            for eve in data_event:
                if eve.project_id:
                    self.pool.get('project.project').write(cr, uid, [eve.project_id.id], {'date_end':eve.date_begin})
        return res

    _columns = {
        'type': fields.many2one('event.type', 'Type'),
        'section_id': fields.many2one('crm.case.section', 'Case section', required=True),
        'register_max': fields.integer('Maximum Registrations'),
        'register_min': fields.integer('Minimum Registrations'),
        'register_current': fields.function(_get_register, method=True, string='Confirmed Registrations'),
        'register_prospect': fields.function(_get_prospect, method=True, string='Unconfirmed Registrations'),
        'project_id': fields.many2one('project.project', 'Project', readonly=True),
        'task_ids': one2many_mod_task('project.task', 'project_id', "Project tasks", readonly=True, domain="[('state','&lt;&gt;', 'done')]"),
        'date_begin': fields.datetime('Beginning date', required=True),
        'date_end': fields.datetime('Ending date', required=True),
        'state': fields.selection([('draft','Draft'),('confirm','Confirmed'),('done','Done'),('cancel','Canceled')], 'Status', readonly=True, required=True),
        'mail_auto_registr':fields.boolean('Mail Auto Register',help='A mail is sent when the registration is confirmed'),
        'mail_auto_confirm':fields.boolean('Mail Auto Confirm',help='A mail is sent when the event is confimed'),
        'mail_registr':fields.text('Mail Register',help='Template for the mail'),
        'mail_confirm':fields.text('Mail Confirm',help='Template for the mail'),
        'budget_id':fields.many2one('account.budget.post','Budget'),
        'product_id':fields.many2one('product.product','Product'),
    }
    _defaults = {
        'state': lambda *args: 'draft',
        'code': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'event.event'),
        'user_id': lambda self,cr,uid,ctx: uid,
    }
event()

class event_registration(osv.osv):

    def _history(self, cr, uid,ids,keyword, history=False, email=False, context={}):
        for case in ids:
            data = {
                'name': keyword,
                'som': case.som.id,
                'canal_id': case.canal_id.id,
                'user_id': uid,
                'case_id': case.case_id.id
            }
            obj = self.pool.get('crm.case.log')
            obj.create(cr, uid, data, context)
        return True

    def button_reg_close(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'done',})
        cases = self.browse(cr, uid, ids)
        self._history(cr, uid, cases, 'Done', history=True)
        return True

    def button_reg_cancel(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'cancel',})
        cases = self.browse(cr, uid, ids)
        self._history(cr, uid, cases, 'Cancel', history=True)
        return True

    def create(self, cr, uid, *args, **argv):
        args[0]['section_id']= self.pool.get('event.event').browse(cr, uid, args[0]['event_id'], None).section_id.id
        res = super(event_registration, self).create(cr, uid, *args, **argv)
        self._history(cr, uid,self.browse(cr, uid, [res]), 'Created', history=True)
        return res

    def write(self, cr, uid, *args, **argv):
        if 'event_id' in args[1]:
            args[1]['section_id']= self.pool.get('event.event').browse(cr, uid, args[1]['event_id'], None).section_id.id
        return super(event_registration, self).write(cr, uid, *args, **argv)

    def mail_user(self,cr,uid,ids):
        src=tools.config.options['smtp_user']
        reg_ids=self.browse(cr,uid,ids)
        for reg_id in reg_ids:
            dest=reg_id.email_from
            if (reg_id.event_id.state in ['confirm','running']) and reg_id.event_id.mail_auto_confirm:
                if dest:
                    tools.email_send(src,[dest],'Auto Confirmation: '+'['+str(reg_id.id)+']'+' '+reg_id.name,reg_id.event_id.mail_confirm)
                    return True
            # Sending another mail
            if reg_id.event_id.state in ['draft', 'fixed', 'open','confirm','running'] and reg_id.event_id.mail_auto_registr:
                if dest:
                    tools.email_send(src,[dest],'Auto Registration: '+'['+str(reg_id.id)+']'+' '+reg_id.name,reg_id.event_id.mail_registr)
                    return True
        return False

    _name= 'event.registration'
    _description = 'Event Registration'
    _inherits = {'crm.case': 'case_id'}
    _columns = {
        'case_id':fields.many2one('crm.case','Case'),
        'nb_register': fields.integer('Number of Registration', readonly=True, states={'draft':[('readonly',False)]}),
        "partner_order_id":fields.many2one('res.partner','Partner Order'),
        'event_id':fields.many2one('event.event', 'Event Related', required=True),
        "partner_invoice_id":fields.many2one('res.partner', 'Partner Invoice'),
        "unit_price": fields.float('Unit Price'),
        "badge_title":fields.char('Badge Title',size=128),
        "badge_name":fields.char('Badge Name',size=128),
        "badge_partner":fields.char('Badge Partner',size=128),
        "invoice_label":fields.char("Label Invoice",size=128,required=True),
        "tobe_invoiced":fields.boolean("To be Invoiced"),
        "invoice_id":fields.many2one("account.invoice","Invoice"),
    }
    _defaults = {
        'nb_register': lambda *a: 1,
        'tobe_invoiced' : lambda *a: True,
        'name': lambda *a: 'Registration'
    }

    def onchange_badge_name(self, cr, uid, ids, badge_name):
        data ={}
        if not badge_name:
            return data
        data['name'] = 'Registration: ' + badge_name
        return {'value':data}

    def onchange_contact_id(self, cr, uid, ids, contact_id):
        data ={}
        if not contact_id:
            return data
        obj_addr=self.pool.get('res.partner.address').browse(cr, uid, contact_id)
        data['email_from'] = obj_addr.email

        if obj_addr.contact_id:
            data['badge_name']=obj_addr.contact_id.name
            data['badge_title']=obj_addr.contact_id.title
            d=self.onchange_badge_name(cr, uid, ids,data['badge_name'])
            data.update(d['value'])

        return {'value':data}

    def onchange_event(self, cr, uid, ids, event_id, partner_invoice_id):
        context={}
        if not event_id:
            return {'value':{'unit_price' : False ,'invoice_label' : False }}
        data_event =  self.pool.get('event.event').browse(cr,uid,event_id)
        if data_event.product_id:
            if not partner_invoice_id:
                unit_price=self.pool.get('product.product').price_get(cr, uid, [data_event.product_id.id],context=context)[data_event.product_id.id]
                return {'value':{'unit_price' : unit_price , 'invoice_label' : data_event.product_id.name}}
            data_partner = self.pool.get('res.partner').browse(cr,uid,partner_invoice_id)
            context.update({'partner_id':data_partner})
            unit_price = self.pool.get('product.product')._product_price(cr, uid, [data_event.product_id.id], False, False, {'pricelist':data_partner.property_product_pricelist.id})[data_event.product_id.id]
            return {'value':{'unit_price' :unit_price , 'invoice_label' : data_event.product_id.name}}
        return {'value':{'unit_price' : False,'invoice_label' : False}}


    def onchange_partner_id(self, cr, uid, ids, part, event_id, email=False):#override function for partner name.
        data={}
        data['badge_partner']=data['partner_address_id']=data['partner_invoice_id']=data['email_from']=data['badge_title']=data['badge_name']=False
        if not part:
            return {'value':data}

        data['partner_invoice_id']=part
        # this calls onchange_partner_invoice_id
        d=self.onchange_partner_invoice_id(cr, uid, ids, event_id,part)
        # this updates the dictionary
        data.update(d['value'])
        addr = self.pool.get('res.partner').address_get(cr, uid, [part], ['contact'])
        data['partner_address_id']=addr['contact']
        if addr['contact']:
            d=self.onchange_contact_id(cr, uid, ids,addr['contact'])
            data.update(d['value'])
        partner_data=self.pool.get('res.partner').browse(cr, uid, part)
        data['badge_partner']=partner_data.name
        return {'value':data}

    def onchange_partner_invoice_id(self, cr, uid, ids, event_id, partner_invoice_id):
        data={}
        context={}
        data['unit_price']=False
        if not event_id:
            return {'value':data}
        data_event =  self.pool.get('event.event').browse(cr,uid,event_id)

        if data_event.product_id:
            if not partner_invoice_id:
                data['unit_price']=self.pool.get('product.product').price_get(cr, uid, [data_event.product_id.id],context=context)[data_event.product_id.id]
                return {'value':data}
            data_partner = self.pool.get('res.partner').browse(cr,uid,partner_invoice_id)
            context.update({'partner_id':data_partner})
            data['unit_price'] = self.pool.get('product.product')._product_price(cr, uid, [data_event.product_id.id], False, False, {'pricelist':data_partner.property_product_pricelist.id})[data_event.product_id.id]
            return {'value':data}
        return {'value':data}

    def onchange_categ_id(self, cr, uid, ids, categ, context={}):
        if not categ:
            return {'value':{}}
        cat = self.pool.get('crm.case.categ').browse(cr, uid, categ, context).probability
        return {'value':{'probability':cat}}

    def _map_ids(self,method,cr, uid, ids, *args, **argv):
        case_data = self.browse(cr,uid,ids)
        new_ids=[]
        for case in case_data:
            new_ids.append(case.case_id.id)
        return getattr(self.pool.get('crm.case'),method)(cr, uid, new_ids, *args, **argv)


    def case_close(self,cr, uid, ids, *args, **argv):
        return self._map_ids('case_close',cr,uid,ids,*args,**argv)
    def case_escalate(self,cr, uid, ids, *args, **argv):
        return self._map_ids('case_escalate',cr,uid,ids,*args,**argv)
    def case_open(self,cr, uid, ids, *args, **argv):
        return self._map_ids('case_open',cr,uid,ids,*args,**argv)
    def case_cancel(self,cr, uid, ids, *args, **argv):
        return self._map_ids('case_cancel',cr,uid,ids,*args,**argv)
    def case_pending(self,cr, uid, ids, *args, **argv):
        return self._map_ids('case_pending',cr,uid,ids,*args,**argv)
    def case_reset(self,cr, uid, ids, *args, **argv):
        return self._map_ids('case_reset',cr,uid,ids,*args,**argv)
    def case_log(self,cr, uid, ids, *args, **argv):
        return self._map_ids('case_log',cr,uid,ids,*args,**argv)
    def case_log_reply(self,cr, uid, ids, *args, **argv):
        return self._map_ids('case_log_reply',cr,uid,ids,*args,**argv)
    def add_reply(self,cr, uid, ids, *args, **argv):
        return self._map_ids('add_reply',cr,uid,ids,*args,**argv)
    def remind_partner(self,cr, uid, ids, *args, **argv):
        return self._map_ids('remind_partner',cr,uid,ids,*args,**argv)
    def remind_user(self,cr, uid, ids, *args, **argv):
        return self._map_ids('remind_user',cr,uid,ids,*args,**argv)


event_registration()



class report_event_registration(osv.osv):
    _name = "report.event.registration"
    _description = "Events on registrations"
    _auto = False
    _columns = {
        'name': fields.char('Event',size=20),
        'date_begin': fields.datetime('Beginning date', required=True),
        'date_end': fields.datetime('Ending date', required=True),
        'draft_state': fields.integer('Draft Registration',size=20),
        'confirm_state': fields.integer('Confirm Registration',size=20),
        'register_max': fields.integer('Maximum Registrations'),
    }
    def init(self, cr):
        cr.execute("""
            create or replace view report_event_registration as (
                select
                e.id as id,
                c.name as name,
                e.date_begin as date_begin,
                e.date_end as date_end,
                (SELECT sum(nb_register) FROM event_registration x , crm_case c  WHERE x.case_id=c.id and c.section_id=e.section_id and state in ('draft')) as draft_state,
                (SELECT sum(nb_register) FROM event_registration x , crm_case c  WHERE x.case_id=c.id and c.section_id=e.section_id and state in ('open')) as confirm_state,
                e.register_max as register_max
                from
                event_event e,crm_case_section c
                where
                e.section_id=c.id
                )""")

report_event_registration()

class report_event_type_registration(osv.osv):
    _name = "report.event.type.registration"
    _description = "Event type on registration"
    _auto = False
    _columns = {
        'name': fields.char('Event Type',size=20),
        'nbevent':fields.integer('Number Of Events'),
        'draft_state': fields.integer('Draft Registrations',size=20),
        'confirm_state': fields.integer('Confirm Registrations',size=20),
        }
    def init(self, cr):
        cr.execute("""
            create or replace view report_event_type_registration as (
                select
                count(t.id) as id,
                t.name as name,
                (select sum(nb_register) from event_registration r , crm_case c , event_event e  where c.section_id=e.section_id and r.case_id=c.id and c.state='draft' and e.type=t.id ) as draft_state ,
                (select sum(nb_register) from event_registration r , crm_case c , event_event e  where c.section_id=e.section_id and r.case_id=c.id and c.state='open' and e.type=t.id ) as  confirm_state,
                count(t.id) as nbevent
                from
                    event_event e
                inner join
                    crm_case_section c1 on (e.section_id=c1.id)
                inner join
                    event_type t on (e.type=t.id)
                group by
                    t.name,t.id

            )""")
report_event_type_registration()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

