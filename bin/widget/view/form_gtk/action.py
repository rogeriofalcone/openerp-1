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

import gtk

import gettext
import common
from common import openerp_gtk_builder
import wid_common

import interface
from widget.screen import Screen

import rpc
import tools
import time
from modules.gui.window.win_search import win_search
import service
import datetime

class action(interface.widget_interface):
    def __init__(self, window, parent, model, attrs={}):
        interface.widget_interface.__init__(self, window, parent, model, attrs)

        self.act_id = int(attrs['name'])
        res = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.actions.actions', 'read', [self.act_id], ['type'], rpc.session.context)
        if not res:
            raise Exception, 'ActionNotFound'
        type = res[0]['type']
        self.action = rpc.session.rpc_exec_auth('/object', 'execute', type, 'read', [self.act_id], False, rpc.session.context)[0]
        if 'view_mode' in attrs:
            self.action['view_mode'] = attrs['view_mode']
        self.action_view_ids = False
        if self.action['type'] == 'ir.actions.act_window':
            if not self.action.get('domain', False):
                self.action['domain'] = '[]'
            if attrs.get('domain',False):
                self.action['domain'] = attrs.get('domain')
            self.context = {'active_id': False, 'active_ids': []}
            self.context.update(tools.expr_eval(self.action.get('context', '{}'), self.context.copy()))
            self.domain = tools.expr_eval(self.action['domain'], self.context.copy())
            view_id = []
            if self.action['view_id']:
                view_id = [self.action['view_id'][0]]
            if self.action.get('views'):
                self.action_view_ids = map(lambda y:y[0], filter(lambda x:x[1] == 'tree',self.action['views']))
            if self.action['view_type']=='form':
                mode = (self.action['view_mode'] or 'form,tree').split(',')
                if not view_id:
                    view_id = map(lambda y:y[0], filter(lambda x:x[1] == mode[0],self.action['views']))
                for extra_mode in mode[1:]:
                    view_id.extend(map(lambda y:y[0], filter(lambda x:x[1] == extra_mode, self.action['views'])))
                self.screen = Screen(self.action['res_model'], view_type=mode, context=self.context, view_ids = view_id, domain=self.domain)
                self.ui = openerp_gtk_builder('openerp.ui', ['widget_paned'])
                self.ui.connect_signals({
                    'on_switch_button_press_event': self._sig_switch,
                    'on_search_button_press_event': self._sig_search,
                    'on_open_button_press_event': self._sig_open,
                })
                label = self.ui.get_object('widget_paned_lab')
                label.set_text(attrs.get('string', self.screen.current_view.title))
                vbox = self.ui.get_object('widget_paned_vbox')
                vbox.add(self.screen.widget)
                self.widget = self.ui.get_object('widget_paned')
                self.widget.set_size_request(int(attrs.get('width', -1)), int(attrs.get('height', -1)))
            elif self.action['view_type']=='tree':
                pass #TODO

    def _sig_switch(self, *args):
        self.screen.switch_view()

    def _sig_search(self, *args):
        win = win_search(self.action['res_model'], view_ids = self.action_view_ids, domain=self.domain, context=self.context)
        res = win.go()
        if res:
            self.screen.clear()
            self.screen.load(res)

    def _sig_open(self, *args):
        obj = service.LocalService('action.main')
        obj.execute(self.act_id, datas={}, type=None, context={})

    def set_value(self, mode, model_field):
        self.screen.current_view.set_value()
        return True

    def display(self, model, model_field):
        limit = self.screen.current_view.view_type != 'graph' and self.action.get('limit', 100)  or False
        res_id = rpc.session.rpc_exec_auth('/object', 'execute',
                self.action['res_model'], 'search', self.domain, 0,
                limit, False, self.context)
        self.screen.clear()
        self.screen.load(res_id)
        return True




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

