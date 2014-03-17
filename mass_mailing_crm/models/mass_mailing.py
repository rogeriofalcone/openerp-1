# -*- coding: utf-8 -*-

from openerp.osv import osv


class MassMailing(osv.Model):
    """Inherit to add crm.lead objects available for mass mailing """
    _name = 'mail.mass_mailing'
    _inherit = 'mail.mass_mailing'

    def _get_mailing_model(self, cr, uid, context=None):
        res = super(MassMailing, self)._get_mailing_model(cr, uid, context=context)
        res.append(('crm.lead', 'Leads / Opportunities'))
        return res
