# -*- encoding: utf-8 -*-
#
#  webkit_report.py
#
#  Created by Nicolas Bessi  
#  Some code is taken from report_openoffice module
#
#  Copyright (c) 2010 CamptoCamp. All rights reserved.
##############################################################################
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
"""Implement report printing mechanisms"""
import sys
import platform
import os
import tempfile
import report
from report.report_sxw import *
from osv import osv
from tools.translate import _
import time
from mako.template import Template
import pooler
from report_helper import WebKitHelper
import netsvc
import pooler
from tools.config import config
import commands
logger = netsvc.Logger()



class WebKitParser(report_sxw):
    """Custom class that use webkit to render HTML reports
       Code partially taken from report openoffice. Thanks guys :)
    """

    def __init__(self, name, table, rml=False, parser=False, 
        header=True, store=False):
        self.parser_instance = False
        report_sxw.__init__(self, name, table, rml, parser, 
            header, store)

        
    def get_lib(self) :
        """Return the lib wkhtml path"""
        #TODO Detect lib in system first
        curr_sys = platform.system()
        sysmapping = {
                    'Linux': 'wkhtmltopdf-linux-i386-0-9-9',
                    'Darwin': 'wkhtmltopdf-0.9.9-OS-X.i368',
                    'Windows' : os.path.join('wkhtmltopdf', 'wkhtmltopdf.exe')
                        
                     }
        if not curr_sys in sysmapping.keys() :
            raise osv.except_osv(
                                    _('Your system is not yet supported'), 
                                    _('You can try to install wkhtmltopdf')
                                )
        path = os.path.join(
                                config['addons_path'], 
                                'webkit_report', 
                                'lib', 
                                sysmapping[curr_sys]
                            )
        if not os.path.exists(path) :
            raise osv.except_osv(
            _('Can not find wkhtmltopdf binary' ), 
            _('You can try to install it into the webkil_report lib folder')
            )
        return path
        
        
    def genreate_pdf(self, comm_path, report_xml, header, footer, html_list):
        """Call webkit in order to generate pdf"""
        tmp_dir = tempfile.gettempdir()
        out = report_xml.name+str(time.time())+'.pdf'
        out = os.path.join(tmp_dir, out.replace(' ',''))
        files = []
        file_to_del = []
        try:
            command = [comm_path]
            command.append('-q')
            if header :
                head_file = file(
                                    os.path.join(
                                      tmp_dir,
                                      str(time.time()) + '.head.html'
                                     ), 
                                    'w'
                                )
                head_file.write(header)
                head_file.close()
                file_to_del.append(head_file.name)
                command.append("--header-html '%s'"%(head_file.name))
            if footer :
                foot_file = file(
                                    os.path.join(
                                      tmp_dir,
                                      str(time.time()) + '.foot.html'
                                     ), 
                                    'w'
                                )
                foot_file.write(footer)
                foot_file.close()
                file_to_del.append(foot_file.name)
                command.append("--footer-html '%s'"%(foot_file.name))
            if report_xml.webkit_header.margin_top :
                command.append('--margin-top %s'%(report_xml.webkit_header.margin_top))
            if report_xml.webkit_header.magrin_bottom :
                command.append('--margin-bottom %s'%(report_xml.webkit_header.magrin_bottom))
            if report_xml.webkit_header.magrin_left :
                command.append('--margin-left %s'%(report_xml.webkit_header.magrin_left))
            if report_xml.webkit_header.magrin_right :
                command.append('--margin-right %s'%(report_xml.webkit_header.magrin_right))
            if report_xml.webkit_header.orientation :
                command.append("--orientation '%s'"%(report_xml.webkit_header.orientation))
            if report_xml.webkit_header.format :
                command.append(" --page-size '%s'"%(report_xml.webkit_header.format))    
            for html in html_list :
                html_file = file(os.path.join(tmp_dir, str(time.time()) + '.body.html'), 'w')
                html_file.write(html)
                html_file.close()
                file_to_del.append(html_file.name)
                command.append(html_file.name)
            command.append(out)
            generate_command = ' '.join(command)
            try:
                status = commands.getstatusoutput(generate_command)
                if status[0] :
                    raise osv.except_osv(
                                    _('Webkit raise an error' ), 
                                    status[1]
                                )
            except Exception, exc:
                try:
                    for f_to_del in file_to_del :
                        os.unlink(f_to_del)
                except Exception, exc:
                    pass
        except Exception, exc:
            raise exc

        pdf = file(out).read()
        try:
            for f_to_del in file_to_del :
                os.unlink(f_to_del)
        except Exception, exc:
            pass
        os.unlink(out)
        return pdf
             
        
        

    # override needed to keep the attachments' storing procedure
    def create_single_pdf(self, cursor, uid, ids, data, report_xml, 
        context=None):
        """generate the PDF"""
        self.parser_instance = self.parser(
                                            cursor, 
                                            uid, 
                                            self.name2, 
                                            context=context
                                        )
        self.pool = pooler.get_pool(cursor.dbname)
        objs = self.getObjects(cursor, uid, ids, context)
        self.parser_instance.set_context(objs, data, ids, report_xml.report_type)
        template =  False
        if report_xml.report_webkit :
            path = os.path.join(config['addons_path'], report_xml.report_webkit)
            if os.path.exists(path) :
                template = file(path).read()
        if not template and report_xml.report_webkit_data :
            template =  report_xml.report_webkit_data
        if not template :
            raise osv.except_osv(_('Report template not found !'), _(''))
        header = report_xml.webkit_header.html
        footer = report_xml.webkit_header.footer_html
        if not header and report_xml.header:
            raise osv.except_osv(
                _('No header defined for this report header html is empty !'), 
                _('look in company settings')
            )
        if not report_xml.header :
            #I know it could be cleaner ...
            header = u"""
<html>
    <head>
        <style type="text/css"> 
            ${css}
        </style>
        <script>
        function subst() {
           var vars={};
           var x=document.location.search.substring(1).split('&');
           for(var i in x) {var z=x[i].split('=',2);vars[z[0]] = unescape(z[1]);}
           var x=['frompage','topage','page','webpage','section','subsection','subsubsection'];
           for(var i in x) {
             var y = document.getElementsByClassName(x[i]);
             for(var j=0; j<y.length; ++j) y[j].textContent = vars[x[i]];
           }
         }
        </script>
    </head>
<body style="border:0; margin: 0;" onload="subst()">
</body>
</html>"""
        css = report_xml.webkit_header.css
        if not css :
            css = ''
        user = self.pool.get('res.users').browse(cursor, uid, uid)
        company= user.company_id
        #default_filters=['unicode', 'entity'] can be used to set global filter
        body_mako_tpl = Template(template ,input_encoding='utf-8')
        helper = WebKitHelper(cursor, uid, report_xml.id, context)
        html = body_mako_tpl.render(
                                    objects=self.parser_instance.localcontext['objects'], 
                                    company=company, 
                                    time=time, 
                                    helper=helper, 
                                    css=css,
                                    formatLang=self.parser_instance.formatLang,
                                    setLang=self.parser_instance.setLang,
                                    )
        head_mako_tpl = Template(header, input_encoding='utf-8')
        head = head_mako_tpl.render(
                                    company=company, 
                                    time=time, 
                                    helper=helper, 
                                    css=css,
                                    formatLang=self.parser_instance.formatLang,
                                    setLang=self.parser_instance.setLang, 
                                    _debug=False
                                )
        foot = False
        if footer :
            foot_mako_tpl = Template(footer ,input_encoding='utf-8')
            foot = foot_mako_tpl.render(
                                        company=company, 
                                        time=time, 
                                        helper=helper, 
                                        css=css, 
                                        formatLang=self.parser_instance.formatLang,
                                        setLang=self.parser_instance.setLang
                                        )
        if report_xml.webkit_debug :
            deb = head_mako_tpl.render(
                                        company=company, 
                                        time=time, 
                                        helper=helper, 
                                        css=css, 
                                        _debug=html,
                                        formatLang=self.parser_instance.formatLang,
                                        setLang=self.parser_instance.setLang
                                        )
            return (deb, 'html')
        bin = self.get_lib()
        pdf = self.genreate_pdf(bin, report_xml, head, foot, [html])
        return (pdf, 'pdf')

    def create_source_webkit(self, cursor, uid, ids, data, report_xml, context=None):
        """We override the create_source_webkit function in order to handle attachement
           Code taken from report openoffice. Thanks guys :) """
        if not context:
            context = {}
        pool = pooler.get_pool(cursor.dbname)
        attach = report_xml.attachment
        if attach:
            objs = self.getObjects(cursor, uid, ids, context)
            results = []
            for obj in objs:
                aname = eval(attach, {'object':obj, 'time':time})
                result = False
                if report_xml.attachment_use and aname and context.get('attachment_use', True):
                    aids = pool.get('ir.attachment').search(
                                                            cursor, 
                                                            uid,
                                                            [
                                                                ('datas_fname','=',aname+'.pdf'),
                                                                ('res_model','=',self.table),
                                                                ('res_id','=',obj.id)
                                                            ]
                                                        )
                    if aids:
                        brow_rec = pool.get('ir.attachment').browse(cursor, uid, aids[0])
                        if not brow_rec.datas:
                            continue
                        d = base64.decodestring(brow_rec.datas)
                        results.append((d,'odt'))
                        continue
                result = self.create_single_pdf(cursor, uid, [obj.id], data, report_xml, context)
                try:
                    if aname:
                        name = aname+'.'+result[1]
                        pool.get('ir.attachment').create(cursor, uid, {
                            'name': aname,
                            'datas': base64.encodestring(result[0]),
                            'datas_fname': name,
                            'res_model': self.table,
                            'res_id': obj.id,
                            }, context=context
                        )
                        cursor.commit()
                except Exception, exp:
                    import traceback, sys
                    tb_s = reduce(lambda x, y: x+y, traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback))
                    netsvc.Logger().notifyChannel(
                                                    'report', 
                                                    netsvc.LOG_ERROR, 
                                                    str(exp)
                                                )
                results.append(result)

        return self.create_single_pdf(
                                        cursor, 
                                        uid, 
                                        ids, 
                                        data, 
                                        report_xml, 
                                        context
                                    )

    def create(self, cursor, uid, ids, data, context=None):
        """We override the create function in order to handle generator
           Code taken from report openoffice. Thanks guys :) """
        pool = pooler.get_pool(cursor.dbname)
        ir_obj = pool.get('ir.actions.report.xml')
        report_xml_ids = ir_obj.search(cursor, uid,
                [('report_name', '=', self.name[7:])], context=context)
        if report_xml_ids:
            
            report_xml = ir_obj.browse(
                                        cursor, 
                                        uid, 
                                        report_xml_ids[0], 
                                        context=context
                                    )
            report_xml.report_rml = None
            report_xml.report_rml_content = None
            report_xml.report_sxw_content_data = None
            report_rml.report_sxw_content = None
            report_rml.report_sxw = None
        else:
            title = ''
            rml = tools.file_open(self.tmpl, subdir=None).read()
            report_type = data.get('report_type', 'pdf')
            class a(object):
                def __init__(self, *args, **argv):
                    for key, arg in argv.items():
                        setattr(self, key, arg)
            report_xml = a(title=title, report_type=report_type, report_rml_content=rml, name=title, attachment=False, header=self.header)
            
        report_type = report_xml.report_type
        if report_type in ['sxw', 'odt']:
            fnct = self.create_source_odt
        elif report_type in ['pdf', 'raw', 'html']:
            fnct = self.create_source_pdf
        elif report_type=='html2html':
            fnct = self.create_source_html2html
        elif report_type=='webkit':
            fnct = self.create_source_webkit
        else:
            raise 'Unknown Report Type'
        fnct_ret = fnct(cursor, uid, ids, data, report_xml, context)
        if not fnct_ret:
            return (False,False)
        return fnct_ret

def register_report(name, model, tmpl_path, parser):
    name = 'report.%s' % name
    if netsvc.service_exist( name ):
        #service = netsvc.SERVICES[name].parser
        if isinstance( netsvc.SERVICES[name], WebKitParser ):
            return
        del netsvc.SERVICES[name]
    WebKitParser(name, model, tmpl_path, parser=parser)
    
old_register_all = report.interface.register_all

def new_register_all(db):
    value = old_register_all(db)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM ir_act_report_xml")
    records = cursor.dictfetchall()
    cursor.close()
    for record in records:
        if record['report_type'] in ('webkit',):
            parser=rml_parse
            register_report( record['report_name'], record['model'], record['report_rml'], parser)
    return value

report.interface.register_all = new_register_all

