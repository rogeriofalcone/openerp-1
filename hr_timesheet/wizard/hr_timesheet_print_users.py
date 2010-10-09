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

import datetime

from osv import osv, fields

class analytical_timesheet_employees(osv.osv_memory):
    _name = 'hr.analytical.timesheet.users'
    _description = 'Print Employees Timesheet'
    _columns = {
        'month': fields.selection([(x, datetime.date(2000, x, 1).strftime('%B')) for x in range(1, 13)],
                                  'Month', required=True),
        'year': fields.integer('Year', required=True),
        'employee_ids': fields.many2many('hr.employee', 'timesheet_employee_rel', 'timesheet_id', 'employee_id', 'employees', required=True)
                }

    _defaults = {
         'month': datetime.date.today().month,
         'year': datetime.date.today().year,
             }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        datas = {
             'ids': [],
             'model': 'hr.employee',
             'form': data
                 }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'hr.analytical.timesheet_users',
            'datas': datas,
            }

analytical_timesheet_employees()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
