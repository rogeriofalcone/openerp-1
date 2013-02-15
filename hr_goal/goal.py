# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2013 Tiny SPRL (<http://openerp.com>).
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

from openerp.osv import fields, osv

from datetime import date

GAMIFICATION_GOAL_STATUS = [
    ('inprogress','In progress'),
    ('reached','Reached'),
    ('failed','Failed'),
]

GAMIFICATION_PLAN_STATUS = [
    ('draft','Draft'),
    ('inprogress','In progress'),
    ('done','Done'),
]

GAMIFICATION_PERIOD_STATUS = [
    ('once','No automatic assigment'),
    ('daily','Daily'),
    ('weekly','Weekly'),
    ('monthly','Monthly'),
    ('yearly', 'Yearly')
]

GAMIFICATION_COMPUTATION_MODE = [
    ('sum','Sum'),
    ('count','Count'),
    ('manually','Manually')
]

GAMIFICATION_VALIDATION_CONDITION = [
    ('minus','<='),
    ('plus','>=')
]


class gamification_goal_type(osv.Model):
    """Goal type definition

    A goal type defining a way to set an objective and evaluate it
    Each module wanting to be able to set goals to the users needs to create
    a new gamification_goal_type
    """
    _name = 'gamification.goal.type'
    _description = 'Gamification goal type'

    _columns = {
        'name': fields.char('Name', required=True),
        'description': fields.text('Description'),
        'computation_mode': fields.selection(GAMIFICATION_COMPUTATION_MODE,
            string="Mode of computation",
            help="""How is computed the goal value :\n
- 'Sum' for the total of the values if the 'Evaluated field'\n
- 'Count' for the number of entries\n
- 'Manually' for user defined values""",
            required=True),
        'object': fields.many2one('ir.model',
            string='Object',
            help='The object type for the field to evaluate' ),
        'field': fields.many2one('ir.model.fields',
            string='Evaluated field',
            help='The field containing the value to evaluate' ),
        'field_date': fields.many2one('ir.model.fields',
            string='Evaluated date field',
            help='The date to use for the time period evaluated'),
        'domain': fields.char("Domain"), # how to apply it ?
        'condition' : fields.selection(GAMIFICATION_VALIDATION_CONDITION,
            string='Validation condition',
            help='A goal is considered as completed when the current value is compared to the value to reach',
            required=True),
        'sequence' : fields.integer('Sequence',
            help='Sequence number for ordering',
            required=True),
    }
    
    _defaults = {
        'sequence': 0,
        'condition': 'plus',
        'computation_mode':'manually',
    }


class gamification_goal(osv.Model):
    """Goal instance for a user

    An individual goal for a user on a specified time period
    """

    _name = 'gamification.goal'
    _description = 'Gamification goal instance'
    _inherit = 'mail.thread'

    _columns = {
        'type_id' : fields.many2one('gamification.goal.type', 
            string='Goal type',
            required=True),
        'user_id' : fields.many2one('res.users', string='User', required=True),
        'plan_id' : fields.many2one('gamification.goal.plan',
            string='Goal plan'),
        'start_date' : fields.date('Start date'),
        'end_date' : fields.date('End date'), # no start and end = always active
        'target_goal' : fields.float('To reach',
            required=True,
            track_visibility = 'always'), # no goal = global index
        'current' : fields.float('Current',
            required=True,
            track_visibility = 'always'),
        'status': fields.selection(GAMIFICATION_GOAL_STATUS,
            string='Status',
            required=True,
            track_visibility = 'always'),
    }

    _defaults = {
        'current': 0,
        'status': 'inprogress',
    }


class gamification_goal_plan(osv.Model):
    """Ga;ification goal plan

    Set of predifined goals to be able to automate goal settings or
    quickly apply several goals manually to a group of users

    If 'user_ids' is defined and 'period' is different than 'one', the set will
    be assigned to the users for each period (eg: every 1st of each month if 
        'monthly' is selected)
    """

    _name = 'gamification.goal.plan'
    _description = 'Gamification goal plan'

    _columns = {
        'name' : fields.char('Plan name', required=True),
        'user_ids' : fields.many2many('res.users',
            string='Definition',
            help="list of users to which the goal will be set"),
        'group_id' : fields.many2one('res.groups', string='Group'),
        'period' : fields.selection(GAMIFICATION_PERIOD_STATUS,
            string='Period',
            help='Period of automatic goal assigment, will be done manually if none is selected',
            required=True),
        'status': fields.selection(GAMIFICATION_PLAN_STATUS,
            string='Status',
            required=True),
        }

    _defaults = {
        'period': 'once',
        'status': 'inprogress',
    }


class gamification_goal_planline(osv.Model):
    """Gamification goal planline

    Predifined goal for 'gamification_goal_plan'
    These are generic list of goals with only the target goal defined
    Should only be created for the gamification_goal_plan object
    """

    _name = 'gamification.goal.planline'
    _description = 'Gamification generic goal for plan'

    _columns = {
        'plan_id' : fields.many2one('gamification.goal.plan',
            string='Plan'),
        'type_id' : fields.many2one('gamification.goal.type',
            string='Goal type'),
        'target_goal' : fields.float('Target value to reach'),
    }
