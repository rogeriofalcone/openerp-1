# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from osv import fields, osv
from operator import itemgetter
import sugar
import sugarcrm_fields_mapping
import pprint
pp = pprint.PrettyPrinter(indent=4)

def create_mapping(obj, cr, uid, res_model, open_id, sugar_id, context):
    model_data = {
        'name':  sugar_id,
        'model': res_model,
        'module': 'sugarcrm_import',
        'res_id': open_id
    }
    model_obj = obj.pool.get('ir.model.data')
    model_obj.create(cr, uid, model_data, context=context)

def find_mapped_id(obj, cr, uid, res_model, sugar_id, context):
    model_obj = obj.pool.get('ir.model.data')
    return model_obj.search(cr, uid, [('model', '=', res_model), ('module', '=', 'sugarcrm_import'), ('name', '=', sugar_id)], context=context)

def get_all(sugar_obj, cr, uid, model, sugar_val, context=None):
       models = sugar_obj.pool.get(model)
       str = sugar_val[0:2]
       all_model_ids = models.search(cr, uid, [('name', '=', sugar_val)]) or models.search(cr, uid, [('code', '=', str.upper())]) 
       output = [(False, '')]
       output = sorted([(o.id, o.name)
                for o in models.browse(cr, uid, all_model_ids,
                                       context=context)],
               key=itemgetter(1))
       return output

def get_all_states(sugar_obj, cr, uid, sugar_val, context=None):
    return get_all(sugar_obj,
        cr, uid, 'res.country.state', sugar_val, context=context)

def get_all_countries(sugar_obj, cr, uid, sugar_val, context=None):
    return get_all(sugar_obj,
        cr, uid, 'res.country', sugar_val, context=context)

def import_partner_address(sugar_obj, cr, uid, context=None):
    if not context:
        context = {}
    res_country_obj = sugar_obj.pool.get('res.country')
    map_partner_address = {
             'id': 'id',              
             'name': ['first_name', 'last_name'],
            'phone': 'phone_work',
            'mobile': 'phone_mobile',
            'fax': 'phone_fax',
            'function': 'title',
            'street': 'primary_address_street',
            'zip': 'primary_address_postalcode',
            'city': 'primary_address_city',
          #  'country_id/id': 'country_id/id',
           # 'state_id/id': 'state_id/id'
            }
    address_obj = sugar_obj.pool.get('res.partner.address')
    PortType, sessionid = sugar.login(context.get('username', ''), context.get('password', ''), context.get('url',''))
    sugar_data = sugar.search(PortType, sessionid, 'Contacts')
    for val in sugar_data:
        str = val.get('primary_address_country')[0:2]
        country = get_all_countries(sugar_obj, cr, uid, val.get('primary_address_country'), context)
        state = get_all_states(sugar_obj,cr, uid, val.get('primary_address_state'), context)
        #Need To Fix
#        val['country_id/id'] =  country and country[0][0] or res_country_obj.create(cr, uid, {'name': val.get('primary_address_country'), 'code': str}),
#      #  val['state_id/id'] =  state and state[0][0] or False        
        fields, datas = sugarcrm_fields_mapping.sugarcrm_fields_mapp(val, map_partner_address)
        address_obj.import_data(cr, uid, fields, [datas], mode='update', current_module='sugarcrm_import', context=context)
        


def import_users(sugar_obj, cr, uid, context=None):
    if not context:
        context = {}
    map_user = {'id' : 'id', 
             'name': ['first_name', 'last_name'],
            'login': 'user_name',
            
            'context_lang' : 'context_lang',
            'password' : 'password',
            '.id' : '.id',
            'context_department_id': 'department'
            } 
    user_obj = sugar_obj.pool.get('res.users')
    department_obj = sugar_obj.pool.get('hr.department')
    PortType,sessionid = sugar.login(context.get('username',''), context.get('password',''), context.get('url',''))
    sugar_data = sugar.search(PortType,sessionid, 'Users')
    for val in sugar_data:
        user_ids = user_obj.search(cr, uid, [('login', '=', val.get('user_name'))])
        if user_ids: 
            val['.id'] = str(user_ids[0])
        else:
            val['password'] = 'sugarcrm' #default password for all user
#            cr.execute('SELECT * FROM users_signatures u LIMIT 0,1000')
        new_department_id = department_obj.create(cr, uid, {'name': val.get('department')})
        val['context_department_id'] = new_department_id     
        val['context_lang'] = context.get('lang','en_US')
        fields, datas = sugarcrm_fields_mapping.sugarcrm_fields_mapp(val, map_user)
        #All data has to be imported separatly because they don't have the same field
        user_obj.import_data(cr, uid, fields, [datas], mode='update', current_module='sugarcrm_import', context=context)

def get_lead_status(surgar_obj, cr, uid, sugar_val,context=None):
    if not context:
        context = {}
    stage_id = ''
    stage_dict = {'status': #field in the sugarcrm database
        { #Mapping of sugarcrm stage : openerp opportunity stage
            'New' : 'New',
            'Assigned':'Qualification',
            'In Progress': 'Proposition',
            'Recycled': 'Negotiation',
            'Dead': 'Lost'
        },}
    stage = stage_dict['status'].get(sugar_val['status'], '')
    stage_pool = surgar_obj.pool.get('crm.case.stage')
    stage_ids = stage_pool.search(cr, uid, [('type', '=', 'lead'), ('name', '=', stage)])
    for stage in stage_pool.browse(cr, uid, stage_ids, context):
        stage_id = stage.id
    return stage_id

def get_opportunity_status(surgar_obj, cr, uid, sugar_val,context=None):
    if not context:
        context = {}
    stage_id = ''
    stage_dict = { 'sales_stage':
            {#Mapping of sugarcrm stage : openerp opportunity stage Mapping
               'Need Analysis': 'New',
               'Closed Lost': 'Lost',
               'Closed Won': 'Won',
               'Value Proposition': 'Proposition',
                'Negotiation/Review': 'Negotiation'
            },
    }
    stage = stage_dict['sales_stage'].get(sugar_val['sales_stage'], '')
    stage_pool = surgar_obj.pool.get('crm.case.stage')
    stage_ids = stage_pool.search(cr, uid, [('type', '=', 'opportunity'), ('name', '=', stage)])
    for stage in stage_pool.browse(cr, uid, stage_ids, context):
        stage_id = stage.id
    return stage_id

def get_billing_address(sugar_obj,cr, uid, val, map_partner_address, context=None):
    fields=[]
    datas=[]
    
    address_obj = sugar_obj.pool.get('res.partner.address')
    res_country_obj = sugar_obj.pool.get('res.country')
    str = val.get('billing_address_country')[0:2]
    map_partner_address.update({
        'street': 'billing_address_street',
        'zip': 'billing_address_postalcode',
        'city': 'billing_address_city',
        'country_id': 'country_id',
        'type': 'type'
            })
    val['type'] = 'invoice'
    country = get_all_countries(sugar_obj,cr, uid, val.get('billing_address_country'), context)
    state = get_all_states(sugar_obj, cr, uid, val.get('billing_address_state'), context)
    val['country_id'] =  country and country[0][0] or res_country_obj.create(cr, uid, {'name': val.get('billing_address_country'), 'code': str}),
    val['state_id'] =  state and state[0][0] or  False,           
    fields, datas = sugarcrm_fields_mapping.sugarcrm_fields_mapp(val, map_partner_address)
    dict_val = dict(zip(fields,datas))
    new_address_id = address_obj.create(cr,uid, dict_val)
    return new_address_id

def get_shipping_address(sugar_obj,cr, uid, val, map_partner_address, context=None):
    fields=[]
    datas=[]
    str = ''
    address_obj = sugar_obj.pool.get('res.partner.address')
    res_country_obj = sugar_obj.pool.get('res.country')
    str = val.get('shipping_address_country')[0:2]
    map_partner_address.update({
        'street': 'shipping_address_street',
        'zip': 'shipping_address_postalcode',
        'city': 'shipping_address_city',
         'country_id': 'country_id',
         'type': 'type'
        })
    val['type'] = 'delivery'
    country = get_all_countries(sugar_obj, cr, uid, val.get('shipping_address_country'), context)
    state = get_all_states(sugar_obj, cr, uid, val.get('shipping_address_state'), context)
    val['country_id'] =  country and country[0][0] or res_country_obj.create(cr, uid, {'name': val.get('shipping_address_country'), 'code': str}),
    val['state_id'] =  state and state[0][0] or  False,
    fields, datas = sugarcrm_fields_mapping.sugarcrm_fields_mapp(val, map_partner_address)
    dict_val = dict(zip(fields,datas))
    new_address_id = address_obj.create(cr,uid, dict_val)
    return new_address_id


def get_address(sugar_obj, cr, uid, val, context=None):
    map_partner_address={}
    address_id=[]
    fields=[]
    datas=[]
    address_obj = sugar_obj.pool.get('res.partner.address')
    address_ids = address_obj.search(cr, uid, [('name', '=',val.get('name')), ('type', 'in', ('invoice', 'delivery')), ('street', '=', val.get('billing_address_street'))])
    if address_ids:
        return address_ids 
    else:
        map_partner_address = {
            'id': 'id',                    
            'name': 'name',
            'partner_id/id': 'account_id',
            'phone': 'phone_office',
            'mobile': 'phone_mobile',
            'fax': 'phone_fax',
            'type': 'type'
            }
        
        address_id.append(get_billing_address(sugar_obj,cr, uid, val, map_partner_address, context))
        address_id.append(get_shipping_address(sugar_obj,cr, uid, val, map_partner_address, context))
        return address_id

def import_partners(sugar_obj, cr, uid, context=None):
    if not context:
        context = {}
    map_lead = {
                'id': 'id',
                'name': 'name',
                'website': 'website',
                'address/.id': 'address/.id',
                'user_id/id': 'assigned_user_id',
                'ref': 'sic_code',
                'comment': ['description', 'employees', 'ownership', 'annual_revenue', 'rating', 'industry', 'ticker_symbol'],
                'customer': False,
                'supplier': False
                }
        
    partner_obj = sugar_obj.pool.get('res.partner')
    address_obj = sugar_obj.pool.get('res.partner.address')
    PortType, sessionid = sugar.login(context.get('username', ''), context.get('password', ''), context.get('url',''))
    sugar_data = sugar.search(PortType, sessionid, 'Accounts')
    
    for val in sugar_data:
        add_id = get_address(sugar_obj, cr, uid, val, context)
        for res_address in address_obj.browse(cr, uid, add_id):
            partner_ids = partner_obj.search(cr, uid, [('name', '=', res_address.name)])
            if partner_ids:
                for partner in partner_obj.browse(cr, uid, partner_ids):
                    address_obj.write(cr,uid,res_address.id,{'partner_id':partner.id})
            else:
                val['address/.id'] = res_address
                if val.get('account_type') in  ('customer', 'prospect', 'other'):
                    val['customer'] = True
                else:
                    val['supplier'] = True
                    fields, datas = sugarcrm_fields_mapping.sugarcrm_fields_mapp(val, map_lead)
                    partner_obj.import_data(cr, uid, fields, [datas], mode='update', current_module='sugarcrm_import', context=context)

    
def import_leads(sugar_obj, cr, uid, context=None):
    if not context:
        context = {}
    map_lead = {
            'id' : 'id',
            'name': ['first_name', 'last_name'],
            'contact_name': ['first_name', 'last_name'],
            'description': 'description',
            'partner_name': ['first_name', 'last_name'],
            'email_from': 'email1',
            'phone': 'phone_work',
            'mobile': 'phone_mobile',
            'function':'title',
            'street': 'primary_address_street',
            'zip': 'primary_address_postalcode',
            'city':'primary_address_city',
            'user_id/id' : 'assigned_user_id',
            'stage_id.id' : 'stage_id.id',
            'type' : 'type',
            }
        
    lead_obj = sugar_obj.pool.get('crm.lead')
    PortType, sessionid = sugar.login(context.get('username', ''), context.get('password', ''), context.get('url',''))
    sugar_data = sugar.search(PortType, sessionid, 'Leads')
    for val in sugar_data:
        val['type'] = 'lead'
        stage_id = get_lead_status(sugar_obj, cr, uid, val, context)
        val['stage_id.id'] = stage_id
        fields, datas = sugarcrm_fields_mapping.sugarcrm_fields_mapp(val, map_lead)
        lead_obj.import_data(cr, uid, fields, [datas], mode='update', current_module='sugarcrm_import', context=context)

def import_opportunities(sugar_obj, cr, uid, context=None):
    if not context:
        context = {}
    map_opportunity = {'id' : 'id',
        'name': 'name',
        'probability': 'probability',
        'planned_revenue': 'amount_usdollar',
        'date_deadline':'date_closed',
        'user_id/id' : 'assigned_user_id',
        'stage_id.id' : 'stage_id.id',
        'type' : 'type',
    }
    lead_obj = sugar_obj.pool.get('crm.lead')
    PortType, sessionid = sugar.login(context.get('username', ''), context.get('password', ''), context.get('url',''))
    sugar_data = sugar.search(PortType, sessionid, 'Opportunities')
    for val in sugar_data:
        val['type'] = 'opportunity'
        stage_id = get_opportunity_status(sugar_obj, cr, uid, val, context)
        val['stage_id.id'] = stage_id
        fields, datas = sugarcrm_fields_mapping.sugarcrm_fields_mapp(val, map_opportunity)
        lead_obj.import_data(cr, uid, fields, [datas], mode='update', current_module='sugarcrm_import', context=context)

MAP_FIELDS = {'Opportunities':  #Object Mapping name
                    {'dependencies' : ['Users'],  #Object to import before this table
                     'process' : import_opportunities,
                     },
              'Leads':
                    {'dependencies' : ['Users'],  #Object to import before this table
                     'process' : import_leads,
                    },
              'Contacts':
                    {'dependencies' : ['Users'],  #Object to import before this table
                     'process' : import_partner_address,
                    },
              'Accounts':
                    {'dependencies' : ['Users'],  #Object to import before this table
                     'process' : import_partners,
                    },
                          
              'Users': 
                    {'dependencies' : [],
                     'process' : import_users,
                    },
#              'Users_Addresses': 
#                    {'dependencies' : [],
#                     'process' : import_users_addresses,
#                    },                     
          }

class import_sugarcrm(osv.osv):
    """Import SugarCRM DATA"""


    _name = "import.sugarcrm"
    _description = __doc__
    _columns = {
        'lead': fields.boolean('Leads', help="If Leads is checked, SugarCRM Leads data imported in openerp crm-Lead form"),
        'opportunity': fields.boolean('Opportunities', help="If Leads is checked, SugarCRM Leads data imported in openerp crm-Opportunity form"),
        'user': fields.boolean('User', help="If Users is checked, SugarCRM Users data imported in openerp crm-Opportunity form"),
        'contact': fields.boolean('Contacts', help="If Contacts is checked, SugarCRM Contacts data imported in openerp partner address form"),
        'account': fields.boolean('Accounts', help="If Accounts is checked, SugarCRM  Accounts data imported in openerp partner form"),
        'username': fields.char('User Name', size=64),
        'password': fields.char('Password', size=24),
    }
    _defaults = {
       'lead': True,
       'opportunity': True,
       'user' : True,
       'contact' : True,
       'account' : True,       
    }
    
    def get_key(self, cr, uid, ids, context=None):
        """Select Key as For which Module data we want import data."""
        if not context:
            context = {}
        key_list = []
        for current in self.browse(cr, uid, ids, context):
            if current.lead:
                key_list.append('Leads')
            if current.opportunity:
                key_list.append('Opportunities')
            if current.user:
                key_list.append('Users')
            if current.contact:
                key_list.append('Contacts')
            if current.account:
                key_list.append('Accounts')     
                           

        return key_list

    def import_all(self, cr, uid, ids, context=None):
        """Import all sugarcrm data into openerp module"""
        if not context:
            context = {}
        keys = self.get_key(cr, uid, ids, context)
        imported = set() #to invoid importing 2 times the sames modules
        for key in keys:
            if not key in imported:
                self.resolve_dependencies(cr, uid, MAP_FIELDS, MAP_FIELDS[key]['dependencies'], imported, context=context)
                MAP_FIELDS[key]['process'](self, cr, uid, context)
                imported.add(key)


        obj_model = self.pool.get('ir.model.data')
        model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','import.message.form')])
        resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'import.message',
                'views': [(resource_id,'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
            }

    def resolve_dependencies(self, cr, uid, dict, dep, imported, context=None):
        for dependency in dep:
            if not dependency in imported:
                self.resolve_dependencies(cr, uid, dict, dict[dependency]['dependencies'], imported, context=context)
                dict[dependency]['process'](self, cr, uid, context)
                imported.add(dependency)


import_sugarcrm()
