# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil import relativedelta
import random
import json
import urllib
import urlparse

from openerp import tools
from openerp.exceptions import Warning
from openerp.tools.safe_eval import safe_eval as eval
from openerp.tools.translate import _
from openerp.osv import osv, fields


class MassMailingCategory(osv.Model):
    """Model of categories of mass mailing, i.e. marketing, newsletter, ... """
    _name = 'mail.mass_mailing.category'
    _description = 'Mass Mailing Category'
    _order = 'name'

    _columns = {
        'name': fields.char('Name', required=True),
    }


class MassMailingContact(osv.Model):
    """Model of a contact. This model is different from the partner model
    because it holds only some basic information: name, email. The purpose is to
    be able to deal with large contact list to email without bloating the partner
    base."""
    _name = 'mail.mass_mailing.contact'
    _description = 'Mass Mailing Contact'
    _order = 'email'
    _rec_name = 'email'

    _columns = {
        'name': fields.char('Name'),
        'email': fields.char('Email', required=True),
        'create_date': fields.datetime('Create Date'),
        'list_id': fields.many2one(
            'mail.mass_mailing.list', string='Mailing List',
            ondelete='cascade', required=True,
        ),
        'opt_out': fields.boolean('Opt Out', help='The contact has chosen not to receive mails anymore from this list'),
    }

    def _get_latest_list(self, cr, uid, context={}):
        lid = self.pool.get('mail.mass_mailing.list').search(cr, uid, [], limit=1, order='id desc', context=context)
        return lid and lid[0] or False

    _defaults = {
        'list_id': _get_latest_list
    }

    def name_create(self, cr, uid, name, context=None):
        name, email = self.pool['res.partner']._parse_partner_name(name, context=context)
        if name and not email:
            email = name
        if email and not name:
            name = email
        rec_id = self.create(cr, uid, {'name': name, 'email': email}, context=context)
        return self.name_get(cr, uid, [rec_id], context)[0]


class MassMailingList(osv.Model):
    """Model of a contact list. """
    _name = 'mail.mass_mailing.list'
    _order = 'name'
    _description = 'Mailing List'

    def _get_contact_nbr(self, cr, uid, ids, name, arg, context=None):
        result = dict.fromkeys(ids, 0)
        Contacts = self.pool.get('mail.mass_mailing.contact')
        for group in Contacts.read_group(cr, uid, [('list_id', 'in', ids), ('opt_out', '!=', True)], ['list_id'], ['list_id'], context=context):
            result[group['list_id'][0]] = group['list_id_count']
        return result

    _columns = {
        'name': fields.char('Mailing List', required=True),
        'contact_nbr': fields.function(
            _get_contact_nbr, type='integer',
            string='Number of Contacts',
        ),
    }


class MassMailingStage(osv.Model):
    """Stage for mass mailing campaigns. """
    _name = 'mail.mass_mailing.stage'
    _description = 'Mass Mailing Campaign Stage'
    _order = 'sequence'

    _columns = {
        'name': fields.char('Name', required=True, translate=True),
        'sequence': fields.integer('Sequence'),
    }

    _defaults = {
        'sequence': 0,
    }


class MassMailingCampaign(osv.Model):
    """Model of mass mailing campaigns. """
    _name = "mail.mass_mailing.campaign"
    _description = 'Mass Mailing Campaign'

    def _get_statistics(self, cr, uid, ids, name, arg, context=None):
        """ Compute statistics of the mass mailing campaign """
        Statistics = self.pool['mail.mail.statistics']
        results = dict.fromkeys(ids, False)
        for cid in ids:
            stat_ids = Statistics.search(cr, uid, [('mass_mailing_campaign_id', '=', cid)], context=context)
            stats = Statistics.browse(cr, uid, stat_ids, context=context)
            results[cid] = {
                'total': len(stats),
                'failed': len([s for s in stats if not s.scheduled is False and s.sent is False and not s.exception is False]),
                'scheduled': len([s for s in stats if not s.scheduled is False and s.sent is False and s.exception is False]),
                'sent': len([s for s in stats if not s.sent is False]),
                'opened': len([s for s in stats if not s.opened is False]),
                'replied': len([s for s in stats if not s.replied is False]),
                'bounced': len([s for s in stats if not s.bounced is False]),
            }
            results[cid]['delivered'] = results[cid]['sent'] - results[cid]['bounced']
            results[cid]['received_ratio'] = 100.0 * results[cid]['delivered'] / (results[cid]['sent'] or 1)
            results[cid]['opened_ratio'] = 100.0 * results[cid]['opened'] / (results[cid]['sent'] or 1)
            results[cid]['replied_ratio'] = 100.0 * results[cid]['replied'] / (results[cid]['sent'] or 1)
        return results

    _columns = {
        'name': fields.char('Name', required=True),
        'stage_id': fields.many2one('mail.mass_mailing.stage', 'Stage', required=True),
        'user_id': fields.many2one(
            'res.users', 'Responsible',
            required=True,
        ),
        'category_ids': fields.many2many(
            'mail.mass_mailing.category', 'mail_mass_mailing_category_rel',
            'category_id', 'campaign_id', string='Categories'),
        'mass_mailing_ids': fields.one2many(
            'mail.mass_mailing', 'mass_mailing_campaign_id',
            'Mass Mailings',
        ),
        'unique_ab_testing': fields.boolean(
            'AB Testing',
            help='If checked, recipients will be mailed only once, allowing to send'
                 'various mailings in a single campaign to test the effectiveness'
                 'of the mailings.'),
        'color': fields.integer('Color Index'),
        # stat fields
        'total': fields.function(
            _get_statistics, string='Total',
            type='integer', multi='_get_statistics'
        ),
        'scheduled': fields.function(
            _get_statistics, string='Scheduled',
            type='integer', multi='_get_statistics'
        ),
        'failed': fields.function(
            _get_statistics, string='Failed',
            type='integer', multi='_get_statistics'
        ),
        'sent': fields.function(
            _get_statistics, string='Sent Emails',
            type='integer', multi='_get_statistics'
        ),
        'delivered': fields.function(
            _get_statistics, string='Delivered',
            type='integer', multi='_get_statistics',
        ),
        'opened': fields.function(
            _get_statistics, string='Opened',
            type='integer', multi='_get_statistics',
        ),
        'replied': fields.function(
            _get_statistics, string='Replied',
            type='integer', multi='_get_statistics'
        ),
        'bounced': fields.function(
            _get_statistics, string='Bounced',
            type='integer', multi='_get_statistics'
        ),
        'received_ratio': fields.function(
            _get_statistics, string='Received Ratio',
            type='integer', multi='_get_statistics',
        ),
        'opened_ratio': fields.function(
            _get_statistics, string='Opened Ratio',
            type='integer', multi='_get_statistics',
        ),
        'replied_ratio': fields.function(
            _get_statistics, string='Replied Ratio',
            type='integer', multi='_get_statistics',
        ),
    }

    def _get_default_stage_id(self, cr, uid, context=None):
        stage_ids = self.pool['mail.mass_mailing.stage'].search(cr, uid, [], limit=1, context=context)
        return stage_ids and stage_ids[0] or False

    _defaults = {
        'user_id': lambda self, cr, uid, ctx=None: uid,
        'stage_id': lambda self, *args: self._get_default_stage_id(*args),
    }

    def get_recipients(self, cr, uid, ids, model=None, context=None):
        """Return the recipients of a mailing campaign. This is based on the statistics
        build for each mailing. """
        Statistics = self.pool['mail.mail.statistics']
        res = dict.fromkeys(ids, False)
        for cid in ids:
            domain = [('mass_mailing_campaign_id', '=', cid)]
            if model:
                domain += [('model', '=', model)]
            stat_ids = Statistics.search(cr, uid, domain, context=context)
            res[cid] = set(stat.res_id for stat in Statistics.browse(cr, uid, stat_ids, context=context))
        return res


class MassMailing(osv.Model):
    """ MassMailing models a wave of emails for a mass mailign campaign.
    A mass mailing is an occurence of sending emails. """

    _name = 'mail.mass_mailing'
    _description = 'Mass Mailing'
    # number of periods for tracking mail_mail statistics
    _period_number = 6
    _order = 'date DESC'

    def __get_bar_values(self, cr, uid, id, obj, domain, read_fields, value_field, groupby_field, context=None):
        """ Generic method to generate data for bar chart values using SparklineBarWidget.
            This method performs obj.read_group(cr, uid, domain, read_fields, groupby_field).

            :param obj: the target model (i.e. crm_lead)
            :param domain: the domain applied to the read_group
            :param list read_fields: the list of fields to read in the read_group
            :param str value_field: the field used to compute the value of the bar slice
            :param str groupby_field: the fields used to group

            :return list section_result: a list of dicts: [
                                                {   'value': (int) bar_column_value,
                                                    'tootip': (str) bar_column_tooltip,
                                                }
                                            ]
        """
        date_begin = datetime.strptime(self.browse(cr, uid, id, context=context).date, tools.DEFAULT_SERVER_DATETIME_FORMAT).date()
        section_result = [{'value': 0,
                           'tooltip': (date_begin + relativedelta.relativedelta(days=i)).strftime('%d %B %Y'),
                           } for i in range(0, self._period_number)]
        group_obj = obj.read_group(cr, uid, domain, read_fields, groupby_field, context=context)
        field_col_info = obj._all_columns.get(groupby_field.split(':')[0])
        pattern = tools.DEFAULT_SERVER_DATE_FORMAT if field_col_info.column._type == 'date' else tools.DEFAULT_SERVER_DATETIME_FORMAT
        for group in group_obj:
            group_begin_date = datetime.strptime(group['__domain'][0][2], pattern).date()
            timedelta = relativedelta.relativedelta(group_begin_date, date_begin)
            section_result[timedelta.days] = {'value': group.get(value_field, 0), 'tooltip': group.get(groupby_field)}
        return section_result

    def _get_daily_statistics(self, cr, uid, ids, field_name, arg, context=None):
        """ Get the daily statistics of the mass mailing. This is done by a grouping
        on opened and replied fields. Using custom format in context, we obtain
        results for the next 6 days following the mass mailing date. """
        obj = self.pool['mail.mail.statistics']
        res = {}
        for id in ids:
            res[id] = {}
            date_begin = datetime.strptime(self.browse(cr, uid, id, context=context).date, tools.DEFAULT_SERVER_DATETIME_FORMAT)
            date_end = date_begin + relativedelta.relativedelta(days=self._period_number - 1)
            date_begin_str = date_begin.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
            date_end_str = date_end.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
            domain = [('mass_mailing_id', '=', id), ('opened', '>=', date_begin_str), ('opened', '<=', date_end_str)]
            res[id]['opened_dayly'] = json.dumps(self.__get_bar_values(cr, uid, id, obj, domain, ['opened'], 'opened_count', 'opened:day', context=context))
            domain = [('mass_mailing_id', '=', id), ('replied', '>=', date_begin_str), ('replied', '<=', date_end_str)]
            res[id]['replied_dayly'] = json.dumps(self.__get_bar_values(cr, uid, id, obj, domain, ['replied'], 'replied_count', 'replied:day', context=context))
        return res

    def _get_statistics(self, cr, uid, ids, name, arg, context=None):
        """ Compute statistics of the mass mailing campaign """
        Statistics = self.pool['mail.mail.statistics']
        results = dict.fromkeys(ids, False)
        for mid in ids:
            stat_ids = Statistics.search(cr, uid, [('mass_mailing_id', '=', mid)], context=context)
            stats = Statistics.browse(cr, uid, stat_ids, context=context)
            results[mid] = {
                'total': len(stats),
                'failed': len([s for s in stats if not s.scheduled is False and s.sent is False and not s.exception is False]),
                'scheduled': len([s for s in stats if not s.scheduled is False and s.sent is False and s.exception is False]),
                'sent': len([s for s in stats if not s.sent is False]),
                'opened': len([s for s in stats if not s.opened is False]),
                'replied': len([s for s in stats if not s.replied is False]),
                'bounced': len([s for s in stats if not s.bounced is False]),
            }
            results[mid]['delivered'] = results[mid]['sent'] - results[mid]['bounced']
            results[mid]['received_ratio'] = 100.0 * results[mid]['delivered'] / (results[mid]['sent'] or 1)
            results[mid]['opened_ratio'] = 100.0 * results[mid]['opened'] / (results[mid]['sent'] or 1)
            results[mid]['replied_ratio'] = 100.0 * results[mid]['replied'] / (results[mid]['sent'] or 1)
        return results

    def _get_private_models(self, context=None):
        return ['res.partner', 'mail.mass_mailing.contact']

    def _get_auto_reply_to_available(self, cr, uid, ids, name, arg, context=None):
        res = dict.fromkeys(ids, False)
        for mailing in self.browse(cr, uid, ids, context=context):
            res[mailing.id] = mailing.mailing_model not in self._get_private_models(context=context)
        return res

    def _get_mailing_model(self, cr, uid, context=None):
        return [
            ('res.partner', _('Customers')),
            ('mail.mass_mailing.contact', _('Mailing List'))
        ]

    # indirections for inheritance
    _mailing_model = lambda self, *args, **kwargs: self._get_mailing_model(*args, **kwargs)

    _columns = {
        'name': fields.char('Subject', required=True),
        'email_from': fields.char('From', required=True),
        'date': fields.datetime('Date'),
        'body_html': fields.html('Body'),
        'mass_mailing_campaign_id': fields.many2one(
            'mail.mass_mailing.campaign', 'Mass Mailing Campaign',
            ondelete='set null',
        ),
        'state': fields.selection(
            [('draft', 'Draft'), ('test', 'Tested'), ('done', 'Sent')],
            string='Status', required=True,
        ),
        'color': fields.related(
            'mass_mailing_campaign_id', 'color',
            type='integer', string='Color Index',
        ),
        # mailing options
        # TODO: simplify these 4 fields
        'reply_in_thread': fields.boolean('Reply in thread'),
        'reply_specified': fields.boolean('Specific Reply-To'),
        'auto_reply_to_available': fields.function(
            _get_auto_reply_to_available,
            type='boolean', string='Reply in thread available'
        ),
        'reply_to': fields.char('Reply To'),
        # Target Emails
        'mailing_model': fields.selection(_mailing_model, string='Recipients Model', required=True),
        'mailing_domain': fields.char('Domain'),
        'contact_list_ids': fields.many2many(
            'mail.mass_mailing.list', 'mail_mass_mailing_list_rel',
            string='Mailing Lists',
        ),
        'contact_ab_pc': fields.integer(
            'AB Testing percentage',
            help='Percentage of the contacts that will be mailed. Recipients will be taken randomly.'
        ),
        # statistics data
        'statistics_ids': fields.one2many(
            'mail.mail.statistics', 'mass_mailing_id',
            'Emails Statistics',
        ),
        'total': fields.function(
            _get_statistics, string='Total',
            type='integer', multi='_get_statistics',
        ),
        'scheduled': fields.function(
            _get_statistics, string='Scheduled',
            type='integer', multi='_get_statistics',
        ),
        'failed': fields.function(
            _get_statistics, string='Failed',
            type='integer', multi='_get_statistics',
        ),
        'sent': fields.function(
            _get_statistics, string='Sent',
            type='integer', multi='_get_statistics',
        ),
        'delivered': fields.function(
            _get_statistics, string='Delivered',
            type='integer', multi='_get_statistics',
        ),
        'opened': fields.function(
            _get_statistics, string='Opened',
            type='integer', multi='_get_statistics',
        ),
        'replied': fields.function(
            _get_statistics, string='Replied',
            type='integer', multi='_get_statistics',
        ),
        'bounced': fields.function(
            _get_statistics, string='Bounced',
            type='integer', multi='_get_statistics',
        ),
        'received_ratio': fields.function(
            _get_statistics, string='Received Ratio',
            type='integer', multi='_get_statistics',
        ),
        'opened_ratio': fields.function(
            _get_statistics, string='Opened Ratio',
            type='integer', multi='_get_statistics',
        ),
        'replied_ratio': fields.function(
            _get_statistics, string='Replied Ratio',
            type='integer', multi='_get_statistics',
        ),
        # dayly ratio
        'opened_dayly': fields.function(
            _get_daily_statistics, string='Opened',
            type='char', multi='_get_daily_statistics',
            oldname='opened_monthly',
        ),
        'replied_dayly': fields.function(
            _get_daily_statistics, string='Replied',
            type='char', multi='_get_daily_statistics',
            oldname='replied_monthly',
        ),
    }

    _defaults = {
        'state': 'draft',
        'date': fields.datetime.now,
        'email_from': lambda self, cr, uid, ctx=None: self.pool['mail.message']._get_default_from(cr, uid, context=ctx),
        'mailing_model': 'mail.mass_mailing.contact',
        'contact_ab_pc': 100,
    }

    #------------------------------------------------------
    # Technical stuff
    #------------------------------------------------------

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        mailing = self.browse(cr, uid, id, context=context)
        default.update({
            'state': 'draft',
            'statistics_ids': [],
            'name': _('%s (duplicate)') % mailing.name,
        })
        return super(MassMailing, self).copy_data(cr, uid, id, default, context=context)

    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
        """ Override read_group to always display all states. """
        if groupby and groupby[0] == "state":
            # Default result structure
            # states = self._get_state_list(cr, uid, context=context)
            states = [('draft', 'Draft'), ('test', 'Tested'), ('done', 'Sent')]
            read_group_all_states = [{
                '__context': {'group_by': groupby[1:]},
                '__domain': domain + [('state', '=', state_value)],
                'state': state_value,
                'state_count': 0,
            } for state_value, state_name in states]
            # Get standard results
            read_group_res = super(MassMailing, self).read_group(cr, uid, domain, fields, groupby, offset=offset, limit=limit, context=context, orderby=orderby)
            # Update standard results with default results
            result = []
            for state_value, state_name in states:
                res = filter(lambda x: x['state'] == state_value, read_group_res)
                if not res:
                    res = filter(lambda x: x['state'] == state_value, read_group_all_states)
                res[0]['state'] = [state_value, state_name]
                result.append(res[0])
            return result
        else:
            return super(MassMailing, self).read_group(cr, uid, domain, fields, groupby, offset=offset, limit=limit, context=context, orderby=orderby)

    #------------------------------------------------------
    # Views & Actions
    #------------------------------------------------------

    def on_change_model(self, cr, uid, ids, mailing_model, list_ids, context=None):
        value = {}
        if mailing_model is 'mail.mass_mailing.contact':
            if list_ids and list_ids[0][0] == 6 and list_ids[0][2]:
                value['mailing_domain'] = "[('list_id', 'in', ["+','.join(map(str, list_ids[0][2]))+"])]"
            else:
                value['mailing_domain'] = "[('list_id', '=', False)]"
        else:
            value['mailing_domain'] = False
        return {'value': value}

    def on_change_reply_specified(self, cr, uid, ids, reply_specified, reply_in_thread, context=None):
        if reply_specified == reply_in_thread:
            return {'value': {'reply_in_thread': not reply_specified}}
        return {}

    def on_change_reply_in_thread(self, cr, uid, ids, reply_specified, reply_in_thread, context=None):
        if reply_in_thread == reply_specified:
            return {'value': {'reply_specified': not reply_in_thread}}
        return {}

    def on_change_contact_list_ids(self, cr, uid, ids, mailing_model, contact_list_ids, context=None):
        values = {}
        list_ids = []
        for command in contact_list_ids:
            if command[0] == 6:
                list_ids += command[2]
        if list_ids:
            values['contact_nbr'] = self.pool[mailing_model].search(
                cr, uid, [('list_id', 'in', list_ids), ('opt_out', '!=', True)],
                count=True, context=context
            )
        else:
            values['contact_nbr'] = 0
        return {'value': values}

    def action_duplicate(self, cr, uid, ids, context=None):
        copy_id = None
        for mid in ids:
            copy_id = self.copy(cr, uid, mid, context=context)
        if copy_id:
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mail.mass_mailing',
                'res_id': copy_id,
                'context': context,
            }
        return False

    def action_test_mailing(self, cr, uid, ids, context=None):
        ctx = dict(context, default_mass_mailing_id=ids[0])
        return {
            'name': _('Test Mailing'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.mass_mailing.test',
            'target': 'new',
            'context': ctx,
        }

    def action_see_recipients(self, cr, uid, ids, context=None):
        mailing = self.browse(cr, uid, ids[0], context=context)
        domain = self.pool['mail.mass_mailing.list'].get_global_domain(cr, uid, [c.id for c in mailing.contact_list_ids], context=context)[mailing.mailing_model]
        return {
            'name': _('See Recipients'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': mailing.mailing_model,
            'target': 'new',
            'domain': domain,
            'context': context,
        }

    def action_edit_html(self, cr, uid, ids, context=None):
        # fixme: assert is not correct
        assert len(ids)==1, "One and only one ID allowed for this action"
        mail = self.browse(cr, uid, ids[0], context=context)
        url = '/website_mail/email_designer?model=mail.mass_mailing&res_id=%d&field_body=body_html&field_from=email_form&field_subject=name&template_model=%s' % (ids[0], mail.mailing_model)
        return {
            'name': _('Open with Visual Editor'),
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }

    #------------------------------------------------------
    # Email Sending
    #------------------------------------------------------

    def get_recipients_data(self, cr, uid, mailing, res_ids, context=None):
        # tde todo: notification link ?
        if mailing.mailing_model == 'mail.mass_mailing.contact':
            contacts = self.pool['mail.mass_mailing.contact'].browse(cr, uid, res_ids, context=context)
            return dict((contact.id, {'partner_id': False, 'name': contact.name, 'email': contact.email}) for contact in contacts)
        else:
            partners = self.pool['res.partner'].browse(cr, uid, res_ids, context=context)
            return dict((partner.id, {'partner_id': partner.id, 'name': partner.name, 'email': partner.email}) for partner in partners)

    def get_recipients(self, cr, uid, mailing, context=None):
        domain = eval(mailing.mailing_domain)
        # self.pool['mail.mass_mailing.list'].get_global_domain(
            # cr, uid, [l.id for l in mailing.contact_list_ids], context=context
        # )[mailing.mailing_model]
        res_ids = self.pool[mailing.mailing_model].search(cr, uid, domain, context=context)

        # randomly choose a fragment
        if mailing.contact_ab_pc < 100:
            topick = mailing.contact_ab_nbr
            if mailing.mass_mailing_campaign_id and mailing.ab_testing:
                already_mailed = self.pool['mail.mass_mailing.campaign'].get_recipients(cr, uid, [mailing.mass_mailing_campaign_id.id], context=context)[mailing.mass_mailing_campaign_id.id]
            else:
                already_mailed = set([])
            remaining = set(res_ids).difference(already_mailed)
            if topick > len(remaining):
                topick = len(remaining)
            res_ids = random.sample(remaining, topick)
        return res_ids

    def get_unsubscribe_url(self, cr, uid, mailing_id, res_id, email, msg=None, context=None):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        url = urlparse.urljoin(
            base_url, 'mail/mailing/%(mailing_id)s/unsubscribe?%(params)s' % {
                'mailing_id': mailing_id,
                'params': urllib.urlencode({'db': cr.dbname, 'res_id': res_id, 'email': email})
            }
        )
        return '<small><a href="%s">%s</a></small>' % (url, msg or 'Click to unsubscribe')

    def send_mail(self, cr, uid, ids, context=None):
        author_id = self.pool['res.users'].browse(cr, uid, uid, context=context).partner_id.id
        for mailing in self.browse(cr, uid, ids, context=context):
            if not mailing.contact_nbr:
                raise Warning('Please select recipients.')
            # instantiate an email composer + send emails
            res_ids = self.get_recipients(cr, uid, mailing, context=context)
            comp_ctx = dict(context, active_ids=res_ids)
            composer_values = {
                'author_id': author_id,
                'body': mailing.body_html,
                'subject': mailing.name,
                'model': mailing.mailing_model,
                'email_from': mailing.email_from,
                'record_name': False,
                'composition_mode': 'mass_mail',
                'mass_mailing_id': mailing.id,
                'mailing_list_ids': [(4, l.id) for l in mailing.contact_list_ids],
            }
            if mailing.reply_specified:
                composer_values['reply_to'] = mailing.reply_to
            composer_id = self.pool['mail.compose.message'].create(cr, uid, composer_values, context=comp_ctx)
            self.pool['mail.compose.message'].send_mail(cr, uid, [composer_id], context=comp_ctx)
            self.write(cr, uid, [mailing.id], {'date': fields.datetime.now(), 'state': 'done'}, context=context)
        return True
