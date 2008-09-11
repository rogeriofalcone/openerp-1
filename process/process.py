# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005-TODAY TINY SPRL. (http://tiny.be) All Rights Reserved.
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

import netsvc
import pooler, tools

from osv import fields, osv

class process_process(osv.osv):
    _name = "process.process"
    _description = "Process"
    _columns = {
        'name': fields.char('Name', size=30,required=True),
        'active': fields.boolean('Active'),
        'note': fields.text('Notes'),
        'node_ids': fields.one2many('process.node', 'process_id', 'Nodes')
    }
    _defaults = {
        'active' : lambda *a: True,
    }

    def graph_get(self, cr, uid, id, res_model, res_id, scale, context):

        current_object = res_model
        pool = pooler.get_pool(cr.dbname)

        process = pool.get('process.process').browse(cr, uid, [id])[0]

        nodes = {}
        start = []
        transitions = {}
        for node in process.node_ids:

            data = {}

            data['name'] = node.name
            data['menu'] = node.menu_id.name
            data['model'] = node.model_id.model

            nodes[node.id] = data

            if node.flow_start:
                start.append(node.id)

            for tr in node.transition_out:
                data = {}
                
                data['name'] = tr.name
                data['source'] = tr.node_from_id.id
                data['target'] = tr.node_to_id.id

                transitions[tr.id] = data

        g = tools.graph(nodes.keys(), map(lambda x: (x['source'], x['target']), transitions.values()))
        g.process(start)
        #g.scale(100, 100, 180, 120)
        g.scale(*scale)

        graph = g.result_get()

        miny = -1

        for k,v in nodes.items():

            x = graph[k]['y']
            y = graph[k]['x']

            if miny == -1:
                miny = y

            miny = min(y, miny)

            v['x'] = x
            v['y'] = y

        for k, v in nodes.items():
            y = v['y']
            v['y'] = min(y - miny + 10, y)

        return dict(nodes=nodes, transitions=transitions)

process_process()

class process_node(osv.osv):
    _name = 'process.node'
    _description ='Process Nodes'
    _columns = {
        'name': fields.char('Name', size=30,required=True),
        'process_id': fields.many2one('process.process', 'Process', required=True),
        'kind': fields.selection([('state','State'),('router','Router'),('subflow','Subflow')],'Kind of Node', required=True),
        'menu_id': fields.many2one('ir.ui.menu', 'Related Menu'),
        'note': fields.text('Notes'),
        'model_id': fields.many2one('ir.model', 'Object', ondelete='set null'),
        'model_states': fields.char('States Expression', size=128),
        'flow_start': fields.boolean('Starting Flow'),
        'transition_in': fields.one2many('process.transition', 'node_to_id', 'Starting Transitions'),
        'transition_out': fields.one2many('process.transition', 'node_from_id', 'Ending Transitions'),
    }
    _defaults = {
        'kind': lambda *args: 'state',
        'model_states': lambda *args: False,
        'flow_start': lambda *args: False,
    }
process_node()

class process_transition(osv.osv):
    _name = 'process.transition'
    _description ='Process Transitions'
    _columns = {
        'name': fields.char('Name', size=32, required=True),
        'node_from_id': fields.many2one('process.node', 'Origin Node', required=True, ondelete='cascade'),
        'node_to_id': fields.many2one('process.node', 'Destination Node', required=True, ondelete='cascade'),
        'transition_ids': fields.many2many('workflow.transition', 'process_transition_ids', 'trans1_id', 'trans2_id', 'Workflow Transitions'),
        'note': fields.text('Description'),
        'action_ids': fields.one2many('process.transition.action', 'transition_id', 'Buttons')
    }
    _defaults = {
    }
process_transition()

class process_transition_action(osv.osv):
    _name = 'process.transition.action'
    _description ='Process Transitions Actions'
    _columns = {
        'name': fields.char('Name', size=32, required=True),
        'state': fields.selection([('dummy','Dummy'),('method','Object Method'),('workflow','Workflow Trigger'),('action','Action')], 'Type', required=True),
        'action': fields.char('Action ID', size=64, states={
            'dummy':[('readonly',1)],
            'method':[('required',1)],
            'workflow':[('required',1)],
            'action':[('required',1)],
        },),
        'transition_id': fields.many2one('process.transition', 'Transition', required=True, ondelete='cascade')
    }
    _defaults = {
        'state': lambda *args: 'dummy',
    }
process_transition_action()




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

