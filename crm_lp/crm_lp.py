# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import tools
from osv import fields,osv,orm
import pooler

import mx.DateTime
import base64
from tools.translate import _
from launchpadlib.launchpad import Launchpad, EDGE_SERVICE_ROOT
from launchpadlib.credentials import Credentials
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import os
import threading
import pickle
import time
import sys
import datetime

class lpServer(threading.Thread):
    launchpad = False

    def __init__(self):
        super(lpServer, self).__init__()
        self.launchpad = self.get_lp()

    def get_lp(self):
        launchpad = False
        cachedir = os.path.expanduser('~/.launchpadlib/cache')
        if not os.path.exists(cachedir):
                os.makedirs(cachedir,0700)
        credfile = os.path.expanduser('~/.launchpadlib/credentials')
        try:
                credentials = Credentials()
                credentials.load(open(credfile))
                launchpad = Launchpad(credentials, EDGE_SERVICE_ROOT, cachedir)
        except:
                launchpad = Launchpad.get_token_and_login(sys.argv[0], EDGE_SERVICE_ROOT, cachedir)
        return launchpad


    def get_lp_bugs(self, projects):
        launchpad = self.launchpad
        res = {}
        if not launchpad:
            return res
        if not isinstance(projects,list):
            projects = [projects]

        bug_status=[]
        for project in projects:
            result = {}
            r = {}
            lp_project = self.launchpad.projects[str(project)]
            result['non-series'] = lp_project.searchTasks(status=bug_status)
            if 'series' in lp_project.lp_collections:
                for series in lp_project.series:
                    result[series.name] = series.searchTasks()
                bug_list=[]
                for name, bugs in result.items():
                    for bug in bugs:
                        bug_list.append(bug)
                res[project]=bug_list
        return  res

    def getProject(self, project):
        project = self.launchpad.projects[project]
        return project

    def getSeries(self, project):
        lp_project = self.launchpad.projects[project]
        if 'series' in lp_project.lp_collections:
                return lp_project.series.entries
        else:
            return None

    def getMilestones(self, project, ml):
        lp_project =self.launchpad.projects[project]
        if 'all_milestones' in lp_project.lp_collections:
                temp = lp_project.all_milestones.entries
                res = [item for item in temp if item['series_target_link'] == ml]
                return res
        else:
            return None

class project_project(osv.osv):
    _inherit = "project.project"
    _columns = {
                'series_ids' : fields.one2many('lp.series', 'project_id', 'LP Series'),
                'milestone_ids' : fields.one2many('lp.project.milestone', 'project_id', 'LP Milestone'),
                'bugs_target': fields.char('Bugs Target', size=300),
                }        
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        vals['bugs_target'] = "https://api.edge.launchpad.net/beta/" + vals['name']
        result = super(osv.osv, self).write(cr, uid, ids[0], vals, context)
        return result
    
project_project()        

class lp_series(osv.osv):
    _name="lp.series"
    _description="LP Series"
    _columns={
              'name':fields.char("Series Name",size=200, required=True, help="The name of the series"),
              'status': fields.char("Status", size=100),
              'summary': fields.char("Summary", size=1000, help="The summary should be a single short paragraph."),
              'project_id': fields.many2one('project.project', 'LP Project', ondelete='cascade'),
               'milestone_ids' : fields.one2many('lp.project.milestone', 'series_id', 'LP Milestone'),
              }
lp_series()

class lp_project_milestone(osv.osv):
    _name="lp.project.milestone"
    _description= "LP milestone"
    _columns={
        'name':fields.char('Version', size=100,required=True),
        'series_id':fields.many2one('lp.series', 'Series', readonly=True,ondelete='cascade'),
        'project_id': fields.many2one('project.project', 'Project', readonly=True),
        'expect_date': fields.datetime('Expected Date', readonly=True),
        }

lp_project_milestone()

class crm_case(osv.osv):
    _inherit = "crm.case"

    _columns = {
                'project_id': fields.many2one('project.project', 'Project'),
                'bug_id': fields.integer('Bug ID',readonly=True),
                'milestone_id': fields.many2one('lp.project.milestone', 'Milestone'),
                }
    
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        attrs = ['stage_id', 'priority']
        for attr in attrs:
            if attr in vals:
                vals['date_action_last'] = time.strftime('%Y-%m-%d %H:%M:%S')
        result = super(osv.osv, self).write(cr, uid, ids, vals, context)
        return result

    def _check_bug(self, cr, uid, ids=False, context={}):
        '''
        Function called by the scheduler to process cases for date actions
        Only works on not done and cancelled cases
        '''
        val={}
        pool=pooler.get_pool(cr.dbname)
        sec_obj = pool.get('crm.case.section')
        sec_id = sec_obj.search(cr, uid, [('code', '=', 'BugSup')])
        if sec_id:
            lp_server = lpServer()
            self._create_bug(cr, uid, sec_id,lp_server, context)
            self._find_project_bug(cr,uid,sec_id,lp_server)
            return True
        else:
            return False

    def _create_bug(self, cr, uid, sec_id,lp_server=None,context={}):
        pool=pooler.get_pool(cr.dbname)
        case_stage= pool.get('crm.case.stage')
        
        categ_fix_id=case_stage.search(cr, uid, [('section_id','=',sec_id[0]),('name','=','Fixed')])
        categ_inv_id=case_stage.search(cr, uid, [('section_id','=',sec_id[0]),('name','=','Invalid')])
        categ_future_id=case_stage.search(cr, uid, [('section_id','=',sec_id[0]), ('name','=','Future')])
        categ_wfix_id=case_stage.search(cr, uid, [('section_id','=',sec_id[0]),('name','=',"Won'tFix")])
        
        crm_case_obj = pool.get('crm.case')
        crm_ids=crm_case_obj.search(cr,uid,[('bug_id','=',False),('section_id','=',sec_id[0]),('project_id','!=',False)])
        launchpad = lp_server.launchpad
        if crm_ids:
            for case in crm_case_obj.browse(cr,uid, crm_ids):
                title = case.name
                target = case.project_id.bugs_target
                if not target:
                    target = "https://api.edge.launchpad.net/beta/" + case.project_id.name
                description=case.description
                b=launchpad.bugs.createBug(title=title, target=target, description=description)
                if b:
                    bool = self.write(cr,uid,case.id,{'bug_id' : b.id},context=None)
                    status='New'
                    imp ='Undecided'
                    if case.stage_id.id == categ_future_id[0] and case.priority == '5':
                        imp = 'Wishlist'
                    elif case.priority == '1':
                        imp = 'High'
                    elif case.priority == '3':
                        imp = 'Medium'
                    if case.stage_id.id == categ_fix_id[0]:
                        status = 'Fix Released'
                    if case.stage_id.id == categ_inv_id[0]:
                        status = 'invalid'
                    t=b.bug_tasks[0]
                    t.status = status
                    t.importance = imp
                    t.lp_save()
                return True
        else:
                return False

    def _find_project_bug(self, cr, uid,sec_id,lp_server=None,context={}):

        pool=pooler.get_pool(cr.dbname)
        case_stage= pool.get('crm.case.stage')

        categ_fix_id=case_stage.search(cr, uid, [('section_id','=',sec_id[0]),('name','=','Fixed')])
        categ_inv_id=case_stage.search(cr, uid, [('section_id','=',sec_id[0]),('name','=','Invalid')])
        categ_future_id=case_stage.search(cr, uid, [('section_id','=',sec_id[0]), ('name','=','Future')])
        categ_wfix_id=case_stage.search(cr, uid, [('section_id','=',sec_id[0]),('name','=',"Won'tFix")])
        val={}
        res={}
        series_ids=[]
        prj = self.pool.get('project.project')
        project_id=prj.search(cr,uid,[])
        for prj_id in prj.browse(cr,uid, project_id):
            project_name=str(prj_id.name)
            if project_name.find('openobject') == 0:
                prjs=lp_server.get_lp_bugs(project_name)
                lp_project = lp_server.getProject(project_name)
                self._get_project_series( cr, uid,lp_project,prj_id.id,lp_server)
                for key, bugs in prjs.items():
                        for bug in bugs:
                            b_id = self.search(cr,uid,[('bug_id','=',bug.bug.id)])
                            val['project_id']=prj_id.id
                            val['bug_id']=bug.bug.id
                            val['name']=bug.bug.title
                            val['section_id']=sec_id[0]
                            if bug.importance == 'Wishlist':
                                val['stage_id']=categ_future_id[0]
                                val['priority']='5'
                            elif bug.importance == 'Critical':
                                val['priority']='1'
                            elif bug.importance=='High':
                                val['priority']='2'
                            elif bug.importance=='Medium':
                                val['priority']='3'
                            if bug.status in ('Confirmed','Fix Released'):
                                val['stage_id']=categ_fix_id[0]
                            if bug.status =='invaild':
                                val['stage_id']= val['stage_id']=categ_inv_id[0]
                            if bug.milestone_link:
                                val['milestone_url']=bug.milestone_link
                            if not b_id:
                                self.create(cr, uid, val,context=context)
                            if b_id:
                                crm_case = self.browse(cr,uid, b_id[0])
                                lp_last_up_time = str(bug.bug.date_last_updated).split('.')[0]
                                lp_last_up_timestamp = time.mktime(time.strptime(lp_last_up_time,'%Y-%m-%d %H:%M:%S'))
                                if not crm_case.date_action_last:
                                    local_last_up_time=0
                                    local_last_up_timestamp = 0
                                    local_last_up_timestamp1=0
                                else:
                                    local_last_up_time = str(crm_case.date_action_last).split('.')[0]
                                    local_last_up_timestamp = time.mktime(time.strptime(local_last_up_time,'%Y-%m-%d %H:%M:%S')) + time.timezone
                                    local_last_up_timestamp1 = time.mktime(time.strptime(local_last_up_time,'%Y-%m-%d %H:%M:%S'))
                                    
                                args = (cr, uid, context, sec_id, crm_case, bug, val)
                                if lp_last_up_timestamp >= local_last_up_timestamp:
                                    self._update_local_record(*args)
                                elif lp_last_up_timestamp < local_last_up_timestamp:
                                    self._update_lp_record(*args)
                            cr.commit()
        return True
    
    def _get_project_series(self, cr, uid,lp_project,lp_project_id,lp_server=None,context={}):
        pool=pooler.get_pool(cr.dbname)
        all_series = lp_server.getSeries(lp_project)
        if all_series:
            prj_milestone_ids=[]
            lp_series = pool.get('lp.series')
            for series in all_series:
                res={}
                res['name'] = series['name']
                res['status'] = series['status']
                res['summary'] = series['summary']
                res['project_id'] = lp_project_id
                lp_series_id=lp_series.create(cr, uid, res,context=context)
                ml = series['all_milestones_collection_link'].rsplit('/',1)[0]
                cr.commit()
                self._get_project_milestone(cr, uid, lp_series_id,ml,lp_project,lp_project_id, lp_server)

        return True

    def _get_project_milestone(self, cr, uid,lp_series_id,milestone,lp_project,lp_project_id,lp_server=None,context={}):
        pool=pooler.get_pool(cr.dbname)
        res={}
        all_milestones = lp_server.getMilestones(lp_project, milestone)
        if all_milestones:
            milestone_ids=[]
            lp_milestones = pool.get('lp.project.milestone')
            for ms in all_milestones:
                res['name'] = ms['name']
                res['series_id'] = lp_series_id
                res['project_id'] = lp_project_id
                if ms['date_targeted']:
                    res['expect_date'] = ms['date_targeted']
                lp_milestones_id=lp_milestones.create(cr, uid, res,context=context)
                cr.commit()
        return True
    
    def _update_local_record(self, cr, uid, context, sec_id, crm_bug, lp_bug, val):
        pool=pooler.get_pool(cr.dbname)
        case= pool.get('crm.case')
        b=case.write(cr,uid,crm_bug.id,val,context=context)
        if b:
            return True
        return False
    
    def _update_lp_record(self, cr, uid, context, sec_id, crm_bug, lp_bug, val):
        pool=pooler.get_pool(cr.dbname)
        case_stage= pool.get('crm.case.stage')

        categ_fix_id=case_stage.search(cr, uid, [('section_id','=',sec_id[0]),('name','=','Fixed')])
        categ_inv_id=case_stage.search(cr, uid, [('section_id','=',sec_id[0]),('name','=','Invalid')])
        categ_future_id=case_stage.search(cr, uid, [('section_id','=',sec_id[0]), ('name','=','Future')])
        categ_wfix_id=case_stage.search(cr, uid, [('section_id','=',sec_id[0]),('name','=',"Won'tFix")])
        
        status='New'
        imp ='Undecided'
        if crm_bug.stage_id.id == categ_future_id[0] and crm_bug.priority == '5':
            imp = 'Wishlist'
        elif crm_bug.priority == '1':
            imp = 'Critical'
        elif crm_bug.priority == '2':
            imp = 'High'
        elif crm_bug.priority == '3':
            imp = 'Medium'
        if crm_bug.stage_id.id == categ_fix_id[0]:
            status = 'Fix Released'
        if crm_bug.stage_id.id == categ_inv_id[0]:
            status = 'Invalid'
        t=lp_bug.bug.bug_tasks[0]
        t.status = status
        t.importance = imp
        t.lp_save()
        return True
crm_case()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
