# -*- coding: utf-8 -*-

from openerp.osv import osv, fields


class MailComposeMessage(osv.TransientModel):
    """Add concept of mass mailing campaign to the mail.compose.message wizard
    """
    _inherit = 'mail.compose.message'

    _columns = {
        'mass_mailing_campaign_id': fields.many2one(
            'mail.mass_mailing.campaign', 'Mass Mailing Campaign',
        ),
        'mass_mailing_id': fields.many2one(
            'mail.mass_mailing', 'Mass Mailing'
        ),
        'mass_mailing_name': fields.char('Mass Mailing'),
        'mailing_list_ids': fields.many2many(
            'mail.mass_mailing.list', string='Mailing List'
        ),
    }

    def get_mail_values(self, cr, uid, wizard, res_ids, context=None):
        """ Override method that generated the mail content by creating the
        mail.mail.statistics values in the o2m of mail_mail, when doing pure
        email mass mailing. """
        res = super(MailComposeMessage, self).get_mail_values(cr, uid, wizard, res_ids, context=context)
        # use only for allowed models in mass mailing
        if wizard.composition_mode == 'mass_mail' and \
                (wizard.mass_mailing_name or wizard.mass_mailing_id) and \
                wizard.model in [item[0] for item in self.pool['mail.mass_mailing']._get_mailing_model(cr, uid, context=context)]:
            mass_mailing = wizard.mass_mailing_id
            if not mass_mailing:
                mass_mailing_id = self.pool['mail.mass_mailing'].create(
                    cr, uid, {
                        'mass_mailing_campaign_id': wizard.mass_mailing_campaign_id and wizard.mass_mailing_campaign_id.id or False,
                        'name': wizard.mass_mailing_name,
                        'template_id': wizard.template_id and wizard.template_id.id or False,
                        'state': 'done',
                        'mailing_type': wizard.model,
                        'mailing_domain': wizard.active_domain,
                    }, context=context)
                mass_mailing = self.pool['mail.mass_mailing'].browse(cr, uid, mass_mailing_id, context=context)
            for res_id in res_ids:
                res[res_id]['mailing_id'] = mass_mailing.id
                res[res_id]['statistics_ids'] = [(0, 0, {
                    'model': wizard.model,
                    'res_id': res_id,
                    'mass_mailing_id': mass_mailing.id,
                })]
        return res
