###############################################################################
#
# Copyright (C) 2007-TODAY Tiny ERP Pvt Ltd. All Rights Reserved.
#
# $Id$
#
# Developed by Tiny (http://openerp.com) and Axelor (http://axelor.com).
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import time
import datetime
import calendar
import xml.dom.minidom

import cherrypy
import turbogears as tg

from openerp import rpc
from openerp import tools
from openerp.utils import TinyDict

from openerp.widgets import interface

from base import TinyCalendar

from utils import Day
from utils import Week
from utils import Month

class MiniCalendar(tg.widgets.CompoundWidget, interface.TinyWidget):
    template = 'openerp.widgets.tinycalendar.templates.mini'
    params = ['selected_day', 'month', 'forweek', 'highlight']
    
    month = None
    selected_day = None
    forweek = False
    highlight = True
        
    def __init__(self, selected_day, forweek=False, highlight=True):        
        self.month = Month(selected_day.year, selected_day.month)
        self.selected_day = selected_day
        self.forweek = forweek
        self.highlight = highlight
        
class GroupBox(tg.widgets.CompoundWidget, interface.TinyWidget):
    template = 'openerp.widgets.tinycalendar.templates.groups'
    params = ["colors", "color_values", "title"]
        
    colors = {}
    color_values = []
    title = None
    action = None
        
    def __init__(self, colors, color_values, selected_day, title=None, mode='month'):
        self.colors = colors
        self.color_values = color_values
        self.title = title
        
def get_calendar(model, view, ids=None, domain=[], context={}, options=None):
        
    mode = (options or None) and options.mode
    if not mode:
        dom = xml.dom.minidom.parseString(view['arch'].encode('utf-8'))
        attrs = tools.node_attributes(dom.childNodes[0])
        mode = attrs.get('mode')
    
    if mode == 'day':
        return DayCalendar(model, view, ids, domain, context, options)
        
    if mode == 'week':
        return WeekCalendar(model, view, ids, domain, context, options)
    
    return MonthCalendar(model, view, ids, domain, context, options)

class MonthCalendar(TinyCalendar):

    template = 'openerp.widgets.tinycalendar.templates.month'
    params = ['month', 'events', 'selected_day', 'calendar_fields', 'date_format']
    member_widgets = ['minical', 'groupbox', 'use_search']    

    month = None
    events = {}
    
    minical = None
    groupbox = None    

    def __init__(self, model, view, ids=None, domain=[], context={}, options=None):
        
        TinyCalendar.__init__(self, model, ids, view, domain, context, options)                
        
        y, m = time.localtime()[:2]
        if options:
            y = options.year
            m = options.month

        self.month = Month(y, m)
        self.events = self.get_events([d for d in self.month])
        
        if not self.selected_day:
            sd = Day.today()
            if sd.year == y and sd.month == m:
                self.selected_day = sd
            else:
                self.selected_day = Day(y, m, 1)

        if not (self.selected_day.year == y and self.selected_day.month == m):
            self.minical = MiniCalendar(Day(y, m, 1))
        else:
            self.minical = MiniCalendar(self.selected_day)
            
        self.groupbox = GroupBox(self.colors, self.color_values, self.selected_day, title=(self.color_field or None) and self.fields[self.color_field]['string'], mode='month')
            
            
class WeekCalendar(TinyCalendar):
    template = 'openerp.widgets.tinycalendar.templates.week'
    params = ['week', 'events', 'selected_day', 'calendar_fields', 'date_format']
    member_widgets = ['minical', 'groupbox', 'use_search']
    
    week = None
    events = {}
    
    minical = None
         
    def __init__(self, model, view, ids=None, domain=[], context={}, options=None):            
        TinyCalendar.__init__(self, model, ids, view, domain, context, options)

        y, m, d = time.localtime()[:3]
        if options:
            y, m, d = options.date1[:3]
                        
        self.week = Week(Day(y,m,d))
        
        self.events = self.get_events([d for d in self.week])        
        self.selected_day = self.selected_day or self.week[0]

        self.minical = MiniCalendar(self.week[0], True)
        self.groupbox = GroupBox(self.colors, self.color_values, self.week[0], title=(self.color_field or None) and self.fields[self.color_field]['string'], mode='week')

class DayCalendar(TinyCalendar):
    template = 'openerp.widgets.tinycalendar.templates.day'
    params = ['day', 'events', 'calendar_fields', 'date_format']
    member_widgets = ['minical', 'groupbox', 'use_search']
    
    day = None
    events = {}
    
    minical = None
         
    def __init__(self, model, view, ids=None, domain=[], context={}, options=None):            
        TinyCalendar.__init__(self, model, ids, view, domain, context, options)
        
        y, m, d = time.localtime()[:3]
        if options:
            y, m, d = options.date1[:3]
                     
        self.day = Day(y,m,d)

        self.events = self.get_events([self.day])        
        self.minical = MiniCalendar(self.day)
        self.groupbox = GroupBox(self.colors, self.color_values, self.day, title=(self.color_field or None) and self.fields[self.color_field]['string'], mode='day')

class GanttCalendar(MonthCalendar):
    template = 'openerp.widgets.tinycalendar.templates.gantt'

    def __init__(self, model, view, ids, domain=[], context={}, options=None):
        super(GanttCalendar, self).__init__(model, view, ids, domain, context, options)

# vim: ts=4 sts=4 sw=4 si et

