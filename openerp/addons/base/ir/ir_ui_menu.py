# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2011 OpenERP SA (<http://openerp.com>).
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

import base64
import re
import threading

import tools
import openerp.modules
from osv import fields, osv
from tools.translate import _

def one_in(setA, setB):
    """Check the presence of an element of setA in setB
    """
    for x in setA:
        if x in setB:
            return True
    return False

class ir_ui_menu(osv.osv):
    _name = 'ir.ui.menu'

    def __init__(self, *args, **kwargs):
        self.cache_lock = threading.RLock()
        self.clear_cache()
        r = super(ir_ui_menu, self).__init__(*args, **kwargs)
        self.pool.get('ir.model.access').register_cache_clearing_method(self._name, 'clear_cache')
        return r

    def clear_cache(self):
        with self.cache_lock:
            # radical but this doesn't frequently happen
            self._cache = {}

    def _filter_visible_menus(self, cr, uid, ids, context=None):
        """Filters the give menu ids to only keep the menu items that should be
           visible in the menu hierarchy of the current user.
           Uses a cache for speeding up the computation.
        """
        with self.cache_lock:
            modelaccess = self.pool.get('ir.model.access')
            user_groups = set(self.pool.get('res.users').read(cr, 1, uid, ['groups_id'])['groups_id'])
            result = []
            for menu in self.browse(cr, uid, ids, context=context):
                # this key works because user access rights are all based on user's groups (cfr ir_model_access.check)
                key = (cr.dbname, menu.id, tuple(user_groups))
                if key in self._cache:
                    if self._cache[key]:
                        result.append(menu.id)
                    #elif not menu.groups_id and not menu.action:
                    #    result.append(menu.id)
                    continue

                self._cache[key] = False
                if menu.groups_id:
                    restrict_to_groups = [g.id for g in menu.groups_id]
                    if not user_groups.intersection(restrict_to_groups):
                        continue
                    #result.append(menu.id)
                    #self._cache[key] = True
                    #continue

                if menu.action:
                    # we check if the user has access to the action of the menu
                    data = menu.action
                    if data:
                        model_field = { 'ir.actions.act_window':    'res_model',
                                        'ir.actions.report.xml':    'model',
                                        'ir.actions.wizard':        'model',
                                        'ir.actions.server':        'model_id',
                                      }

                        field = model_field.get(menu.action._name)
                        if field and data[field]:
                            if not modelaccess.check(cr, uid, data[field], 'read', False):
                                continue
                else:
                    # if there is no action, it's a 'folder' menu
                    if not menu.child_id:
                        # not displayed if there is no children
                        continue

                result.append(menu.id)
                self._cache[key] = True
            return result

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}

        ids = super(ir_ui_menu, self).search(cr, uid, args, offset=0,
            limit=None, order=order, context=context, count=False)

        if not ids:
            if count:
                return 0
            return []

        # menu filtering is done only on main menu tree, not other menu lists
        if context.get('ir.ui.menu.full_list'):
            result = ids
        else:
            result = self._filter_visible_menus(cr, uid, ids, context=context)

        if offset:
            result = result[long(offset):]
        if limit:
            result = result[:long(limit)]

        if count:
            return len(result)
        return result

    def _get_full_name(self, cr, uid, ids, name, args, context):
        res = {}
        for m in self.browse(cr, uid, ids, context=context):
            res[m.id] = self._get_one_full_name(m)
        return res

    def _get_one_full_name(self, menu, level=6):
        if level<=0:
            return '...'
        if menu.parent_id:
            parent_path = self._get_one_full_name(menu.parent_id, level-1) + "/"
        else:
            parent_path = ''
        return parent_path + menu.name

    def create(self, *args, **kwargs):
        self.clear_cache()
        return super(ir_ui_menu, self).create(*args, **kwargs)

    def write(self, *args, **kwargs):
        self.clear_cache()
        return super(ir_ui_menu, self).write(*args, **kwargs)

    def unlink(self, *args, **kwargs):
        self.clear_cache()
        return super(ir_ui_menu, self).unlink(*args, **kwargs)

    def copy(self, cr, uid, id, default=None, context=None):
        ir_values_obj = self.pool.get('ir.values')
        res = super(ir_ui_menu, self).copy(cr, uid, id, context=context)
        datas=self.read(cr,uid,[res],['name'])[0]
        rex=re.compile('\([0-9]+\)')
        concat=rex.findall(datas['name'])
        if concat:
            next_num=int(concat[0])+1
            datas['name']=rex.sub(('(%d)'%next_num),datas['name'])
        else:
            datas['name']=datas['name']+'(1)'
        self.write(cr,uid,[res],{'name':datas['name']})
        ids = ir_values_obj.search(cr, uid, [
            ('model', '=', 'ir.ui.menu'),
            ('res_id', '=', id),
            ])
        for iv in ir_values_obj.browse(cr, uid, ids):
            ir_values_obj.copy(cr, uid, iv.id, default={'res_id': res},
                               context=context)
        return res

    def _action(self, cursor, user, ids, name, arg, context=None):
        res = {}
        ir_values_obj = self.pool.get('ir.values')
        value_ids = ir_values_obj.search(cursor, user, [
            ('model', '=', self._name), ('key', '=', 'action'),
            ('key2', '=', 'tree_but_open'), ('res_id', 'in', ids)],
            context=context)
        values_action = {}
        for value in ir_values_obj.browse(cursor, user, value_ids, context=context):
            values_action[value.res_id] = value.value
        for menu_id in ids:
            res[menu_id] = values_action.get(menu_id, False)
        return res

    def _action_inv(self, cursor, user, menu_id, name, value, arg, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        if self.CONCURRENCY_CHECK_FIELD in ctx:
            del ctx[self.CONCURRENCY_CHECK_FIELD]
        ir_values_obj = self.pool.get('ir.values')
        values_ids = ir_values_obj.search(cursor, user, [
            ('model', '=', self._name), ('key', '=', 'action'),
            ('key2', '=', 'tree_but_open'), ('res_id', '=', menu_id)],
            context=context)
        if value and values_ids:
            ir_values_obj.write(cursor, user, values_ids, {'value': value}, context=ctx)
        elif value:
            # no values_ids, create binding
            ir_values_obj.create(cursor, user, {
                'name': 'Menuitem',
                'model': self._name,
                'value': value,
                'key': 'action',
                'key2': 'tree_but_open',
                'res_id': menu_id,
                }, context=ctx)
        elif values_ids:
            # value is False, remove existing binding
            ir_values_obj.unlink(cursor, user, values_ids, context=ctx)

    def _get_icon_pict(self, cr, uid, ids, name, args, context):
        res = {}
        for m in self.browse(cr, uid, ids, context=context):
            res[m.id] = ('stock', (m.icon,'ICON_SIZE_MENU'))
        return res

    def onchange_icon(self, cr, uid, ids, icon):
        if not icon:
            return {}
        return {'type': {'icon_pict': 'picture'}, 'value': {'icon_pict': ('stock', (icon,'ICON_SIZE_MENU'))}}

    def read_image(self, path):
        if not path:
            return False
        path_info = path.split(',')
        icon_path = openerp.modules.get_module_resource(path_info[0],path_info[1])
        icon_image = False
        if icon_path:
            try:
                icon_file = tools.file_open(icon_path,'rb')
                icon_image = base64.encodestring(icon_file.read())
            finally:
                icon_file.close()
        return icon_image

    def _get_image_icon(self, cr, uid, ids, names, args, context=None):
        res = {}
        for menu in self.browse(cr, uid, ids, context=context):
            res[menu.id] = r = {}
            for fn in names:
                fn_src = fn[:-5]    # remove _data
                r[fn] = self.read_image(menu[fn_src])

        return res

    def _get_needaction(self, cr, uid, ids, field_names, args, context=None):
        if context is None:
            context = {}
        res = dict.fromkeys(ids)
        for menu in self.browse(cr, uid, ids, context=context):
            res[menu.id] = {}
            if menu.action and menu.action.type == 'ir.actions.act_window' and menu.action.res_model:
                menu_needaction_res = self.pool.get(menu.action.res_model).get_needaction_info(cr, uid, uid, domain=menu.action.domain, context=context)
            else:
                menu_needaction_res = [False, 0, ()]
            res[menu.id]['needaction_enabled'] = menu_needaction_res[0]
            res[menu.id]['needaction_counter'] = menu_needaction_res[1]
            res[menu.id]['needaction_record_ids'] = menu_needaction_res[2]
        return res
        
    _columns = {
        'name': fields.char('Menu', size=64, required=True, translate=True),
        'sequence': fields.integer('Sequence'),
        'child_id' : fields.one2many('ir.ui.menu', 'parent_id','Child IDs'),
        'parent_id': fields.many2one('ir.ui.menu', 'Parent Menu', select=True),
        'groups_id': fields.many2many('res.groups', 'ir_ui_menu_group_rel',
            'menu_id', 'gid', 'Groups', help="If you have groups, the visibility of this menu will be based on these groups. "\
                "If this field is empty, OpenERP will compute visibility based on the related object's read access."),
        'complete_name': fields.function(_get_full_name, 
            string='Complete Name', type='char', size=128),
        'icon': fields.selection(tools.icons, 'Icon', size=64),
        'icon_pict': fields.function(_get_icon_pict, type='char', size=32),
        'web_icon': fields.char('Web Icon File', size=128),
        'web_icon_hover':fields.char('Web Icon File (hover)', size=128),
        'web_icon_data': fields.function(_get_image_icon, string='Web Icon Image', type='binary', readonly=True, store=True, multi='icon'),
        'web_icon_hover_data':fields.function(_get_image_icon, string='Web Icon Image (hover)', type='binary', readonly=True, store=True, multi='icon'),
        'needaction_enabled': fields.function(_get_needaction, string='Target model uses the need action mechanism', type='boolean', help='If the menu entry action is an act_window action, and if this action is related to a model that uses the need_action mechanism, this field is set to true. Otherwise, it is false.', multi='_get_needaction'),
        'needaction_counter': fields.function(_get_needaction, string='Number of actions the user has to perform', type='integer', help='If the target model uses the need action mechanism, this field gives the number of actions the current user has to perform.', multi='_get_needaction'),
        'needaction_record_ids': fields.function(_get_needaction, string='Ids of records requesting an action from the user', type='many2many', help='If the target model uses the need action mechanism, this field holds the ids of the record requesting the user to perform an action.', multi='_get_needaction'),
        'action': fields.function(_action, fnct_inv=_action_inv,
            type='reference', string='Action',
            selection=[
                ('ir.actions.report.xml', 'ir.actions.report.xml'),
                ('ir.actions.act_window', 'ir.actions.act_window'),
                ('ir.actions.wizard', 'ir.actions.wizard'),
                ('ir.actions.url', 'ir.actions.url'),
                ('ir.actions.server', 'ir.actions.server'),
                ('ir.actions.client', 'ir.actions.client'),
            ]),
    }

    def _rec_message(self, cr, uid, ids, context=None):
        return _('Error ! You can not create recursive Menu.')

    _constraints = [
        (osv.osv._check_recursion, _rec_message , ['parent_id'])
    ]
    _defaults = {
        'icon' : 'STOCK_OPEN',
        'icon_pict': ('stock', ('STOCK_OPEN','ICON_SIZE_MENU')),
        'sequence' : 10,
    }
    _order = "sequence,id"
ir_ui_menu()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

