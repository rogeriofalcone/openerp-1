##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

import time
import datetime as DT
import gtk
import common
import gettext
import locale
import wid_int

DT_FORMAT = '%Y-%m-%d'

if not hasattr(locale, 'nl_langinfo'):
	locale.nl_langinfo = lambda *a: '%x'

if not hasattr(locale, 'D_FMT'):
	locale.D_FMT = None

class calendar(wid_int.wid_int):
	def __init__(self, name, parent, attrs={}):
		wid_int.wid_int.__init__(self, name, parent, attrs)

		tooltips = gtk.Tooltips()
		self.widget = gtk.HBox(spacing=3)

		self.entry1 = gtk.Entry()
		self.entry1.set_property('width-chars', 10)
		self.entry1.set_property('activates_default', True)
		tooltips.set_tip(self.entry1, _('Start date'))
		self.widget.pack_start(self.entry1, expand=False, fill=True)

		self.eb1 = gtk.EventBox()
		tooltips.set_tip(self.eb1, _('Open the calendar widget'))
		self.eb1.set_events(gtk.gdk.BUTTON_PRESS)
		self.eb1.connect('button_press_event', self.cal_open, self.entry1, parent)
		img = gtk.Image()
		img.set_from_stock('gtk-zoom-in', gtk.ICON_SIZE_MENU)
		img.set_alignment(0.5, 0.5)
		self.eb1.add(img)
		self.widget.pack_start(self.eb1, expand=False, fill=False)

		self.widget.pack_start(gtk.Label('-'), expand=False, fill=False)

		self.entry2 = gtk.Entry()
		self.entry2.set_property('width-chars', 10)
		self.entry2.set_property('activates_default', True)
		tooltips.set_tip(self.entry2, _('End date'))
		self.widget.pack_start(self.entry2, expand=False, fill=True)

		self.eb2 = gtk.EventBox()
		tooltips.set_tip(self.eb2, _('Open the calendar widget'))
		self.eb2.set_events(gtk.gdk.BUTTON_PRESS)
		self.eb2.connect('button_press_event', self.cal_open, self.entry2, parent)
		img = gtk.Image()
		img.set_from_stock('gtk-zoom-in', gtk.ICON_SIZE_MENU)
		img.set_alignment(0.5, 0.5)
		self.eb2.add(img)
		self.widget.pack_start(self.eb2, expand=False, fill=False)

		tooltips.enable()

	def _date_get(self, str):
		try:
			date = time.strptime(str, locale.nl_langinfo(locale.D_FMT).replace('%y', '%Y'))
		except:
			return False
		return time.strftime(DT_FORMAT, date)

	def _value_get(self):
		res = []
		val = self.entry1.get_text()
		if val:
			res.append((self.name, '>=', self._date_get(val)))
		val = self.entry2.get_text()
		if val:
			res.append((self.name, '<=', self._date_get(val)))
		return res

	def _value_set(self, value):
		pass

	value = property(_value_get, _value_set, None, _('The content of the widget or ValueError if not valid'))

	def cal_open(self, widget, event, dest, parent=None):
		win = gtk.Dialog(_('Tiny ERP - Date selection'), parent,
				gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
				(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
				gtk.STOCK_OK, gtk.RESPONSE_OK))

		cal = gtk.Calendar()
		cal.display_options(gtk.CALENDAR_SHOW_HEADING|gtk.CALENDAR_SHOW_DAY_NAMES|gtk.CALENDAR_SHOW_WEEK_NUMBERS)
		cal.connect('day-selected-double-click', lambda *x: win.response(gtk.RESPONSE_OK))
		win.vbox.pack_start(cal, expand=True, fill=True)
		win.show_all()

		try:
			val = self._date_get(dest.get_text())
			if val:
				cal.select_month(int(val[5:7])-1, int(val[0:4]))
				cal.select_day(int(val[8:10]))
		except ValueError:
			pass

		response = win.run()
		if response == gtk.RESPONSE_OK:
			year, month, day = cal.get_date()
			dt = DT.date(year, month+1, day)
			dest.set_text(dt.strftime(locale.nl_langinfo(locale.D_FMT).replace('%y', '%Y')))
		win.destroy()

	def clear(self):
		self.value = ''

	def sig_activate(self, fct):
		self.entry1.connect_after('activate', fct)
		self.entry2.connect_after('activate', fct)
