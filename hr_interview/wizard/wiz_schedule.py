import wizard
import pooler
import datetime
import time
from copy import deepcopy
import netsvc

_schedule_form = '''<?xml version="1.0"?>
<form string="Interview Scheduling Of Candidate">
    <field name="start_interview"/>
    <field name="end_interview"/>
    <field name="interval_time"/>
 </form>'''

_schedule_fields = {
    'start_interview' : {'string' : 'Start Interview Time', 'type' : 'datetime','required':True },
    'end_interview' : {'string' : 'End Interview Time', 'type' : 'datetime','required':True },
    'interval_time' : {'string' : 'Interval(Approximate Evaluation Time) ', 'type' : 'integer','required':True },
    }


form = """<?xml version="1.0"?>
<form string="Use Model">
    <separator string="Scheduled Candidate List " colspan="4"/>
    <field name="list_all"   nolabel="1"/>
    <separator string="Some Candidate Still Remaining " colspan="4"/>
    <field name="list"   nolabel="1"/>
</form>
"""
fields = {
    'list' : {'string': "",'type':'text','readonly':True},
    'list_all' : {'string': "",'type':'text','readonly':True}
          }


class wiz_schedule(wizard.interface):
    def _scheduling(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        hr_int_obj = pool.get("hr.interview")
        if time.strptime(str(data['form']['start_interview']),"%Y-%m-%d %H:%M:%S") < time.strptime(data['form']['end_interview'],"%Y-%m-%d %H:%M:%S") and time.strptime(str(data['form']['start_interview']),"%Y-%m-%d %H:%M:%S")[:3] ==time.strptime(str(data['form']['end_interview']),"%Y-%m-%d %H:%M:%S")[:3] :  
            if datetime.datetime(*time.strptime(str(data['form']['end_interview']),"%Y-%m-%d %H:%M:%S")[:6]) >= datetime.datetime(*time.strptime(str(data['form']['start_interview']),"%Y-%m-%d %H:%M:%S")[:6]) + datetime.timedelta(minutes=int(data['form']['interval_time'])):
                cur_time = data['form']['start_interview']
                re_id = deepcopy(data['ids'])
                list_all="Interview ID \t Name "
                for rec in data['ids']:
                    wf_service = netsvc.LocalService('workflow')
                    wf_service.trg_validate(uid, 'hr.interview', rec, 'state_scheduled', cr)
                    record = hr_int_obj.read(cr,uid,rec,['hr_id','name'])
                    list_all +="\n" + record['hr_id']+"\t\t" + record['name'] 
                    id = hr_int_obj.write(cr,uid,rec,{'date':cur_time,'state':'scheduled'})
                    cur_time  = datetime.datetime(*time.strptime(str(cur_time),"%Y-%m-%d %H:%M:%S")[:6]) + datetime.timedelta(minutes=int(data['form']['interval_time']))
                    re_id.remove(rec)
                    end_time  = datetime.datetime(*time.strptime(str(cur_time),"%Y-%m-%d %H:%M:%S")[:6]) + datetime.timedelta(minutes=int(data['form']['interval_time']))
                    if len(re_id) > 0 and time.strptime(str(end_time),"%Y-%m-%d %H:%M:%S") > time.strptime(data['form']['end_interview'],"%Y-%m-%d %H:%M:%S") :
                        remain="Interview ID \t Name "
                        for record in hr_int_obj.read(cr,uid,re_id,['hr_id','name']):
                            remain +="\n" + record['hr_id']+"\t\t" + record['name'] 
                        data['form']['list']=remain
                        data['form']['list_all']=list_all
                        return data['form']
            else :
                raise  wizard.except_wizard(_('UserError'),_('Start date-time and end date-time difference is less than of interval time '))
                return {}
        else :
            raise  wizard.except_wizard(_('UserError'),_('Start time and end time both are not same or start date and end date both are  not same '))
            return {}
        
        data['form']['list_all']= list_all
        data['form']['list']= "None"
        
        return data['form']
    
    
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_schedule_form, 'fields':_schedule_fields, 'state':[('Schedule','Scheduled','gtk-ok'),('end','Cancel','gtk-cancel')]}
                },
            'scheduled': {
            'actions': [_scheduling],
            'result': {'type': 'form','arch':form, 'fields':fields, 'state':[('end','Ok')]}
                },                
    }
wiz_schedule('wiz_interview_scheduling')