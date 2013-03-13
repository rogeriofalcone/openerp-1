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
{
    'name': 'Gamification',
    'version': '1.0',
    'author': 'OpenERP SA',
    'category': 'Human Resources',
    'depends': ['mail'],
    'description': """Gamification of goals""",

    'data': [
        'plan_view.xml',
        'badge_view.xml',
        'goal_view.xml',
        'cron.xml',
        'security/gamification_security.xml',
        'security/ir.model.access.csv',
        'goal_base_data.xml',
    ],
    'demo': [
        'badge_demo.xml',
    ],
    'installable': True,
    'application': True,
    'css': ['static/src/css/goal.css'],
}
