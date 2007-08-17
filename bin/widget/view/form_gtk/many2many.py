##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id$
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

import gobject
import gtk

import gettext

import copy

import wid_common
import common

from widget.screen import Screen
import interface

import rpc

from modules.gui.window.win_search import win_search

class many2many(interface.widget_interface):
	def __init__(self, window, parent, model, attrs={}):
		interface.widget_interface.__init__(self, window, parent, model, attrs)

		self.widget = gtk.VBox(homogeneous=False, spacing=1)

		hb = gtk.HBox(homogeneous=False, spacing=3)
		self.wid_text = gtk.Entry()
		self.wid_text.set_property('width_chars', 13)
		self.wid_text.connect('activate', self._sig_activate)
		self.wid_text.connect('button_press_event', self._menu_open)
		hb.pack_start(self.wid_text, expand=True, fill=True)

		hb.pack_start(gtk.VSeparator(), padding=2, expand=False, fill=False)

		self.wid_but_add = gtk.Button(stock='gtk-add')
		self.wid_but_add.set_relief(gtk.RELIEF_HALF)
		self.wid_but_add.set_focus_on_click(True)
		self.wid_but_add.connect('clicked', self._sig_add)
		hb.pack_start(self.wid_but_add, padding=3, expand=False, fill=False)

		self.wid_but_remove = gtk.Button(stock='gtk-remove')
		self.wid_but_remove.set_relief(gtk.RELIEF_HALF)
		self.wid_but_remove.set_focus_on_click(True)
		self.wid_but_remove.connect('clicked', self._sig_remove)
		hb.pack_start(self.wid_but_remove, expand=False, fill=False)

		self.widget.pack_start(hb, expand=False, fill=False)
		self.widget.pack_start(gtk.HSeparator(), expand=False, fill=True)

		scroll = gtk.ScrolledWindow()
		scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scroll.set_placement(gtk.CORNER_TOP_LEFT)
		scroll.set_shadow_type(gtk.SHADOW_NONE)

		self.screen = Screen(attrs['relation'], view_type=['tree'])
		scroll.add_with_viewport(self.screen.widget)
		self.widget.pack_start(scroll, expand=True, fill=True)

		self.old = None

	def destroy(self):
		self.screen.destroy()
		self.widget.destroy()
		del self.widget

	def _menu_sig_default(self, obj):
		res = rpc.session.rpc_exec_auth('/object', 'execute', self.attrs['model'], 'default_get', [self.attrs['name']])
		self.value = res.get(self.attrs['name'], False)

	def _sig_add(self, *args):
		domain = self._view.modelfield.domain_get(self._view.model)
		context = self._view.modelfield.context_get(self._view.model)

		ids = rpc.session.rpc_exec_auth('/object', 'execute', self.attrs['relation'], 'name_search', self.wid_text.get_text(), domain, 'ilike', context)
		ids = map(lambda x: x[0], ids)
		if len(ids)<>1:
			win = win_search(self.attrs['relation'], sel_multi=True, ids=ids, context=context, domain=domain, parent=self._window)
			ids = win.go()

		self.screen.load(ids)
		self.screen.display()
		self.wid_text.set_text('')

	def _sig_remove(self, *args):
		self.screen.remove()
		self.screen.display()

	def _sig_activate(self, *args):
		self._sig_add()

	def _readonly_set(self, ro):
		self.wid_text.set_editable(not ro)
		self.wid_text.set_sensitive(not ro)
		self.wid_but_remove.set_sensitive(not ro)
		self.wid_but_add.set_sensitive(not ro)

	def display(self, model, model_field):
		super(many2many, self).display(model, model_field)
		ids = []
		if model_field:
			ids = model_field.get_client(model)
		if ids<>self.old:
			self.screen.clear()
			self.screen.load(ids)
			self.old = ids
		self.screen.display()
		return True

	def set_value(self, model, model_field):
		model_field.set_client(model, [x.id for x in self.screen.models.models])

