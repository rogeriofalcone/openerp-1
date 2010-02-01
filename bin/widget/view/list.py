# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Copyright (c) 2008-2009 B2CK, Bertrand Chenal, Cedric Krier (D&D in lists)
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

import gobject
import gtk
import tools

import rpc
from rpc import RPCProxy
import service
import locale
from interface import parser_view

class field_record(object):
    def __init__(self, name):
        self.name = name
    def get_client(self, *args):
        return self.name
    def get(self, *args):
        return self.name
    def get_state_attrs(self, *args, **argv):
        return {}
    def set_client(self,*args):
        pass
    def set(self,*args):
        pass

class group_record(object):
    def __init__(self, value={}):
        self.list_parent = None
        self._children = []
        self.value = value
        self.id = False

    def getChildren(self):
        self._children.load()
        return self._children

    def setChildren(self, c):
        self._children = c
        return c
    children = property(getChildren, setChildren)

    def expr_eval(self, *args, **argv):
        return True

    def __setitem__(self, attr, val):
        pass

    def __getitem__(self, attr):
        return field_record(self.value.get(attr, ''))

def echo(fn):
    def wrapped(self, *v, **k):
        name = fn.__name__
        res = fn(self, *v, **k)
        return res
    return wrapped


class list_record(object):
    def __init__(self, mgroup, parent=None, context=None, domain=None):
        self.mgroup = mgroup
        self.mgroup.list_parent = parent
        self.mgroup.list_group = self
        self.parent = parent
        self.context = context or {}
        self.domain = domain
        self.loaded = False
        self.lst = []
        self.load()

    def load(self):
        if self.loaded:
            return
        self.loaded = True
        gb = self.context.get('group_by', False)
        if gb:
            records = rpc.session.rpc_exec_auth('/object', 'execute', self.mgroup.resource, 'read_group',
                self.context.get('__domain', []) + (self.domain or []), self.mgroup.fields.keys(), gb, 0, False, self.context)
            for r in records:
                rec = group_record(r)
                self.add(rec)
                ctx = {'__domain': r.get('__domain', [])}
                ctx.update(r.get('__context', {}))
                l = list_record(self.mgroup, parent=rec, context=ctx, domain=self.domain)
                rec.children = l

        else:
            if self.context.get('__domain'):
                ids = rpc.session.rpc_exec_auth('/object', 'execute', self.mgroup.resource, 'search', self.context.get('__domain'))
                self.mgroup.load(ids)
                res= []
                for id in ids:
                    res.append(self.mgroup.get_by_id(id))
                self.add_list(res)
            else:
                self.lst = self.mgroup.models
                for m in self.mgroup.models:
                    m.list_group = self
                    m.list_parent = self.parent
                #self.add_list(self.mgroup.models)

    def add(self, lst):
        lst.list_parent = self.parent
        lst.list_group = self
        self.lst.append(lst)

    def add_list(self, lst):
        for l in lst:
            self.add(l)

    def __getitem__(self, i):
        self.load()
        return self.lst[i]

    def __len__(self):
        self.load()
        return len(self.lst)

class AdaptModelGroup(gtk.GenericTreeModel):
    def __init__(self, model_group, context={}, domain=[]):
        super(AdaptModelGroup, self).__init__()
        self.model_group = model_group
        self.context = context or {}
        self.domain = domain
        self.models = list_record(model_group, context=context, domain=self.domain)
        self.set_property('leak_references', False)

    def added(self, modellist, position):
        model = modellist[position]
        self.emit('row_inserted', self.on_get_path(model),
                  self.get_iter(self.on_get_path(model)))

    def cancel(self):
        pass

    def move(self, path, position):
        idx = path[0]
        self.model_group.model_move(self.models[idx], position)

    def removed(self, lst, position):
        self.emit('row_deleted', position)
        self.invalidate_iters()

    def append(self, model):
        self.model_group.model_add(model)

    def prepend(self, model):
        self.model_group.model_add(model, 0)

    def remove(self, iter):
        idx = self.get_path(iter)[0]
        self.model_group.model_remove(self.models[idx])
        self.invalidate_iters()

    def saved(self, id):
        return self.model_group.writen(id)

    def __len__(self):
        return len(self.models)

    ## Mandatory GenericTreeModel methods

    def on_get_flags(self):
        if self.context.get('group_by', False):
            return gtk.TREE_MODEL_ITERS_PERSIST
        return gtk.TREE_MODEL_LIST_ONLY

    def on_get_n_columns(self):
        return 1

    def on_get_column_type(self, index):
        return gobject.TYPE_PYOBJECT

    def on_get_path(self, iter):
        iter2 = iter
        result = []
        while iter:
            result.insert(0,iter.list_group.lst.index(iter))
            iter = iter.list_parent
        return tuple(result)

    def on_get_iter(self, path):
        if not isinstance(path,(list, tuple)):
            path = (path,)
        mods = self.models
        for p in path[:-1]:
            mods = mods[p].children
        if path[-1]<len(mods):
            return mods[path[-1]]
        return None

    def on_get_value(self, node, column):
        assert column == 0
        return node

    def on_iter_next(self, node):
        try:
            i = node.list_group.lst.index(node) + 1
            return node.list_group[i]
        except IndexError:
            return None

    def on_iter_has_child(self, node):
        return bool(getattr(node,'children',None))

    def on_iter_children(self, node):
        return getattr(node,'children',[])[0]

    def on_iter_n_children(self, node):
        return len(getattr(node,'children',[]))

    def on_iter_nth_child(self, node, n):
        if node is None:
            return self.on_get_iter([n])
        if n<len(getattr(node,'children',[])):
            return getattr(node,'children',[])[n]
        return None

    def on_iter_parent(self, node):
        return node.list_parent

class ViewList(parser_view):
    def __init__(self, window, screen, widget, children=None, buttons=None,
            toolbar=None, submenu=None):
        super(ViewList, self).__init__(window, screen, widget, children,
                buttons, toolbar, submenu=submenu)
        self.store = None
        self.view_type = 'tree'
        self.model_add_new = True
        self.widget = gtk.VBox()
        self.widget_tree = widget
        scroll = gtk.ScrolledWindow()
        scroll.add(self.widget_tree)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.widget.pack_start(scroll, expand=True, fill=True)
        self.widget_tree.screen = screen
        self.reload = False
        self.children = children
        self.last_col = None
        self.tree_editable = False
        if children:
            hbox = gtk.HBox()
            self.widget.pack_start(hbox, expand=False, fill=False, padding=2)
            for c in children:
                hbox2 = gtk.HBox()
                hbox2.pack_start(children[c][1], expand=True, fill=False)
                hbox2.pack_start(children[c][2], expand=True, fill=False)
                hbox.pack_start(hbox2, expand=False, fill=False, padding=12)
            hbox.show_all()

        self.display()

        self.widget_tree.connect('button-press-event', self.__contextual_menu)
        self.widget_tree.connect_after('row-activated', self.__sig_switch)
        selection = self.widget_tree.get_selection()
        selection.set_mode(gtk.SELECTION_MULTIPLE)
        selection.connect('changed', self.__select_changed)

        if self.widget_tree.sequence:
            self.widget_tree.enable_model_drag_source(gtk.gdk.BUTTON1_MASK,
                    [('MY_TREE_MODEL_ROW', gtk.TARGET_SAME_WIDGET, 0),],
                    gtk.gdk.ACTION_MOVE)
            self.widget_tree.drag_source_set(gtk.gdk.BUTTON1_MASK | gtk.gdk.BUTTON3_MASK,
                    [('MY_TREE_MODEL_ROW', gtk.TARGET_SAME_WIDGET, 0),],
                    gtk.gdk.ACTION_MOVE)
            self.widget_tree.enable_model_drag_dest(
                    [('MY_TREE_MODEL_ROW', gtk.TARGET_SAME_WIDGET, 0),],
                    gtk.gdk.ACTION_MOVE)

            self.widget_tree.connect('drag-drop', self.drag_drop)
            self.widget_tree.connect("drag-data-get", self.drag_data_get)
            self.widget_tree.connect('drag-data-received', self.drag_data_received)
            self.widget_tree.connect('drag-data-delete', self.drag_data_delete)

    def drag_drop(self, treeview, context, x, y, time):
        treeview.emit_stop_by_name('drag-drop')
        treeview.drag_get_data(context, context.targets[-1], time)
        return True

    def drag_data_get(self, treeview, context, selection, target_id,
            etime):
        treeview.emit_stop_by_name('drag-data-get')
        def _func_sel_get(store, path, iter, data):
            data.append(path)
        data = []
        treeselection = treeview.get_selection()
        treeselection.selected_foreach(_func_sel_get, data)
        data = str(data[0])
        selection.set(selection.target, 8, data)

    def drag_data_received(self, treeview, context, x, y, selection,
            info, etime):
        treeview.emit_stop_by_name('drag-data-received')
        if treeview.sequence:
            for model in self.screen.models.models:
                if model['sequence'].get_state_attrs(
                        model).get('readonly', False):
                    return
        model = treeview.get_model()
        data = eval(selection.data)
        drop_info = treeview.get_dest_row_at_pos(x, y)
        group_by = self.screen.context.get('group_by',False)
        if drop_info:
            path, position = drop_info
            if group_by:
                target_group = model.models[path[0]]
                target_domain = filter(lambda x: x[0] == group_by, target_group.children.context.get('__domain',[]))[0]
                source_group = model.models[data[0]]
                source_group_child = source_group.children.lst[data[1]]
                rpc = RPCProxy(source_group_child.resource)
                rpc.write([source_group_child.id], {target_domain[0]:target_domain[2]})
                self.reload = True
                self.screen.reload()
                self.expand_row((data[0],))
                self.expand_row((path[0],))
            else:
                idx = path[0]
                if position in (gtk.TREE_VIEW_DROP_BEFORE,
                        gtk.TREE_VIEW_DROP_INTO_OR_BEFORE):
                    model.move(data, idx)
                else:
                    model.move(data, idx + 1)
        context.drop_finish(False, etime)
        if treeview.sequence:
            self.screen.models.set_sequence(field='sequence')

    def drag_data_delete(self, treeview, context):
        treeview.emit_stop_by_name('drag-data-delete')

    def attrs_set(self, model,path):
        if path.attrs.get('attrs',False):
            attrs_changes = eval(path.attrs.get('attrs',"{}"),{'uid':rpc.session.uid})
            for k,v in attrs_changes.items():
                result = True
                for condition in v:
                    result = tools.calc_condition(self,model,condition)
                if result:
                    if k=='invisible':
                        return False
                    elif k=='readonly':
                        return False
        return True

    def __contextual_menu(self, treeview, event, *args):
        if event.button in [1,3]:
            path = treeview.get_path_at_pos(int(event.x),int(event.y))
            selection = treeview.get_selection()
            if selection.get_mode() == gtk.SELECTION_SINGLE:
                model, iter = selection.get_selected()
            elif selection.get_mode() == gtk.SELECTION_MULTIPLE:
                model, paths = selection.get_selected_rows()
            if (not path) or not path[0]:
                return False
            m = model.models[path[0][0]]
            if self.screen.context.get('group_by',False):
                if not len(path[0])> 1: return False
                m = m.children[path[0][-1]]
            # TODO: add menu cache
            if event.button == 1:
                # first click on button
                if path[1]._type == 'Button':
                    cell_button = path[1].get_cells()[0]
                    # Calling actions
                    attrs_check = self.attrs_set(m,path[1])
                    if attrs_check and m['state'].get(m) in path[1].attrs['states'].split(','):
                        m.get_button_action(self.screen,m.id,path[1].attrs)
                        self.screen.current_model = m
                        self.screen.reload()
                        treeview.screen.reload()

            else:
                # Here it goes for right click
                if path[1]._type=='many2one':
                    value = m[path[1].name].get(m)
                    resrelate = rpc.session.rpc_exec_auth('/object', 'execute', 'ir.values', 'get', 'action', 'client_action_relate', [(self.screen.fields[path[1].name]['relation'], False)], False, rpc.session.context)
                    resrelate = map(lambda x:x[2], resrelate)
                    menu = gtk.Menu()
                    for x in resrelate:
                        x['string'] = x['name']
                        item = gtk.ImageMenuItem('... '+x['name'])
                        f = lambda action, value, model: lambda x: self._click_and_relate(action, value, model)
                        item.connect('activate', f(x, value, self.screen.fields[path[1].name]['relation']))
                        item.set_sensitive(bool(value))
                        item.show()
                        menu.append(item)
                    menu.popup(None,None,None,event.button,event.time)

    def _click_and_relate(self, action, value, model):
        data={}
        context={}
        act=action.copy()
        if not(value):
            common.message(_('You must select a record to use the relation !'))
            return False
        from widget.screen import Screen
        screen = Screen(model)
        screen.load([value])
        act['domain'] = screen.current_model.expr_eval(act['domain'], check_load=False)
        act['context'] = str(screen.current_model.expr_eval(act['context'], check_load=False))
        obj = service.LocalService('action.main')
        value = obj._exec_action(act, data, context)
        return value

    def signal_record_changed(self, signal, *args):
        if not self.store:
            return
        if signal=='record-added':
            self.store.added(*args)
        elif signal=='record-removed':
            self.store.removed(*args)
        else:
            pass
        self.update_children()

    def cancel(self):
        pass

    def __str__(self):
        return 'ViewList (%s)' % self.screen.resource

    def __getitem__(self, name):
        return None

    def destroy(self):
        self.widget_tree.destroy()
        del self.screen
        del self.widget_tree
        del self.widget

    def __sig_switch(self, treeview, *args):
        if not isinstance(self.screen.current_model, group_record):
            self.screen.row_activate(self.screen)

    def __select_changed(self, tree_sel):
        if tree_sel.get_mode() == gtk.SELECTION_SINGLE:
            model, iter = tree_sel.get_selected()
            if iter:
                path = model.get_path(iter)[0]
                self.screen.current_model = model.on_get_iter(path)
        elif tree_sel.get_mode() == gtk.SELECTION_MULTIPLE:
            model, paths = tree_sel.get_selected_rows()
            if paths:
                iter = model.on_get_iter(paths[0])
                self.screen.current_model = iter
        self.update_children()

    def set_value(self):
        if self.widget_tree.editable:
            self.widget_tree.set_value()

    def reset(self):
        pass
    #
    # self.widget.set_model(self.store) could be removed if the store
    # has not changed -> better ergonomy. To test
    #
    def display(self):
        if self.reload or (not self.widget_tree.get_model()) or self.screen.models<>self.widget_tree.get_model().model_group:
            if self.screen.context.get('group_by',False):
                if self.screen.models.parent and self.screen.context.get('o2m',False):
                    parent_value = self.screen.models.parent.value or {}
                    mgroup = parent_value.get(self.screen.context.get('o2m',False),False)
                    if mgroup:
                        self.screen.domain = [('id','in',map(lambda x:x.id,mgroup.models))]
                self.screen.models.models.clear()
                if self.last_col:
                    self.widget_tree.move_column_after(self.widget_tree.get_column(0),self.last_col)
                    self.last_col = None
                for col in self.widget_tree.get_columns():
                    if col.name == self.screen.context.get('group_by',False):
                        pos = self.widget_tree.get_columns().index(col) - 1
                        if not pos == -1:
                            self.last_col = self.widget_tree.get_column(pos)
                        self.widget_tree.move_column_after(col,None)
                if self.widget_tree.editable:
                    self.unset_editable()
                    self.tree_editable = True
            else:
                if self.last_col:
                    self.widget_tree.move_column_after(self.widget_tree.get_column(0),self.last_col)
                    self.last_col = None
                if self.tree_editable:
                    self.set_editable()
                    self.tree_editable = False
            self.set_invisible_attr()
            self.store = AdaptModelGroup(self.screen.models, self.screen.context, self.screen.domain)
            if self.store:
                self.widget_tree.set_model(self.store)
        else:
            self.store.invalidate_iters()
        self.reload = False
        if not self.screen.current_model:
            #
            # Should find a simpler solution to do something like
            #self.widget.set_cursor(None,None,False)
            #
            if self.store:
                self.widget_tree.set_model(self.store)
        self.update_children()

    def update_children(self):
        ids = self.sel_ids_get()
        for c in self.children:
            value = 0.0
            for model in self.screen.models.models:
                if model.id in ids or not ids:
                    value += model.fields_get()[self.children[c][0]].get(model, check_load=False)
            label_str = tools.locale_format('%.' + str(self.children[c][3]) + 'f', value)
            if self.children[c][4]:
                self.children[c][2].set_markup('<b>%s</b>' % label_str)
            else:
                self.children[c][2].set_markup(label_str)

    def set_cursor(self, new=False):
        if self.screen.current_model:
            path = self.store.on_get_path(self.screen.current_model)
            columns = self.widget_tree.get_columns(include_non_visible=False, include_non_editable=False)
            focus_column = len(columns) and columns[0] or None
            self.widget_tree.set_cursor(path, focus_column, new)

    def sel_ids_get(self):
        def _func_sel_get(store, path, iter, ids):
            model = store.on_get_iter(path)
            if model.id:
                ids.append(model.id)
        ids = []
        sel = self.widget_tree.get_selection()
        if sel:
            sel.selected_foreach(_func_sel_get, ids)
        return ids

    def sel_models_get(self):
        def _func_sel_get(store, path, iter, models):
            models.append(store.on_get_iter(path))
        models = []
        sel = self.widget_tree.get_selection()
        sel.selected_foreach(_func_sel_get, models)
        return models

    def on_change(self, callback):
        self.set_value()
        self.screen.on_change(callback)

    def unset_editable(self):
        self.set_editable(False)

    def expand_row(self, path, open_all = False):
        self.widget_tree.expand_row(path, open_all)

    def collapse_row(self, path):
        self.widget_tree.collapse_row(path)

    def set_editable(self, value=True):
        self.widget_tree.editable = value
        for col in self.widget_tree.get_columns():
            for renderer in col.get_cell_renderers():
                if isinstance(renderer, gtk.CellRendererToggle):
                    renderer.set_property('activatable', value)
                elif not isinstance(renderer, gtk.CellRendererProgress) and not isinstance(renderer, gtk.CellRendererPixbuf):
                    renderer.set_property('editable', value)

    def set_invisible_attr(self):
        for col in self.widget_tree.get_columns():
            value = eval(str(self.widget_tree.cells[col.name].attrs.get('invisible', 'False')),\
                           {'context':self.screen.context})
            col.set_visible(not value)
