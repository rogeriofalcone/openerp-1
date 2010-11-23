# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

from osv import fields, osv
import pooler
import binascii
import base64
import os
import time
import smtplib
import mimetypes
from optparse import OptionParser
from email import Encoders
from email.Message import Message
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
import netsvc
import random
import sys
import tools
import re
from tools.translate import _
#if sys.version[0:3] > '2.4':
#    from hashlib import md5
#else:
#    from md5 import md5

class SmtpClient(osv.osv):
    _name = 'email.smtpclient'
    _description = 'Email Client'
    _columns = {
        'name' : fields.char('Server Name', size=256, required=True),
        'from_email' : fields.char('Email From', size=256, required=True, readonly=True, states={'new':[('readonly',False)]}),
        'email' : fields.char('Email Address', size=256, required=True, readonly=True, states={'new':[('readonly',False)]}),
        'use_auth': fields.boolean("Use Authentication", readonly=True, states={'new': [('readonly',False)]}),
        'user' : fields.char('User Name', size=256, required=False, readonly=True, states={'new':[('readonly',False)]}),
        'password' : fields.char('Password', size=256, required=False, readonly=True, states={'new':[('readonly',False)]}),
        'server' : fields.char('SMTP Server', size=256, required=True, readonly=True, states={'new':[('readonly',False)]}),
        'port' : fields.char('SMTP Port', size=256, required=True, readonly=True, states={'new':[('readonly',False)]}),
        'ssl' : fields.boolean("Use SSL?", readonly=True, states={'new':[('readonly',False)]}),
        'use_debug': fields.boolean("Show debugging information"),
        'users_id': fields.many2many('res.users', 'res_smtpserver_group_rel', 'sid', 'uid', 'Users Allowed'),
        'state': fields.selection([
            ('new','Not Verified'),
            ('waiting','Waiting for Verification'),
            ('confirm','Verified'),
        ],'Server Status', select=True, readonly=True),
        'active' : fields.boolean("Active"),
        'date_create': fields.date('Date Create', required=True, readonly=True, states={'new':[('readonly',False)]}),
        'test_email' : fields.text('Test Message'),
        'body' : fields.text('Message', help="The message text that will be send along with the email which is send through this server"),
        'verify_email' : fields.text('Verify Message', readonly=True, states={'new':[('readonly',False)]}),
        'code' : fields.char('Verification Code', size=1024),
        'type' : fields.selection([("default", "Default"),("account", "Account"),("sale","Sale"),("stock","Stock")], "Server Type",required=True),
        'history_line': fields.one2many('email.smtpclient.history', 'server_id', 'History'),
        'server_statistics': fields.one2many('report.smtp.server', 'server_id', 'Statistics')
    }
    
    _defaults = {
        'date_create': lambda *a: time.strftime('%Y-%m-%d'),
        'state': lambda *a: 'new',
        'active':lambda *a: 1,
        'verify_email': lambda *a: _("Verification Message. This is the code\n\n__code__\n\nyou must copy in the OpenERP Email Server (Verify Server wizard).\n\nCreated by user __user__"),
    }
    server = {}
    smtpServer = {}
    
#    def read(self,cr, uid, ids, fields=None, context=None, load='_classic_read'):
#        def override_password(o):
#            for field in o[0]:
#                if field == 'password':
#                    o[0][field] = '********'
#            return o
#        
#        result = super(SmtpClient, self).read(cr, uid, ids, fields, context, load)
#        result = override_password(result)
#        return result
    
#    def write(self, cr, user, ids, vals, context=None):
#        flag = False
#        if vals.get('password', False) != False:
#            for pass_char in vals.get('password'):
#                if pass_char != '*':
#                    flag= True
#                    break
#
#            if flag:    
#                vals['password'] = base64.b64encode(vals.get('password'))
#            else:
#                del vals['password']    
#            
#        res = super(SmtpClient, self).write(cr, user, ids, vals, context)
#        return res
            
    def change_email(self, cr, uid, ids, email):
        ptrn = re.compile('(\w+@\w+(?:\.\w+)+)')
        result=ptrn.search(email)
        if not result:
            raise osv.except_osv(_('Error !'),_('Verify the email address for this server'))
        else:
            user = email[0:email.index('@')]
            return {'value':{'user':user}}
        
    def check_permissions(self, cr, uid, ids):
        cr.execute('select * from res_smtpserver_group_rel where sid=%s and uid=%s' % (ids[0], uid))
        data = cr.fetchall()
        if len(data) <= 0:
            return False
        
        return True
    
    def gen_private_key(self, cr, uid, ids):
        new_key = []
        for i in time.strftime('%Y-%m-%d %H:%M:%S'):
            ky = i
            if ky in (' ', '-', ':'):
                keys = random.random()
                key = str(keys).split('.')[1]
                ky = key
                
            new_key.append(ky)
        new_key.sort()
        key = ''.join(new_key)
        return key
        
    def test_verify_email(self, cr, uid, ids, toemail, test=False, code=False):
        for serverid in ids:
            self.open_connection(cr, uid, ids, serverid)

            if test and self.server[serverid]['state'] != 'confirm':
                pooler.get_pool(cr.dbname).get('email.smtpclient.history').create \
                    (cr, uid, {'date_create':time.strftime('%Y-%m-%d %H:%M:%S'),'server_id' : serverid,'name':_('Please verify Email Server, without verification you can not send Email(s).')})
                raise osv.except_osv(_('Server Error!'), _('Please verify Email Server, without verification you can not send Email(s).'))
            key = False
            if test and self.server[serverid]['state'] == 'confirm':
                body = tools.ustr(self.server[serverid]['test_email'])
            else:
                body = tools.ustr(self.server[serverid]['verify_email'])
                #ignore the code
                key = self.gen_private_key(cr, uid, serverid)
                #md5(time.strftime('%Y-%m-%d %H:%M:%S') + toemail).hexdigest();
                body = body.replace("__code__", key)
                self.write(cr, uid, [serverid], {'code':key})
                
            user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, [uid])[0]
            body = body.replace("__user__", user.name)
            
            if len(body.strip()) <= 0:
                raise osv.except_osv(_('Message Error!'), _('Please configure Email Server Messages [Verification / Test]'))
          
            try:
                msg = MIMEText(body.encode('utf8') or '',_subtype='plain',_charset='utf-8')
            except:
                msg = MIMEText(body or '',_subtype='plain',_charset='utf-8')
            
            if not test and not self.server[serverid]['state'] == 'confirm':
                msg['Subject'] = _('OpenERP SMTP server Email Registration Code!')
            else:
                msg['Subject'] = _('OpenERP Test Email!')
                
            
            msg['To'] = toemail
            msg['From'] = tools.ustr(self.server[serverid]['from_email'])
            
            message = msg.as_string()
            
            queue = pooler.get_pool(cr.dbname).get('email.smtpclient.queue')
            queue.create(cr, uid, {
                    'to':toemail,
                    'server_id':serverid,
                    'name':msg['Subject'],
                    'body':body,
                    'serialized_message':message,
                })
        return True
        
    def open_connection(self, cr, uid, ids, serverid=False, permission=True):
        if serverid:
            self.server[serverid] = self.read(cr, uid, [serverid])[0]
        else:
            raise osv.except_osv(_('Read Error!'), _('Unable to read Server Settings'))
        
        if permission:
            if not self.check_permissions(cr, uid, [serverid]):
                raise osv.except_osv(_('Permission Error!'), _('You have no permission to access SMTP Server : %s ') % (self.server[serverid]['name'],) )

        if self.server[serverid]:
            try:
                self.smtpServer[serverid] = smtplib.SMTP()
                self.smtpServer[serverid].debuglevel = self.server[serverid]['use_debug']
                self.smtpServer[serverid].connect(str(self.server[serverid]['server']),str(self.server[serverid]['port']))
                if self.server[serverid]['ssl']:
                    self.smtpServer[serverid].ehlo()
                    self.smtpServer[serverid].starttls()
                    self.smtpServer[serverid].ehlo()
                if self.server[serverid]['use_auth']:
                    self.smtpServer[serverid].login(str(self.server[serverid]['user']),str(self.server[serverid]['password']))
            except Exception, e:
                raise osv.except_osv(_('SMTP Server Error!'), e)
            
        return True
    
    def selectAddress(self, cr, uid, partner=None, contact=None, ):
        email = 'none@none.com'
        if partner is None and contact is None:
            return 'none@none.com'
         
        if partner is not None and contact is None:
            pool = self.pool.get('res.partner')
            data = pool.read(cr, uid, [partner])[0]
            if data:
                contact = data['address']

        if contact is not None:
            pool = self.pool.get('res.partner.address')
            data = pool.read(cr, uid, contact)[0]
            email = data['email']
        
        return email
    
    def select(self, cr, uid, type):
        pool = self.pool.get('email.smtpclient')
        ids = pool.search(cr, uid, [('type','=',type)], context=False)
        if not ids:
            ids = pool.search(cr, uid, [('type','=','default')], context=False)
        
        if not ids:
            return False
        
        return ids[0]

    def send_email(self, cr, uid, server_id, emailto, subject, body=False, attachments=[], reports=[]):
    
        def createReport(cr, uid, report, ids):
            files = []
            for id in ids:
                #try:
                service = netsvc.LocalService(report)
                (result, format) = service.create(cr, uid, [id], {}, {})
                report_file = '/tmp/'+ str(id) + '.pdf'
                fp = open(report_file,'wb+')
                try:
                    fp.write(result);
                finally:
                    fp.close();
                files += [report_file]    
                #except Exception,e:
            return files
            
        smtp_server = self.browse(cr, uid, server_id)
        if smtp_server.state != 'confirm':
            raise osv.except_osv(_('SMTP Server Error !'), _('Server is not Verified, Please Verify the Server !'))
            
        if type(emailto) == type([]):
            for to in emailto:
                msg = MIMEMultipart()
                msg['Subject'] = tools.ustr(subject) 
                msg['To'] =  to
                msg['From'] = smtp_server.from_email
                try:
                    msg.attach(MIMEText(body.encode('utf8') or '', _charset='utf-8', _subtype="html"))
                except:
                    msg.attach(MIMEText(body or '', _charset='utf-8', _subtype="html"))
                
                for rpt in reports:
                    rpt_file = createReport(cr, uid, rpt[0], rpt[1])
                    attachments += rpt_file
                
                for file in attachments:
                    part = MIMEBase('application', "octet-stream")
                    f = open(file, "rb")
                    try:
                        payload = f.read()
                    finally:
                        f.close()
                    part.set_payload( payload )
                    Encoders.encode_base64(part)
                    part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
                    msg.attach(part)
                
                message = msg.as_string()
                
                queue = pooler.get_pool(cr.dbname).get('email.smtpclient.queue')
                queue.create(cr, uid, {
                        'to':to,
                        'server_id':server_id,
                        'cc':False,
                        'bcc':False,
                        'name':subject,
                        'body':body,
                        'serialized_message':message,
                    })
        else:
            msg = MIMEMultipart()
            msg['Subject'] = tools.ustr(subject) 
            msg['To'] =  emailto
            msg['From'] = smtp_server.from_email
            try:
                msg.attach(MIMEText(body.encode('utf8') or '', _charset='utf-8', _subtype="html"))
            except:
                msg.attach(MIMEText(body or '', _charset='utf-8', _subtype="html"))    
            
            for rpt in reports:
                rpt_file = createReport(cr, uid, rpt[0], rpt[1])
                attachments += rpt_file
            
            for file in attachments:
                part = MIMEBase('application', "octet-stream")
                f = open(file, "rb")
                try:
                    payload = f.read()
                finally:
                    f.close()
                part.set_payload( payload )
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
                msg.attach(part)
            
            message = msg.as_string()
            
            queue = pooler.get_pool(cr.dbname).get('email.smtpclient.queue')
            queue.create(cr, uid, {
                    'to':emailto,
                    'server_id':server_id,
                    'cc':False,
                    'bcc':False,
                    'name':subject,
                    'body':body,
                    'serialized_message':message,
                })
        
        return True
            
    def _check_queue(self, cr, uid, ids=False, context={}):
        import tools
        
        queue = self.pool.get('email.smtpclient.queue')
        history = self.pool.get('email.smtpclient.history')
        sids = queue.search(cr, uid, [('state','not in',['send','sending'])], limit=30)
        queue.write(cr, uid, sids, {'state':'sending'})
        sent = []
        open_server = []
        for email in queue.browse(cr, uid, sids):
            if not email.server_id.id in open_server:
                open_server.append(email.server_id.id)
                self.open_connection(cr, uid, ids, email.server_id.id)
                
            try:
                self.smtpServer[email.server_id.id].sendmail(str(email.server_id.email), email.to, tools.ustr(email.serialized_message))
            except Exception, e:
                queue.write(cr, uid, [email.id], {'error':e, 'state':'error'})
                continue
            
            history.create(cr, uid, {
                        'name':email.body,
                        'user_id':uid,
                        'server_id': email.server_id.id,
                        'email':email.to
                    })
            sent.append(email.id)
            queue.write(cr, uid, sent, {'state':'send'})
            smtpclient_state = self.read(cr, uid, [email.server_id.id], ['state'])
            if smtpclient_state[0]['state'] == 'new':
                self.write(cr, uid, email.server_id.id, {'state':'waiting'})
        return True
SmtpClient()

class HistoryLine(osv.osv):
    _name = 'email.smtpclient.history'
    _description = 'Email Client History'
    _columns = {
        'name' : fields.text('Description',required=True, readonly=True),
        'date_create': fields.datetime('Date',readonly=True),
        'user_id':fields.many2one('res.users', 'Username', readonly=True, select=True),
        'server_id' : fields.many2one('email.smtpclient', 'Smtp Server', ondelete='set null', readonly=True, required=True),
        'model':fields.many2one('ir.model', 'Model', readonly=True, select=True),
        'resource_id':fields.integer('Resource ID', readonly=True),
        'email':fields.char('Email',size=64,readonly=True),
    }
    
    _defaults = {
        'date_create': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda obj, cr, uid, context: uid,
    }
    
    def create(self, cr, uid, vals, context=None):
        super(HistoryLine,self).create(cr, uid, vals, context)
        cr.commit()
HistoryLine()

class MessageQueue(osv.osv):
    _name = 'email.smtpclient.queue'
    _description = 'Email Queue'
    _columns = {
        'to' : fields.char('Mail to', size=1024, readonly=True, states={'draft':[('readonly',False)], 'error':[('readonly',False)]}),
        'server_id':fields.many2one('email.smtpclient', 'SMTP Server', readonly=True, states={'draft':[('readonly',False)]}),
        'cc' : fields.char('CC to', size=1024, readonly=True, states={'draft':[('readonly',False)]}),
        'bcc' : fields.char('BCC to', size=1024, readonly=True, states={'draft':[('readonly',False)]}),
        'name' : fields.char('Subject', size=1024, readonly=True, states={'draft':[('readonly',False)]}),
        'body' : fields.text('Email Text', readonly=True, states={'draft':[('readonly',False)]}),
        'serialized_message':fields.text('Message', readonly=True, states={'draft':[('readonly',False)]}),
        'state':fields.selection([
            ('draft','Queued'),
            ('sending','Waiting'),
            ('send','Sent'),
            ('error','Error'),
        ],'Message Status', select=True, readonly=True),
        'error':fields.text('Last Error', size=256, readonly=True, states={'draft':[('readonly',False)]}),
        'date_create': fields.datetime('Date', readonly=True),
    }
    _defaults = {
        'date_create': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'state': lambda *a: 'draft',
    }
MessageQueue()

class report_smtp_server(osv.osv):
    _name = "report.smtp.server"
    _description = "Server Statistics"
    _auto = False
    _columns = {
        'server_id':fields.many2one('email.smtpclient','Server ID',readonly=True),
        'name': fields.char('Server',size=64,readonly=True),
        'history':fields.char('History',size=64, readonly=True),
        'no':fields.integer('Total No.',readonly=True),
    }
    def init(self, cr):#    def write(self, cr, user, ids, vals, context=None):
#        flag = False
#        if vals.get('password', False) != False:
#            for pass_char in vals.get('password'):
#                if pass_char != '*':
#                    flag= True
#                    break
#
#            if flag:    
#                vals['password'] = base64.b64encode(vals.get('password'))
#            else:
#                del vals['password']    
#            
#        res = super(SmtpClient, self).write(cr, user, ids, vals, context)
#        return res
         cr.execute("""
            create or replace view report_smtp_server as (
                   select min(h.id) as id, c.id as server_id, h.name as history, h.name as name, count(h.name) as no  from email_smtpclient c inner join email_smtpclient_history h on c.id=h.server_id group by h.name, c.id
                              )
         """)
report_smtp_server()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

