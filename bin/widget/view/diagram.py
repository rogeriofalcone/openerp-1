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

from interface import parser_view

class ViewDiagram(parser_view):

    def __init__(self, window, screen, widget, children=None, buttons=None,
            toolbar=None, submenu=None, help={}):
        super(ViewDiagram, self).__init__(window, screen, widget, children,
                buttons, toolbar, submenu)
        self.view_type = 'diagram'
        self.view = widget
        self.model_add_new = False
        self.widget = widget.widget
        self.view.screen = screen

    def cancel(self):
        pass

    def __str__(self):
        return 'ViewDiagram (%s)' % self.screen.resource

    def __getitem__(self, name):
        return None

    def set_value(self):
        pass

    def reset(self):
        pass

    def reset(self):
        pass

    def display(self):
        self.view.display()
        return None

    def signal_record_changed(self, *args):
        pass

    def sel_ids_get(self):
        return []

    def on_change(self, callback):
        pass

    def unset_editable(self):
        pass

    def set_cursor(self, new=False):
        pass
    
    def destroy(self):
        self.widget.destroy()
        del self.screen
        del self.widget

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

