###############################################################################
#
# Copyright (c) 2007 TinyERP Pvt Ltd. (http://tinyerp.com) All Rights Reserved.
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
###############################################################################

from turbogears import expose
from turbogears import redirect
from turbogears import controllers

from tinyerp import rpc
from tinyerp import tools
from tinyerp import common

from tinyerp.tinyres import TinyResource

class Shortcuts(controllers.Controller, TinyResource):

    def my(self):

        if not rpc.session.is_logged():
            return []

        proxy = rpc.RPCProxy('ir.ui.view_sc')
        res = proxy.search([('user_id', '=', rpc.session.uid), ('resource', '=', 'ir.ui.menu')])
        res = proxy.read(res, ['res_id', 'name'])

        return res

    @expose()
    def default(self):
        from tinyerp.modules import actions

        domain = [('user_id', '=', rpc.session.uid), ('resource', '=', 'ir.ui.menu')]
        return actions._execute_window(False, 'ir.ui.view_sc', res_id=None, domain=domain, view_type='form', mode='tree,form')

    @expose()
    def add(self, id):
        id = int(id)
        proxy = rpc.RPCProxy('ir.ui.view_sc')
        if not proxy.search([('user_id', '=', rpc.session.uid), ('resource', '=', 'ir.ui.menu'), ('res_id', '=', id)]):
            name = rpc.RPCProxy('ir.ui.menu').name_get([id], rpc.session.context)[0][1]
            proxy.create({'user_id': rpc.session.uid, 'res_id': id, 'resource': 'ir.ui.menu', 'name': name})

        raise redirect('/tree/open', id=id, model='ir.ui.menu')
