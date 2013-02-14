# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-Today OpenERP SA (<http://www.openerp.com>)
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

import re
from openerp.osv import osv
from openerp.osv import fields
from datetime import datetime
from openerp.tools.translate import _
import uuid

class survey_mail_compose_message(osv.TransientModel):
    _name = 'survey.mail.compose.message'
    _inherit = 'mail.compose.message'
    _description = 'Email composition wizard for Survey'
    _log_access = True

    _columns = {
        'partner_ids': fields.many2many('res.partner',
            'survey_mail_compose_message_res_partner_rel',
            'wizard_id', 'partner_id', 'Additional contacts'),
        'attachment_ids': fields.many2many('ir.attachment',
            'survey_mail_compose_message_ir_attachments_rel',
            'wizard_id', 'attachment_id', 'Attachments'),
        'multi_email': fields.text(string='List of emails', help="This list of emails of recipients will not converted in partner. Emails separated by commas, semicolons or newline."),
        'date_deadline': fields.date(string="Deadline date", help=""),
    }
    #------------------------------------------------------
    # Wizard validation and send
    #------------------------------------------------------

    def send_mail(self, cr, uid, ids, context=None):
        """ Process the wizard content and proceed with sending the related
            email(s), rendering any template patterns on the fly if needed. """
        if context is None:
            context = {}

        emails_split = re.compile(r"[;,\n\r]+")
        survey_response_obj = self.pool.get('survey.response')
        partner_obj = self.pool.get('res.partner')
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)

        def send_mail_survey(wizard, token, partner_id, email):
            """ Create one mail by recipients and replace __URL__ by link with identification token
            """
            if not partner_id:
                partner_id = partner_obj.search(cr, uid, [('email', '=', email)], context=context)
                partner_id = partner_id and partner_id[0] or None

            survey_response_obj.create(cr, uid, {
                    'date_deadline': wizard.date_deadline,
                    'survey_id': wizard.res_id,
                    'date_create': datetime.now(),
                    'response_type': 'link',
                    'state': 'new',
                    'token': token,
                    'partner_id': partner_id,
                    'email': email,
                })

            post_values = {
                'subject': wizard.subject,
                'body_html': wizard.body.replace("__URL__", "#active_id=%s&params=%s" % (wizard.res_id, token)),
                'parent_id': None,
                'partner_ids': partner_id and [partner_id] or None,
                'attachments': attachments,
                'email_from': wizard.email_from or user.partner_id.email or None,
                'email_to': email,
                'notification': False,
            }
            print ""
            print post_values
            print ""


            # # post the message
            # active_model_pool.message_post(cr, uid, [res_id], type='comment', subtype='mt_comment', context=context, **post_values)


        for wizard in self.browse(cr, uid, ids, context=context):
            if wizard.model == 'survey':

                # default values, according to the wizard options
                attachments = [(attach.datas_fname or attach.name, base64.b64decode(attach.datas)) for attach in wizard.attachment_ids]

                # check if __URL__ is in the text
                if wizard.body.find("__URL__") < 0:
                    raise osv.except_osv(_('Warning!'),_("The content of the text don't contain '__URL__'. \
                        __URL__ is automaticaly converted into the special url of the survey."))

                emails = list(set(emails_split.split( wizard.multi_email or "")) - set([partner.email for partner in wizard.partner_ids]))

                # quick check of email list
                emails_checked = []
                for email in emails:
                    email = email.strip()
                    if email:
                        if not re.search(r"^[^@]+@[^@]+$", email):
                            raise osv.except_osv(_('Warning!'),_("An email address is incorrect: '%s'" % email))
                        else:
                            emails_checked.append(email)
                if not len(emails_checked) and not len(wizard.partner_ids):
                    raise osv.except_osv(_('Warning!'),_("Please enter at least one recipient."))

                for email in emails_checked:
                    send_mail_survey(wizard, uuid.uuid4(), None, email)
                for partner in wizard.partner_ids:
                    send_mail_survey(wizard, uuid.uuid4(), partner.id, partner.email)

        return None
        return {'type': 'ir.actions.act_window_close'}

