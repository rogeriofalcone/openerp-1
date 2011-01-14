##############################################################################
#
# Copyright (c) 2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

from rpc import RPCProxy
import rpc
from record import ModelRecord
import field

import signal_event

try:
	a = set()
except NameError:
	from sets import Set as set

class ModelList(list):
	def __init__(self, screen):
		super(ModelList, self).__init__()
		self.lock_signal = False
		self.__screen = screen

	def insert(self, pos, obj):
		super(ModelList, self).insert(pos, obj)
		if not self.lock_signal:
			self.__screen.signal('record-changed', ('record-added', pos))

	def append(self, obj):
		super(ModelList, self).append(obj)
		if not self.lock_signal:
			self.__screen.signal('record-changed', ('record-added', -1))

	def remove(self, obj):
		idx = self.index(obj)
		super(ModelList, self).remove(obj)
		if not self.lock_signal:
			self.__screen.signal('record-changed', ('record-removed', idx))
	
	def clear(self):
		for obj in range(len(self)):
			self.pop()
			if not self.lock_signal:
				self.__screen.signal('record-changed', ('record-removed', len(self)))

	def __setitem__(self, key, value):
		super(ModelList, self).__setitem__(key, value)
		if not self.lock_signal:
			self.__screen.signal('record-changed', ('record-changed', key))

class ModelRecordGroup(signal_event.signal_event):
	def __init__(self, resource, fields, ids=[], parent=None, context={}):
		super(ModelRecordGroup, self).__init__()
		self.parent = parent
		self._context = context
		self._context.update(rpc.session.context)
		self.resource = resource
		self.rpc = RPCProxy(resource)
		self.fields = fields
		self.mfields = {}
		self.mfields_load(fields.keys(), self)

		self.models = ModelList(self)
		self.current_idx = None

		self.load(ids)
		self.model_removed = []
		self.on_write = ''

	def mfields_load(self, fkeys, models):
		for fname in fkeys:
			fvalue = models.fields[fname]
			modelfield = field.ModelField(fvalue['type'])
			fvalue['name'] = fname
			models.mfields[fname] = modelfield(models, fvalue)

	def save(self):
		for model in self.models:
			saved = model.save()
			self.writen(saved)

	def writen(self, edited_id):
		if not self.on_write:
			return
		new_ids = getattr(self.rpc, self.on_write)(edited_id, self.context)
		model_idx = self.models.index(self[edited_id])
		result = False
		for id in new_ids:
			cont = False
			for m in self.models:
				if m.id == id:
					cont = True
					m.reload()
			if cont:
				continue
			newmod = ModelRecord(self.resource, id, parent=self.parent, group=self)
			newmod.reload()
			if not result:
				result = newmod
			new_index = min(model_idx, len(self.models)-1)
			self.model_add(newmod, new_index)
		return result
	
	def pre_load(self, ids, display=True):
		if not ids:
			return True
		if len(ids)>10:
			self.models.lock_signal = True
		for id in ids:
			newmod = ModelRecord(self.resource, id, parent=self.parent, group=self)
			self.model_add(newmod)
			if display:
				self.signal('model-changed', newmod)
		if len(ids)>10:
			self.models.lock_signal = False
			self.signal('record-cleared')
		return True

	def load_for(self, values):
		if len(values)>10:
			self.models.lock_signal = True
		for value in values:
			newmod = ModelRecord(self.resource, value['id'], parent=self.parent, group=self)
			newmod.set(value)
			self.models.append(newmod)
			newmod.signal_connect(self, 'record-changed', self._record_changed)
		if len(values)>10:
			self.models.lock_signal = False
			self.signal('record-cleared')

	def load(self, ids, display=True):
		if not ids:
			return True
		if not self.fields:
			return self.pre_load(ids, display)
		c = rpc.session.context.copy()
		c.update(self.context)
		values = self.rpc.read(ids, self.fields.keys(), c)
		if not values:
			return False
		newmod = False
		self.load_for(values)
		if newmod and display:
			self.signal('model-changed', newmod)
		self.current_idx = 0
		return True
	
	def clear(self):
		self.models.clear()
		self.model_removed = []
	
	def getContext(self):
		ctx = {}
		ctx.update(self._context)
		#ctx['active_ids'] = [model.id for model in self.models if model.id]
		#if self.current_idx is not None:
		#	ctx['active_id'] = self.models[self.current_idx].id or False
		#else:
		#	ctx['active_id'] = False
		return ctx
	context = property(getContext)

	def model_add(self, model, position=-1):
		#
		# To be checked
		#
		if not model.mgroup is self:
			fields = {}
			for mf in model.mgroup.fields:
				fields[model.mgroup.fields[mf]['name']] = model.mgroup.fields[mf]
			self.add_fields(fields, self)
			self.add_fields(self.fields, model.mgroup)
			model.mgroup = self

		if position==-1:
			self.models.append(model)
		else:
			self.models.insert(position, model)
		self.current_idx = position
		model.parent = self.parent
		model.signal_connect(self, 'record-changed', self._record_changed)
		return model

	def model_new(self, default=True, domain=[], context={}):
		newmod = ModelRecord(self.resource, None, group=self, 
					   parent=self.parent, new=True)
		newmod.signal_connect(self, 'record-changed', self._record_changed)
		if default:
			ctx=context.copy()
			ctx.update(self.context)
			newmod.default_get(domain, ctx)
		self.signal('model-changed', newmod)
		return newmod
	
	def model_remove(self, model):
		idx = self.models.index(model)
		self.models.remove(model)
		if model.parent:
			model.parent.modified = True
		if self.models:
			self.current_idx = min(idx, len(self.models)-1)
		else:
			self.current_idx = None

	def _record_changed(self, model, signal_data):
		self.signal('model-changed', model)

	def prev(self):
		if self.models and self.current_idx is not None:
			self.current_idx = (self.current_idx - 1) % len(self.models)
		elif self.models:
			self.current_idx = 0
		else:
			return None
		return self.models[self.current_idx]
	
	def next(self):
		if self.models and self.current_idx is not None:
			self.current_idx = (self.current_idx + 1) % len(self.models)
		elif self.models:
			self.current_idx = 0
		else:
			return None
		return self.models[self.current_idx]

	def remove(self, model):
		try:
			idx = self.models.index(model)
			if self.models[idx].id:
				self.model_removed.append(self.models[idx].id)
			if model.parent:
				model.parent.modified = True
			self.models.remove(self.models[idx])
		except:
			pass

	def add_fields_custom(self, fields, models):
		to_add = []
		for f in fields.keys():
			if not f in models.fields:
				models.fields[f] = fields[f]
				models.fields[f]['name'] = f
				to_add.append(f)
			else:
				models.fields[f].update(fields[f])
		self.mfields_load(to_add, models)
		for fname in to_add:
			for m in models.models:
				m.value[fname] = self.mfields[fname].create(m)
		return to_add

	def add_fields(self, fields, models):
		import time
		ct = time.time()
		to_add = self.add_fields_custom(fields, models)
		models = models.models
		if not len(models):
			return True

		old = []
		new = []
		for model in models:
			if model.id:
				old.append(model.id)
			else:
				new.append(model)
		if len(old) and len(to_add):
			c = rpc.session.context.copy()
			c.update(self.context)
			values = self.rpc.read(old, to_add, c)
			if values:
				for v in values:
					id = v['id']
					if 'id' not in to_add:
						del v['id']
					self[id].set(v, signal=False)
		if len(new) and len(to_add):
			values = self.rpc.default_get(to_add, self.context)
			for t in to_add:
				if t not in values:
					values[t] = False
			for mod in new:
				mod.set_default(values)

	def __iter__(self):
		return iter(self.models)

	def get_by_id(self, id):
		for model in self.models:
			if model.id == id:
				return model

	__getitem__ = get_by_id

# vim:noexpandtab:
