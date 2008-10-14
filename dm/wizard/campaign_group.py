# -*- encoding: utf-8 -*-
import wizard
import pooler

class wizard_campaign_group(wizard.interface):

    new_group = '''<?xml version="1.0"?>
    <form string="Select Group">
        <field name="group" colspan="4"/>
    </form>'''
    
    group_form = '''<?xml version="1.0"?>
    <form string="Create Group">
        <field name="group" colspan="4"/>
    </form>'''
    
    message ='''<?xml version="1.0"?>
    <form string="Create Group">
        <label align="0.0" colspan="4" string="Selected campaign has been added in the group.Campaigns that are already in some group will not be added in new group and will remain in same group"/>
    </form>'''
    
    error_message = '''<?xml version="1.0"?>
    <form string="Error!!!">
        <label align="0.0" colspan="4" string="Group name can't be none.You have to select any avilable group or create new"/>
    </form>'''
    
    def _add_group(self, cr, uid, data, context):
        if context.has_key('group_id'):
            group_id = context['group_id']
        else :
            group_id = data['form']['group']
        pool=pooler.get_pool(cr.dbname)
        camp_obj = pool.get('dm.campaign')
        for r in camp_obj.browse(cr,uid,data['ids']):
            if not r.campaign_group_id:
                camp_obj.write(cr,uid,[r.id],{'campaign_group_id':group_id})
        return {}

    def _new_group(self, cr, uid, data, context):
        pool=pooler.get_pool(cr.dbname)
        group_id = pool.get('dm.campaign.group').create(cr,uid,{'name':data['form']['group']})
        context['group_id'] = group_id
        self._add_group(cr,uid,data,context)
        return {}
    
    def _get_groups(self, cr, uid, context):
        pool=pooler.get_pool(cr.dbname)
        group_obj=pool.get('dm.campaign.group')
        ids=group_obj.search(cr, uid, [])
        res=[(group.id, group.name) for group in group_obj.browse(cr, uid, ids)]
        res.sort(lambda x,y: cmp(x[1],y[1]))
        return res    
    
    def _next(self, cr, uid, data, context):
        if not data['form']['group']:
            return 'error'
        return 'add'

    
    group_fields = {
                    
        'group': {'string': 'Select Group', 'type': 'selection', 'selection':_get_groups, }
        
        }
    
    new_group_fields = {
        'group': {'string': 'Group Name', 'type': 'char', 'size':64, 'required':True }
        }    
    
    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':group_form, 'fields':group_fields, 'state':[('end','Cancel'),('name_group','Create New Group'),('next','Add in Group'),]}
            },
        'name_group': {
            'actions': [],
            'result': {'type':'form', 'arch':new_group, 'fields':new_group_fields, 'state':[('end','Cancel'),('new','Create Group')]}
            },            
        'new': {
            'actions': [_new_group],
            'result': {'type': 'form', 'arch': message, 'fields':{} ,'state': [('end', 'Ok', 'gtk-ok', True)]}
        },
        'next': {
            'actions': [],
            'result': {'type': 'choice', 'next_state': _next}
        },
        'error': {
            'actions': [],
            'result': {'type': 'form', 'arch': error_message, 'fields':{} ,'state': [('end','Cancel'),('init','Select the group')]}
        },        
        'add': {
            'actions': [_add_group],
            'result': {'type': 'form', 'arch': message, 'fields':{} ,'state': [('end', 'Ok', 'gtk-ok', True)]}
        },
        }
wizard_campaign_group("wizard_campaign_group")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: