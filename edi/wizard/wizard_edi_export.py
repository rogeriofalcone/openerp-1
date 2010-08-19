# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

import wizard

_export_form = '''<?xml version="1.0"?>
<form string="EDI file export">
    <label string="Not Implemented!"/>
    <separator string="Export to the following directory" colspan="4" />
    <field name="ediexportdir" colspan="4" />
</form>'''

_export_fields = {
        'ediexportdir': {
            'string' : 'EDI Import Dir',
            'type' : 'char',
            'size' : 100,
            'default' : lambda *a: '/edi/reception',
            'required' : True
        },
}

_export_done_form = '''<?xml version="1.0"?>
<form string="EDI file exported">
    <separator string="EDI file exported" colspan="4" />
</form>'''

_export_done_fields = {}

def _do_export(self, cr, uid, data, context):
    return {}

class wiz_edi_export(wizard.interface):
    states = {
        'init' : {
            'actions': [],
            'result': {
                'type': 'form',
                'arch': _export_form,
                'fields': _export_fields,
                'state': [
                    ('end', 'Cancel'),
                    ('export', 'Export Sales')
                ],
            },
        },
        'export' : {
            'actions': [_do_export],
            'result': {
                'type': 'form',
                'arch': _export_done_form,
                'fields': _export_done_fields,
                'state': [
                    ('end', 'Ok')
                ],
            },
        },
    }

wiz_edi_export('edi.export')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

