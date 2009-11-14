# -*- coding: utf-8 -*-
##############################################################################
#
#    hr_attendance_project module for OpenERP
#    Copyright (C) 2008 Zikzakmedia S.L. (http://zikzakmedia.com)
#       Raimon Esteve <resteve@zikzakmedia.com> All Rights Reserved.
#       Jordi Esteve <resteve@zikzakmedia.com> All Rights Reserved.
#    Copyright (C) 2009 SYLEAM Info Services (http://www.Syleam.fr)
#       Sebastien LANGE <sebastien.lange@syleam.fr> All Rights Reserved.
#
#    This file is a part of hr_attendance_project
#
#    hr_attendance_project is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    hr_attendance_project is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import wizard
import time
import pooler
from tools.translate import _
from tools.misc import UpdateableStr

si_form ='''<?xml version="1.0"?> 
<form string="Sign in / Sign out">
    <separator string="Sign in" colspan="4"/>
    <field name="name" readonly="True" />
    <field name="state" readonly="True" />
    <field name="server_date"/>
    <label string="(local time on the server side)" colspan="2"/>
    <field name="date"/>
    <label string="(Keep empty for current time)" colspan="2"/>
    <field name="tasks_project" domain="[('project_id.members', 'child_of', [uid]),('state','in',['draft','open'])]" colspan="4"/>
</form>'''

si_fields = {
    'name': {'string': "Employee's name", 'type':'char', 'required':True, 'readonly':True},
    'state': {'string': "Current state", 'type' : 'char', 'required' : True, 'readonly': True},
    'date': {'string':"Starting Date", 'type':'datetime'},
    'server_date': {'string':"Current Date", 'type':'datetime', 'readonly':True},
    'tasks_project': {'string':"Task", 'type':'many2one', 'relation':'project.task'},
}

so_form_base = '''<?xml version="1.0" ?>
<form string="Sign in status">
    <separator string="General Information" colspan="4" />
    <field name="name" readonly="True" />
    <field name="state" readonly="True" />
    <field name="date_start"/>
    <field name="server_date"/>
    <separator string="Work done in the last period" colspan="4" />
    <field name="account_id" colspan="2" attrs="{'readonly':[('project_id','!=',False)],'required':[('project_id','==',False)]}"/>
    <field name="project_id" attrs="{'readonly':[('account_id','!=',False)],'required':[('account_id','==',False)]}" domain="[('members','child_of',[uid]), ('state','=','open')]" />
    <field name="tasks_account" domain="[('project_id.category_id', '=', account_id),('state','=','open'),%s]" attrs="{'readonly':[('project_id','!=',False)],'required':[('project_id','==',False)]}"/>
    <field name="tasks_project" domain="[('project_id', '=', project_id),('state','=','open'),%s]" attrs="{'readonly':[('account_id','!=',False)],'required':[('account_id','==',False)]}"/>
    <field name="info" colspan="4"/>
    <field name="date" colspan="2"/>
    <label string="(Keep empty for current_time)" colspan="2"/>
    <field name="analytic_amount"/>
</form>'''

so_form = UpdateableStr()

so_fields = {
    'name': {'string':"Employee's name", 'type':'char', 'required':True, 'readonly':True},
    'state': {'string':"Current state", 'type':'char', 'required':True, 'readonly':True},
    'account_id': {'string':"Analytic Account", 'type':'many2one', 'relation':'account.analytic.account', 'domain':"[('type','=','normal')]"},
    'info': {'string':"Work Description", 'type':'char', 'size':256, 'required':True},
    'date': {'string':"Closing Date", 'type':'datetime'},
    'date_start': {'string':"Starting Date", 'type':'datetime', 'readonly':True},
    'server_date': {'string':"Current Server Date", 'type':'datetime', 'readonly':True},
    'analytic_amount': {'string':"Minimum Analytic Amount", 'type':'float'},
    'project_id': {'string':"Project", 'type':'many2one', 'relation':'project.project'},
    'tasks_account': {'string':"Task", 'type':'many2one', 'relation':'project.task'},
    'tasks_project': {'string':"Task", 'type':'many2one', 'relation':'project.task'},
}

def _get_empid(self, cr, uid, data, context):
    emp_obj = pooler.get_pool(cr.dbname).get('hr.employee')
    emp_id = emp_obj.search(cr, uid, [('user_id', '=', uid)])
    if emp_id:
        employee = emp_obj.read(cr, uid, emp_id)[0]
        return {'name': employee['name'], 'state': employee['state'], 'emp_id': emp_id[0], 'date':False, 'server_date':time.strftime('%Y-%m-%d %H:%M:%S')}
    raise wizard.except_wizard(_('UserError'), _('No employee defined for your user !'))

def _get_empid2(self, cr, uid, data, context=None):
    if not context:
        context = {}
    model_data_obj = pooler.get_pool(cr.dbname).get('ir.model.data')
    menu_id = model_data_obj.search(cr, uid, [('name','=','menu_sitp_sotp_my')])[0] 
    menu = model_data_obj.browse(cr, uid, menu_id)
    if not context.get('task', False):
        if menu.res_id == data['id']:
            # The menu 'Sign in / Sign out by my task project' has been selected
            so_form.string = so_form_base % ("('user_id', '=', uid)", "('user_id', '=', uid)")
        else:
            # The menu 'Sign in / Sign out by task project' has been selected
            so_form.string = so_form_base % ('', '')
    else:
        so_form.string = so_form_base % ('', '')

    res = _get_empid(self,cr, uid, data, context)
    cr.execute('select name,action from hr_attendance where employee_id=%s order by name desc limit 1', (res['emp_id'],))
    res['server_date'] = time.strftime('%Y-%m-%d %H:%M:%S')
    res['date_start'] = cr.fetchone()[0]
    res['info'] = ''
    res['account_id'] = False
    if context.get('task', False):
        task_obj = pooler.get_pool(cr.dbname).get('project.task')
        task = task_obj.browse(cr, uid, data['id'])
        res['project_id'] = task.project_id.id
        res['tasks_project'] = data['id']
    return res

def _sign_in_result(self, cr, uid, data, context):
    pool_obj = pooler.get_pool(cr.dbname)
    emp_obj = pool_obj.get('hr.employee')
    emp_id = data['form']['emp_id']
    from osv.osv import except_osv
    try:
        success = emp_obj.sign_in(cr, uid, [emp_id], dt=data['form']['date'] or False)
    except except_osv, e:
        raise wizard.except_wizard(e.name, e.value)
    return {}

def _open_task(self, cr, uid, data, context):
    pool_obj = pooler.get_pool(cr.dbname)
    emp_obj = pool_obj.get('hr.employee')
    emp_id = data['form']['emp_id']
    model_data_ids = pool_obj.get('ir.model.data').search(cr,uid,[('model','=','ir.ui.view'),('name','=','view_task_form2')])
    resource_id = pool_obj.get('ir.model.data').read(cr,uid,model_data_ids,fields=['res_id'])[0]['res_id']
    from osv.osv import except_osv
    try:
        success = emp_obj.sign_in(cr, uid, [emp_id], dt=data['form']['date'] or False)
    except except_osv, e:
        raise wizard.except_wizard(e.name, e.value)
    if data['form']['tasks_project']:
        return {
            'domain': "[('id','=', %s)]" %  data['form']['tasks_project'],
            'context': "{'task':1}",
            'name': 'Task',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'views': [(False,'tree'),(resource_id,'form')],
            'type': 'ir.actions.act_window'
        }
    else:
        return {}

def _write(self, cr, uid, data, emp_id, context):
    project_obj = pooler.get_pool(cr.dbname).get('project.project')
    project_task_obj = pooler.get_pool(cr.dbname).get('project.task.work')
    timesheet_obj = pooler.get_pool(cr.dbname).get('hr.analytic.timesheet')

    hour = (time.mktime(time.strptime(data['form']['date'] or time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')) -
        time.mktime(time.strptime(data['form']['date_start'], '%Y-%m-%d %H:%M:%S'))) / 3600.0
    minimum = data['form']['analytic_amount']
    if minimum:
        hour = round(round((hour + minimum / 2) / minimum) * minimum, 2)
    res = timesheet_obj.default_get(cr, uid, ['product_id','product_uom_id'])
    if not res['product_uom_id']:
        raise wizard.except_wizard(_('UserError'), _('No cost unit defined for this employee !'))
    up = timesheet_obj.on_change_unit_amount(cr, uid, False, res['product_id'], hour, res['product_uom_id'])['value']

    if not data['form']['account_id']:
        project = project_obj.browse(cr, uid, data['form']['project_id'])
        if not project.category_id:
            raise wizard.except_wizard(_('Error'), _('This project does not have any analytic account defined.'))
        account_id = project.category_id.id
        task_id = data['form']['tasks_project']
    else:
        account_id = data['form']['account_id']
        task_id = data['form']['tasks_account']    
 
    value = {
        'name': data['form']['info'],
        'date': data['form']['date_start'],
        'task_id': task_id,
        'hours': hour,
        'user_id': uid,
    }
    project_task_obj.create(cr, uid, value)

    res['name'] = data['form']['info']
    #res['account_id'] = data['form']['account_id']
    res['account_id'] = account_id
    res['unit_amount'] = hour
    res.update(up)
    up = timesheet_obj.on_change_account_id(cr, uid, [], res['account_id']).get('value', {})
    res.update(up)
    return timesheet_obj.create(cr, uid, res, context)

def _sign_out_result_end(self, cr, uid, data, context):
    emp_obj = pooler.get_pool(cr.dbname).get('hr.employee')
    emp_id = data['form']['emp_id']
    emp_obj.sign_out(cr, uid, [emp_id], dt=data['form']['date'])
    _write(self, cr, uid, data, emp_id, context)
    return {}

def _sign_out_result(self, cr, uid, data, context):
    emp_obj = pooler.get_pool(cr.dbname).get('hr.employee')
    emp_id = data['form']['emp_id']
    emp_obj.sign_change(cr, uid, [emp_id], dt=data['form']['date'])
    _write(self, cr, uid, data, emp_id, context)
    return {}

def _state_check(self, cr, uid, data, context):
    emp_id = _get_empid(self, cr, uid, data, context)['emp_id']
    # get the latest action (sign_in or out) for this employee
    cr.execute('select action from hr_attendance where employee_id=%s and action in (\'sign_in\',\'sign_out\') order by name desc limit 1', (emp_id,))
    res = (cr.fetchone() or ('sign_out',))[0]
#TODO: invert sign_in et sign_out
    return res

class wiz_sitp_sotp(wizard.interface):
    states = {
            'init' : {
                'actions' : [_get_empid],
                'result' : {'type' : 'choice', 'next_state': _state_check}
            },
            'sign_out' : { # this means sign_in...
                'actions' : [_get_empid],
                'result' : {'type':'form', 'arch':si_form, 'fields' : si_fields, 'state':[('end', 'Cancel'),('si_result', 'Start Working'),('si_result_open_task', 'Start Working and Open Task') ] }
            },
            'si_result' : {
                'actions' : [_sign_in_result],
                'result' : {'type':'state', 'state':'end'}
            },
            'si_result_open_task': {
                'actions': [],
                'result': {'type':'action', 'action':_open_task, 'state':'end'}
            },
            'sign_in' : { # this means sign_out...
                'actions' : [_get_empid2],
                'result' : {'type':'form', 'arch':so_form, 'fields':so_fields, 'state':[('end', 'Cancel'),('so_result', 'Change Work'),('so_result_end', 'Stop Working') ] }
            },
            'so_result' : {
                'actions' : [_sign_out_result],
                'result' : {'type':'state', 'state':'end'}
            },
            'so_result_end' : {
                'actions' : [_sign_out_result_end],
                'result' : {'type':'state', 'state':'end'}
            },
    }
wiz_sitp_sotp('hr_timesheet.sitp_sotp')
