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


import gobject
import pango
import gtk
import re

import tools
from datetime import datetime
import tools.datetime_util
import time


class DateEntry(gtk.Entry):
    def __init__(self, format, callback=None, callback_process=None):
        super(DateEntry, self).__init__()
        self.modify_font(pango.FontDescription("monospace"))
        self.valid = True
        self.format = format
        self.small_format = self.regex = self.initial_value = self.convert_fmt(format)
        for key,val in tools.datetime_util.date_mapping.items():
            self.regex = self.regex.replace(key, val[1])
            self.initial_value = self.initial_value.replace(key, val[0])
            
        self.small_text = self.initial_value 
        self.set_text(self.initial_value)
        self.regex = re.compile(self.regex)

        assert self.regex.match(self.initial_value), 'Error, the initial value should be validated by regex'
        self.set_width_chars(len(self.initial_value))
        self.set_max_length(len(self.initial_value))

        self.connect('key-press-event', self._on_key_press)
        self.connect('insert-text', self._on_insert_text)
        self.connect('delete-text', self._on_delete_text)

        self.connect('focus-out-event', self._focus_out)
        self.connect('focus-in-event', self._focus_in)
        self.callback = callback
        self.callback_process = callback_process

        self._interactive_input = True
        self.mode_cmd = False
        gobject.idle_add(self.set_position, 0)
        self.set_tooltip_text(_('''You can use special operation by pressing +, - or =.  Plus/minus adds/decrease the variable to the current selected date. Equals set part of selected date. Available variables: 12h = 12 hours, 8d = 8 days, 4w = 4 weeks, 1m = 1 month, 2y = 2 years. Some examples:
* +21d : adds 21 days to selected year
* =23w : set date to the 23th week of the year
* -4m : decrease 4 months to the current date
You can also use "=" to set the date to the current date/time and '-' to clear the field.'''))

    def convert_fmt(self, fmt=''):
        """If format string doesn't contain
        any of the `%Y, %m or %d` then returns default datetime format `%Y/%m/%d`
        """
        for x,y in [('%y','%Y'),('%B','%m'),('%A',''), ('%I','%H'), ('%p',''), ('%j',''), ('%a',''), ('%b','%m'),
                    ('%U',''), ('%W','')]:
            fmt = fmt.replace(x, y)

        if (not (fmt.count('%Y') >= 1 and fmt.count('%m') >= 1 and fmt.count('%d') >= 1) or fmt.count('%x') >= 1) \
                and (fmt.count('%H') == 0 and fmt.count('%M') == 0 and fmt.count('%S') == 0 and fmt.count('%X') == 0): 
            return '%Y/%m/%d'
        
        elif not (fmt.count('%Y') >= 1 and fmt.count('%m') >= 1 and fmt.count('%d') >= 1) \
                or (fmt.count('%x') >=1 or fmt.count('%c') >= 1):
            return '%Y/%m/%d %H:%M:%S'
            

        return fmt

    def isvalid_date(self, text):
        self.valid = True
        try:
            return datetime.strptime(text, self.format)
        except:
            pass
            
        try:
            return datetime.strptime(text, self.small_format)
        except:
            self.valid = False
            return False
        
        
    def _on_insert_text(self, editable, value, length, position):
        if not self._interactive_input:
            return

        self.stop_emission('insert-text')
        if self.mode_cmd:
            if self.callback: self.callback(value)
            return 
        
        text = self.get_text()  
        current_pos = self.get_position()
        
        if(length + current_pos > len(text)) and text != self.initial_value:
            return
        
        pos = (current_pos < 10  or text != self.initial_value) and current_pos or 0

        if length != 1:
            return

        text = text[:pos] + value + text[pos + 1:]
        if self.regex.match(text):
            pos += 1
            while (pos<len(self.initial_value)) and (self.initial_value[pos] not in ['_','0','X']):
                pos += 1
            self.set_text(text)
            self.small_text = text
            gobject.idle_add(self.set_position, pos)
        self.show()
        return

    def _on_delete_text(self, editable, start, end):
        if not self._interactive_input:
            return

        #if end - start != 1:
        #    #TODO: cut/delete several
        #    self.stop_emission('delete-text')
        #    return
        while (start>0) and (self.initial_value[start] not in ['_','0','X']):
            start -= 1
        text = self.get_text()
        text = text[:start] + self.initial_value[start:end] + text[end:]
        self.set_text(text)
        self.small_text = text
        gobject.idle_add(self.set_position, start)
        self.stop_emission('delete-text')
        return

    def _focus_out(self, args, args2):
        date = self.isvalid_date(self.small_text)
        if date:
            large_text = date.strftime(self.format)
            self.set_text(large_text)
        else:
            self.set_text(self.small_text)
        if self.mode_cmd:
            self.mode_cmd = False
            if self.callback_process: self.callback_process(False, self, False)
            
    def _focus_in(self, args, args2):
        self.set_text(self.small_text)
        if self.mode_cmd:
            self.mode_cmd = False
            if self.callback_process: self.callback_process(False, self, False)

    def set_text(self, text):
        self._interactive_input = False
        try:
            self.set_max_length(len(text))
            gtk.Entry.set_text(self, text)
            date = self.isvalid_date(text);
            if(date):
                self.small_text = date.strftime(self.small_format)
            elif text == self.initial_value:
                self.small_text = self.initial_value
        finally:
            self._interactive_input = True
            
    def get_text(self):
        date = self.isvalid_date(self.small_text)
        if date and not self.is_focus():
            return date.strftime(self.format)
        return gtk.Entry.get_text(self)
            
    def get_value(self):
        date = self.isvalid_date(self.small_text)
        if date:
            return date.strftime(self.format)
        entered_value = gtk.Entry.get_text(self)
        if '_' not in entered_value:
            self.set_text(self.initial_value)
        return entered_value
        
    def date_set(self, dt):
        if dt:
            self.set_text(dt.strftime(self.format))
        else:
            self.set_text(self.initial_value)

    def date_get(self):
        tt = time.strftime(self.format, time.localtime())
        tc = self.get_text()
        if tc == self.initial_value:
            return False
        for a in range(len(self.initial_value)):
            if self.initial_value[a] == tc[a]:
                tc = tc[:a] + tt[a] + tc[a+1:]
        try:
            self.set_text(tc)
            return tools.datetime_util.strptime(tc, self.format)
        except:
            tc = tt
        self.set_text(tc)
        return tools.datetime_util.strptime(tc, self.format)

    def delete_text(self, start, end):
        self._interactive_input = False
        try:
            gtk.Entry.delete_text(self, start, end)
        finally:
            self._interactive_input = True

    def insert_text(self, text, position=0):
        self._interactive_input = False
        try:
            gtk.Entry.insert_text(self, text, position)
        finally:
            self._interactive_input = True

    def clear(self):
        if(self.valid):
            self.set_text(self.initial_value)

    def _on_key_press(self, editable, event):
        if event.keyval in (gtk.keysyms.Tab, gtk.keysyms.Escape, gtk.keysyms.Return, gtk.keysyms.KP_Enter):
            if self.mode_cmd:
                self.mode_cmd = False
                if self.callback_process: self.callback_process(False, self, event)
                self.stop_emission("key-press-event")
                return True
        elif event.keyval in (gtk.keysyms.KP_Add, gtk.keysyms.plus,
                              gtk.keysyms.KP_Subtract, gtk.keysyms.minus,
                              gtk.keysyms.KP_Equal, gtk.keysyms.equal):
                self.mode_cmd = True
                self.date_get()
                if self.callback_process: self.callback_process(True, self, event)
                self.stop_emission("key-press-event")
                return True
        elif self.mode_cmd:
            if self.callback: self.callback(event)
            return True
        return False

class CmdEntry(gtk.Label):
    pass

class ComplexEntry(gtk.HBox):
    def __init__(self, format, *args, **argv):
        super(ComplexEntry, self).__init__(*args, **argv)
        self.widget = DateEntry(
            format,
            self._date_cb,
            self._process_cb
        )
        self.widget.set_position(0)
        self.widget.select_region(0, 0)
        self.widget_cmd = CmdEntry()
        self.widget_cmd.hide()
        self.pack_start(self.widget, expand=True, fill=True)
        self.pack_start(self.widget_cmd, expand=False, fill=True)

    def _date_cb(self, event):
        if event.keyval in (gtk.keysyms.BackSpace,):
            text = self.widget_cmd.get_text()[:-1]
            self.widget_cmd.set_text(text)
            return True
        text = self.widget_cmd.get_text()
        self.widget_cmd.set_text(text + event.string)
        return True

    def _process_cb(self, ok, widget, event=None):
        if ok:
            self.widget_cmd.show()
            self._date_cb(event)
        else:
            data = self.widget.get_text()
            if (not event) or event.keyval != gtk.keysyms.Escape:
                cmd = self.widget_cmd.get_text()
                for r,f in tools.datetime_util.date_operation.items():
                    groups = re.match(r, cmd)
                    if groups:
                        dt = self.widget.date_get()
                        if not dt:
                            dt = time.strftime(self.widget.format, time.localtime())
                            dt = tools.datetime_util.strptime(dt, self.widget.format)
                        self.widget.date_set(f(dt,groups))
                        break

                # Compute HERE using DATA and setting WIDGET
                pass
            self.widget_cmd.set_text('')
            self.widget_cmd.hide()

if __name__ == '__main__':
    import sys
    def _(s):
        return s

    def main(args):
        win = gtk.Window()
        win.set_title('gtk.Entry subclass')
        def cb(window, event):
            gtk.main_quit()
        win.connect('delete-event', cb)

        widget = ComplexEntry('%d/%m/%Y %H:%M:%S')
        win.add(widget)

        win.show_all()
        gtk.main()

    sys.exit(main(sys.argv))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

