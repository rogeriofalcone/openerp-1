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
import pooler
from osv import osv
from tools.translate import _

form = '''<?xml version="1.0"?>
<form string="Verify Code">
    <field name="code" colspan="4"/>
</form>'''

fields = {
    'code': {'string': 'Verification Code','required':True,  'size': 255 , 'type': 'char', 'help': 'Enter the verification code thay you get in your verification Email'}
}

class verifycode(wizard.interface):

    def checkcode(self, cr, uid, data, context):

        state = pooler.get_pool(cr.dbname).get('email.smtpclient').browse(cr, uid, data['id'], context).state
        if state == 'confirm':
            raise osv.except_osv(_('Error'), _('Server already verified!'))

        code = pooler.get_pool(cr.dbname).get('email.smtpclient').browse(cr, uid, data['id'], context).code
        if code == data['form']['code']:
            pooler.get_pool(cr.dbname).get('email.smtpclient').write(cr, uid, [data['id']], {'state':'confirm'})
        else:
            raise osv.except_osv(_('Error'), _('Verification failed. Invalid Verification Code!'))
        return {}

    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':form, 'fields':fields, 'state':[('end','Cancel'),('check','Verify Code')]}
        },
        'check': {
            'actions': [checkcode],
            'result': {'type':'state', 'state':'end'}
        }
    }
verifycode('email.verifycode')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

