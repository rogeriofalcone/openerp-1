# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

from osv import osv
from osv import fields
import os
import tools
import openerp
from openerp import SUPERUSER_ID
from tools.translate import _
from tools.safe_eval import safe_eval as eval

class multi_company_default(osv.osv):
    """
    Manage multi company default value
    """
    _name = 'multi_company.default'
    _description = 'Default multi company'
    _order = 'company_id,sequence,id'

    _columns = {
        'sequence': fields.integer('Sequence'),
        'name': fields.char('Name', size=256, required=True, help='Name it to easily find a record'),
        'company_id': fields.many2one('res.company', 'Main Company', required=True,
            help='Company where the user is connected'),
        'company_dest_id': fields.many2one('res.company', 'Default Company', required=True,
            help='Company to store the current record'),
        'object_id': fields.many2one('ir.model', 'Object', required=True,
            help='Object affected by this rule'),
        'expression': fields.char('Expression', size=256, required=True,
            help='Expression, must be True to match\nuse context.get or user (browse)'),
        'field_id': fields.many2one('ir.model.fields', 'Field', help='Select field property'),
    }

    _defaults = {
        'expression': lambda *a: 'True',
        'sequence': lambda *a: 100,
    }

    def copy(self, cr, uid, id, default=None, context=None):
        """
        Add (copy) in the name when duplicate record
        """
        if not context:
            context = {}
        if not default:
            default = {}
        company = self.browse(cr, uid, id, context=context)
        default = default.copy()
        default['name'] = company.name + _(' (copy)')
        return super(multi_company_default, self).copy(cr, uid, id, default, context=context)

multi_company_default()

class res_company(osv.osv):
    _name = "res.company"
    _description = 'Companies'
    _order = 'name'

    def _get_address_data(self, cr, uid, ids, field_names, arg, context=None):
        """ Read the 'address' functional fields. """
        result = {}
        part_obj = self.pool.get('res.partner')
        for company in self.browse(cr, uid, ids, context=context):
            result[company.id] = {}.fromkeys(field_names, False)
            if company.partner_id:
                address_data = part_obj.address_get(cr, openerp.SUPERUSER_ID, [company.partner_id.id], adr_pref=['default'])
                if address_data['default']:
                    address = part_obj.read(cr, openerp.SUPERUSER_ID, address_data['default'], field_names, context=context)
                    for field in field_names:
                        result[company.id][field] = address[field] or False
        return result

    def _set_address_data(self, cr, uid, company_id, name, value, arg, context=None):
        """ Write the 'address' functional fields. """
        company = self.browse(cr, uid, company_id, context=context)
        if company.partner_id:
            part_obj = self.pool.get('res.partner')
            address_data = part_obj.address_get(cr, uid, [company.partner_id.id], adr_pref=['default'])
            address = address_data['default']
            if address:
                part_obj.write(cr, uid, [address], {name: value or False})
            else:
                part_obj.create(cr, uid, {name: value or False, 'parent_id': company.partner_id.id}, context=context)
        return True

    def _format_company_footer(self, cr, uid, company, context=None):
        """
        Format the company's RML footer the right way

        @param company: compny's browse record OR dict with the required data

        @return: string containing the formated footer
        """

        # list of values required to compose the footer
        val = []

        if company['phone']: val.append(_('Phone: ')+company['phone'])
        if company['fax']: val.append(_('Fax: ')+company['fax'])
        if company['email']: val.append(_('Email: ')+company['email'])
        if company['website']: val.append(_('Website: ')+company['website'])
        if company['vat']: val.append(_('TIN: ')+company['vat'])
        if company['company_registry']: val.append(_('Reg: ')+company['company_registry'])

        # fetch the company's bank accounts
        # todo #TODO: make it work with the onchange
        bank_accounts = self.browse(cr, uid, company['id'], context=context).bank_ids
        bank_accounts_names = [bank_account.name_get()[0][1] for bank_account in bank_accounts if bank_account.footer]

        res = ' | '.join(val)
        # append the account(s) in the footer and manage plural form of "account" if necessary
        if len(bank_accounts_names) == 1:
            res += _('\nBank Account: ') + ', '.join(bank_accounts_names)
        elif len(bank_accounts_names) > 1:
            res += _('\nBank Accounts: ') + ', '.join(bank_accounts_names)

        return res

    def _get_rml_footer(self, cr, uid, ids, field_names, arg, context=None):
        result = {}
        for company in self.browse(cr, uid, ids, context=context):
            if company.customize_footer:
                result[company.id] = company.rml_footer
            else:
                result[company.id] = self._format_company_footer(cr, uid, company, context)

        return result

    def _set_rml_footer(self, cr, uid, company_id, name, value, arg, context=None):
        company = self.browse(cr, uid, [company_id], context=context)[0]

        if company.customize_footer:
            rml_footer = value
        else:
            rml_footer = self._format_company_footer(cr, uid, company, context)

        return cr.execute('UPDATE res_company SET rml_footer = %s WHERE id = %s', (rml_footer, company_id))

    def _get_rml_footer_by_line(self, cr, uid, ids, rml_footer, line=0, context=None):
        rml_split = rml_footer.split('\n')
        if len(rml_split) < line + 1:
            return False
        return rml_split[line]

    _columns = {
        'name': fields.related('partner_id', 'name', string='Company Name', size=128, required=True, store=True, type='char'),
        'customize_footer': fields.boolean('Customize Footer', help="If it is true then general information footer will not update automatically."),
        'parent_id': fields.many2one('res.company', 'Parent Company', select=True),
        'child_ids': fields.one2many('res.company', 'parent_id', 'Child Companies'),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'rml_footer': fields.function(_get_rml_footer, fnct_inv=_set_rml_footer, type='text', string='General Information Footer', store=True),
        'rml_header': fields.text('RML Header and Footer', required=True),
        'rml_header1': fields.char('Company Slogan', size=200, help="Appears by default on the top right corner of your printed documents (report header)."),
        'rml_header2': fields.text('RML Internal Header', required=True),
        'rml_header3': fields.text('RML Internal Header for Landscape Reports', required=True),
        'logo': fields.related('partner_id', 'image', string="Logo", type="binary"),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True),
        'currency_ids': fields.one2many('res.currency', 'company_id', 'Currency'),
        'user_ids': fields.many2many('res.users', 'res_company_users_rel', 'cid', 'user_id', 'Accepted Users'),
        'account_no':fields.char('Account No.', size=64),
        'street': fields.function(_get_address_data, fnct_inv=_set_address_data, size=128, type='char', string="Street", multi='address'),
        'street2': fields.function(_get_address_data, fnct_inv=_set_address_data, size=128, type='char', string="Street2", multi='address'),
        'zip': fields.function(_get_address_data, fnct_inv=_set_address_data, size=24, type='char', string="Zip", multi='address'),
        'city': fields.function(_get_address_data, fnct_inv=_set_address_data, size=24, type='char', string="City", multi='address'),
        'state_id': fields.function(_get_address_data, fnct_inv=_set_address_data, type='many2one', domain="[('country_id', '=', country_id)]", relation='res.country.state', string="Fed. State", multi='address'),
        'bank_ids': fields.one2many('res.partner.bank','company_id', 'Bank Accounts', help='Bank accounts related to this company'),
        'country_id': fields.function(_get_address_data, fnct_inv=_set_address_data, type='many2one', relation='res.country', string="Country", multi='address'),
        'email': fields.function(_get_address_data, fnct_inv=_set_address_data, size=64, type='char', string="Email", multi='address'),
        'phone': fields.function(_get_address_data, fnct_inv=_set_address_data, size=64, type='char', string="Phone", multi='address'),
        'fax': fields.function(_get_address_data, fnct_inv=_set_address_data, size=64, type='char', string="Fax", multi='address'),
        'website': fields.related('partner_id', 'website', string="Website", type="char", size=64),
        'vat': fields.related('partner_id', 'vat', string="Tax ID", type="char", size=32),
        'company_registry': fields.char('Company Registry', size=64),
        'paper_format': fields.selection([('a4', 'A4'), ('us_letter', 'US Letter')], "Paper Format", required=True),
    }
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The company name must be unique !')
    ]

    def on_change_footer(self, cr, uid, ids, customize_footer=None, phone=None, email=None, fax=None, website=None, vat=None, company_registry=None, bank_ids=None, context=None):
        if not customize_footer:
            company_values = {
                'id': ids[0],
                'customize_footer': customize_footer,
                'phone': phone,
                'email': email,
                'fax': fax,
                'website': website,
                'vat': vat,
                'company_registry': company_registry,
                'bank_ids': bank_ids,
            }
            return {'value': {'rml_footer': self._format_company_footer(cr, uid, company_values, context)}}

    def _search(self, cr, uid, args, offset=0, limit=None, order=None,
            context=None, count=False, access_rights_uid=None):
        if context is None:
            context = {}
        if context.get('user_preference'):
            # We browse as superuser. Otherwise, the user would be able to
            # select only the currently visible companies (according to rules,
            # which are probably to allow to see the child companies) even if
            # she belongs to some other companies.
            user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context)
            cmp_ids = list(set([user.company_id.id] + [cmp.id for cmp in user.company_ids]))
            return cmp_ids
        return super(res_company, self)._search(cr, uid, args, offset=offset, limit=limit, order=order,
            context=context, count=count, access_rights_uid=access_rights_uid)

    def _company_default_get(self, cr, uid, object=False, field=False, context=None):
        """
        Check if the object for this company have a default value
        """
        if not context:
            context = {}
        proxy = self.pool.get('multi_company.default')
        args = [
            ('object_id.model', '=', object),
            ('field_id', '=', field),
        ]

        ids = proxy.search(cr, uid, args, context=context)
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        for rule in proxy.browse(cr, uid, ids, context):
            if eval(rule.expression, {'context': context, 'user': user}):
                return rule.company_dest_id.id
        return user.company_id.id

    @tools.ormcache()
    def _get_company_children(self, cr, uid=None, company=None):
        if not company:
            return []
        ids =  self.search(cr, uid, [('parent_id','child_of',[company])])
        return ids

    def _get_partner_hierarchy(self, cr, uid, company_id, context=None):
        if company_id:
            parent_id = self.browse(cr, uid, company_id)['parent_id']
            if parent_id:
                return self._get_partner_hierarchy(cr, uid, parent_id.id, context)
            else:
                return self._get_partner_descendance(cr, uid, company_id, [], context)
        return []

    def _get_partner_descendance(self, cr, uid, company_id, descendance, context=None):
        descendance.append(self.browse(cr, uid, company_id).partner_id.id)
        for child_id in self._get_company_children(cr, uid, company_id):
            if child_id != company_id:
                descendance = self._get_partner_descendance(cr, uid, child_id, descendance)
        return descendance

    #
    # This function restart the cache on the _get_company_children method
    #
    def cache_restart(self, cr):
        self._get_company_children.clear_cache(self)

    def create(self, cr, uid, vals, context=None):
        if not vals.get('name', False) or vals.get('partner_id', False):
            self.cache_restart(cr)
            return super(res_company, self).create(cr, uid, vals, context=context)
        obj_partner = self.pool.get('res.partner')
        partner_id = obj_partner.create(cr, uid, {'name': vals['name'], 'is_company':True}, context=context)
        vals.update({'partner_id': partner_id})
        self.cache_restart(cr)
        company_id = super(res_company, self).create(cr, uid, vals, context=context)
        obj_partner.write(cr, uid, partner_id, {'company_id': company_id}, context=context)
        return company_id

    def write(self, cr, *args, **argv):
        self.cache_restart(cr)
        return super(res_company, self).write(cr, *args, **argv)

    def _get_euro(self, cr, uid, context=None):
        try:
            return self.pool.get('res.currency').search(cr, uid, [])[0]
        except:
            return False

    def _get_logo(self, cr, uid, ids):
        return open(os.path.join( tools.config['root_path'], 'addons', 'base', 'res', 'res_company_logo.png'), 'rb') .read().encode('base64')

    _header = """
<header>
<pageTemplate>
    <frame id="first" x1="28.0" y1="28.0" width="%s" height="%s"/>
    <pageGraphics>
        <fill color="black"/>
        <stroke color="black"/>
        <setFont name="DejaVu Sans" size="8"/>
        <drawString x="%s" y="%s"> [[ formatLang(time.strftime("%%Y-%%m-%%d"), date=True) ]]  [[ time.strftime("%%H:%%M") ]]</drawString>
        <setFont name="DejaVu Sans Bold" size="10"/>
        <drawCentredString x="%s" y="%s">[[ company.partner_id.name ]]</drawCentredString>
        <stroke color="#000000"/>
        <lines>%s</lines>
    </pageGraphics>
</pageTemplate>
</header>"""

    _header2 = _header % (539, 772, "1.0cm", "28.3cm", "11.1cm", "28.3cm", "1.0cm 28.1cm 20.1cm 28.1cm")

    _header3 = _header % (786, 525, 25, 555, 440, 555, "25 550 818 550")

    def _get_header(self,cr,uid,ids):
        try :
            header_file = tools.file_open(os.path.join('base', 'report', 'corporate_rml_header.rml'))
            try:
                return header_file.read()
            finally:
                header_file.close()
        except:
            return self._header_a4

    _header_main = """
<header>
<pageTemplate>
    <frame id="first" x1="1.3cm" y1="3.0cm" height="%s" width="19.0cm"/>
    <pageGraphics>
        <!-- You Logo - Change X,Y,Width and Height -->
        <image x="1.3cm" y="%s" height="40.0" >[[ company.logo or removeParentNode('image') ]]</image>
        <setFont name="DejaVu Sans" size="8"/>
        <fill color="black"/>
        <stroke color="black"/>
        <lines>1.3cm %s 20cm %s</lines>

        <drawRightString x="20cm" y="%s">[[ company.rml_header1 ]]</drawRightString>


        <drawString x="1.3cm" y="%s">[[ company.partner_id.name ]]</drawString>
        <drawString x="1.3cm" y="%s">[[ company.partner_id.street or  '' ]]</drawString>
        <drawString x="1.3cm" y="%s">[[ company.partner_id.city or '' ]] - [[ company.partner_id.country_id and company.partner_id.country_id.name  or '']]</drawString>
        <drawString x="1.3cm" y="%s">Phone:</drawString>
        <drawRightString x="7cm" y="%s">[[ company.partner_id.phone or '' ]]</drawRightString>
        <drawString x="1.3cm" y="%s">Mail:</drawString>
        <drawRightString x="7cm" y="%s">[[ company.partner_id.email or '' ]]</drawRightString>
        <lines>1.3cm %s 7cm %s</lines>

        <!--page bottom-->

        <lines>1.2cm 2.65cm 19.9cm 2.65cm</lines>
        <drawCentredString x="10.5cm" y="2.3cm">[[ company._get_rml_footer_by_line(company.rml_footer,line=0) ]]</drawCentredString>
        <drawCentredString x="10.5cm" y="1.8cm">[[ company._get_rml_footer_by_line(company.rml_footer,line=1) ]]</drawCentredString>
        <drawCentredString x="10.5cm" y="1.3cm">[[ company._get_rml_footer_by_line(company.rml_footer,line=2) ]]
        <drawCentredString x="10.5cm" y="0.8cm">Contact : [[ user.name ]] - Page: <pageNumber/></drawCentredString>
    </pageGraphics>
</pageTemplate>
</header>"""

    _header_a4 = _header_main % ('23.0cm', '27.6cm', '27.7cm', '27.7cm', '27.8cm', '27.2cm', '26.8cm', '26.4cm', '26.0cm', '26.0cm', '25.6cm', '25.6cm', '25.5cm', '25.5cm')
    _header_letter = _header_main % ('21.3cm', '25.9cm', '26.0cm', '26.0cm', '26.1cm', '25.5cm', '25.1cm', '24.7cm', '24.3cm', '24.3cm', '23.9cm', '23.9cm', '23.8cm', '23.8cm')

    def onchange_paper_format(self, cr, uid, ids, paper_format, context=None):
        if paper_format == 'us_letter':
            return {'value': {'rml_header': self._header_letter}}
        return {'value': {'rml_header': self._header_a4}}

    _defaults = {
        'currency_id': _get_euro,
        'paper_format': 'a4',
        'rml_header':_get_header,
        'rml_header2': _header2,
        'rml_header3': _header3,
        'logo':_get_logo
    }

    _constraints = [
        (osv.osv._check_recursion, 'Error! You can not create recursive companies.', ['parent_id'])
    ]


res_company()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

