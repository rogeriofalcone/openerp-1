# -*- coding: utf-'8' "-*-"

from openerp.osv import osv, fields

import logging

_logger = logging.getLogger(__name__)


def _partner_format_address(address1=False, address2=False):
    return ' '.join((address1 or '', address2 or ''))


def _partner_split_name(partner_name):
    return [' '.join(partner_name.split()[-1:]), ' '.join(partner_name.split()[:-1])]


class ValidationError(ValueError):
    """ Used for value error when validating transaction data coming from acquirers. """
    pass


class PaymentAcquirer(osv.Model):
    """ Acquirer Model. Each specific acquirer can extend the model by adding
    its own fields. Using the required_if_provider='<name>' attribute on fields
    it is possible to have required fields that depend on a specific acquirer.

    Each acquirer has a link to an ir.ui.view record that is a template of
    a button used to display the payment form. See examples in ``payment_acquirer_ogone``
    and ``payment_acquirer_paypal`` modules.

    Methods that should be added in an acquirer-specific implementation:

     - ``<name>_form_generate_values(self, cr, uid, id, reference, amount, currency,
       partner_id=False, partner_values=None, tx_custom_values=None, context=None)``:
       method that generates the values used to render the form button template.
     - ``<name>_get_form_action_url(self, cr, uid, id, context=None):``: method
       that returns the url of the button form. It is used for example in
       ecommerce application, if you want to repost some data to the acquirer.

    Each acquirer should also define controllers to handle communication between
    OpenERP and the acquirer. It generally consists in return urls given to the
    button form and that the acquirer uses to send the customer back after the
    transaction, with transaction details given as a POST request.
    """
    _name = 'payment.acquirer'
    _description = 'Payment Acquirer'

    _columns = {
        'name': fields.char('Name', required=True),
        'message': fields.html('Message', help='Message displayed to help payment and validation'),
        'view_template_id': fields.many2one('ir.ui.view', 'Form Button Template', required=True),
        'env': fields.selection(
            [('test', 'Test'), ('prod', 'Production')],
            string='Environment'),
        'portal_published': fields.boolean('Visible in Portal',
                                           help="Make this payment acquirer available (Customer invoices, etc.)"),
    }

    _defaults = {
        'portal_published': True,
        'env': 'test',
    }

    def _check_required_if_provider(self, cr, uid, ids, context=None):
        """ If the field has 'required_if_provider="<name>"' attribute, then it
        required if record.name is <name>. """
        for acquirer in self.browse(cr, uid, ids, context=context):
            if any(c for c, f in self._all_columns.items() if getattr(f.column, 'required_if_provider', None) == acquirer.name and not acquirer[c]):
                return False
        return True

    _constraints = [
        (_check_required_if_provider, 'Required fields not filled', ['required for this provider']),
    ]

    def render(self, cr, uid, id, reference, amount, currency, tx_id=None, partner_id=False, partner_values=None, tx_custom_values=None, context=None):
        """ Renders the form template of the given acquirer as a qWeb template.
        All templates should handle:

         - acquirer: the payment.acquirer browse record
         - user: the current user browse record
         - currency: currency browse record
         - amount: amount of the transaction
         - reference: reference of the transaction
         - partner: the current partner browse record, if any (not necessarily set)
         - partner_values: a dictionary of partner-related values
         - tx_custom_values: a dictionary of transaction related values that depends
                             on the acquirer. Some specific keys should be managed
                             in each provider, depending on the features it offers:

          - 'feedback_url': feedback URL, controler that manage answer of the acquirer
                            (without base url)
          - 'return_url': URL for coming back after payment validation (wihout
                          base url)
          - 'cancel_url': URL if the client cancels the payment
          - 'error_url': URL if there is an issue with the payment

         - context: OpenERP context dictionary

        :param string reference: the transaction reference
        :param float amount: the amount the buyer has to pay
        :param res.currency browse record currency: currency
        :param int tx_id: id of a transaction; if set, bypasses all other given
                          values and only render the already-stored transaction
        :param res.partner browse record partner_id: the buyer
        :param dict partner_values: a dictionary of values for the buyer (see above)
        :param dict tx_custom_values: a dictionary of values for the transction
                                      that is given to the acquirer-specific method
                                      generating the form values
        :param dict context: OpenERP context
        """
        if context is None:
            context = {}
        partner = None
        if partner_id:
            partner = self.pool['res.partner'].browse(cr, uid, partner_id, context=context)
        acquirer = self.browse(cr, uid, id, context=context)
        method_name = '%s_form_generate_values' % (acquirer.name)

        if tx_id and hasattr(self.pool['payment.transaction'], method_name):
            method = getattr(self.pool['payment.transaction'], method_name)
            tx_values = method(cr, uid, tx_id, tx_custom_values, context=context)
        elif hasattr(self, method_name):
            method = getattr(self, method_name)
            tx_values = method(cr, uid, id, reference, amount, currency, partner_id, partner_values, tx_custom_values, context=context)
        else:
            tx_values = tx_custom_values

        qweb_context = {
            'acquirer': acquirer,
            'user': self.pool.get("res.users").browse(cr, uid, uid, context=context),
            'reference': reference,
            'amount': amount,
            'currency': currency,
            'partner': partner,
            'partner_values': partner_values,
            'tx_values': tx_values,
            'context': context,
        }
        # because render accepts view ids but not qweb -> need to find the xml_id
        return self.pool['ir.ui.view'].render(cr, uid, acquirer.view_template_id.xml_id, qweb_context, engine='ir.qweb', context=context)

    def get_form_action_url(self, cr, uid, id, context=None):
        acquirer = self.browse(cr, uid, id, context=context)
        if hasattr(self, '%s_get_form_action_url' % acquirer.name):
            return getattr(self, '%s_get_form_action_url' % acquirer.name)(cr, uid, id, context=context)
        return False


class PaymentTransaction(osv.Model):
    """ Transaction Model. Each specific acquirer can extend the model by adding
    its own fields.

    Methods that should be added in an acquirer-specific implementation:

     - ``<name>_form_generate_values(self, cr, uid, id, tx_custom_values=None,
       context=None)``: method that generates the values used to render the
       form button template.

    Methods that can be added in an acquirer-specific implementation:

     - ``<name>_create``: method receiving values used when creating a new
       transaction and that returns a dictionary that will update those values.
       This method can be used to tweak some transaction values.

    Methods defined for convention, depending on your controllers:

     - ``<name>_form_feedback(self, cr, uid, data, context=None)``: method that
       handles the data coming from the acquirer after the transaction. It will
       generally receives data posted by the acquirer after the transaction.
    """
    _name = 'payment.transaction'
    _description = 'Payment Transaction'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _rec_name = 'reference'

    _columns = {
        'date_create': fields.datetime('Creation Date', readonly=True, required=True),
        'date_validate': fields.datetime('Validation Date'),
        'acquirer_id': fields.many2one(
            'payment.acquirer', 'Acquirer',
            required=True,
        ),
        'type': fields.selection(
            [('server2server', 'Server To Server'), ('form', 'Form')],
            string='Type', required=True),
        'state': fields.selection(
            [('draft', 'Draft'), ('pending', 'Pending'),
             ('done', 'Done'), ('error', 'Error'),
             ('cancel', 'Canceled')
             ], 'Status', required=True,
            track_visiblity='onchange'),
        'state_message': fields.text('Message',
                                     help='Field used to store error and/or validation messages for information'),
        # payment
        'amount': fields.float('Amount', required=True,
                               help='Amount in cents',
                               track_visibility='always'),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True),
        'reference': fields.char('Order Reference', required=True),
        # duplicate partner / transaction data to store the values at transaction time
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'partner_name': fields.char('Partner Name'),
        'partner_lang': fields.char('Lang'),
        'partner_email': fields.char('Email'),
        'partner_zip': fields.char('Zip'),
        'partner_address': fields.char('Address'),
        'partner_city': fields.char('City'),
        'partner_country_id': fields.many2one('res.country', 'Country'),
        'partner_phone': fields.char('Phone'),
        'partner_reference': fields.char('Buyer Reference'),
    }

    _sql_constraints = [
        ('reference_uniq', 'UNIQUE(reference)', 'The payment transaction reference must be unique!'),
    ]

    _defaults = {
        'date_create': fields.datetime.now,
        'type': 'form',
        'state': 'draft',
        'partner_lang': 'en_US',
    }

    def create(self, cr, uid, values, context=None):
        if values.get('partner_id'):  # @TDENOTE: not sure
            values.update(self.on_change_partner_id(cr, uid, None, values.get('partner_id'), context=context)['values'])

        # call custom create method if defined (i.e. ogone_create for ogone)
        if values.get('acquirer_id'):
            acquirer = self.pool['payment.acquirer'].browse(cr, uid, values.get('acquirer_id'), context=context)
            custom_method_name = '%s_create' % acquirer.name
            if hasattr(self, custom_method_name):
                values.update(getattr(self, custom_method_name)(cr, uid, values, context=context))

        return super(PaymentTransaction, self).create(cr, uid, values, context=context)

    def on_change_partner_id(self, cr, uid, ids, partner_id, context=None):
        if partner_id:
            partner = self.pool['res.partner'].browse(cr, uid, partner_id, context=context)
            values = {
                'partner_name': partner.name,
                'partner_lang': partner.lang,
                'partner_email': partner.email,
                'partner_zip': partner.zip,
                'partner_address': _partner_format_address(partner.street, partner.street2),
                'partner_city': partner.city,
                'partner_country_id': partner.country_id.id,
                'partner_phone': partner.phone,
            }
        else:
            values = {
                'partner_name': False,
                'partner_lang': 'en_US',
                'partner_email': False,
                'partner_zip': False,
                'partner_address': False,
                'partner_city': False,
                'partner_country_id': False,
                'partner_phone': False,
            }
        return {'values': values}

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    def form_feedback(self, cr, uid, data, acquirer_name, context=None):
        invalid_parameters, tx = None, None

        tx_find_method_name = '_%s_form_get_tx_from_data' % acquirer_name
        if hasattr(self, tx_find_method_name):
            tx = getattr(self, tx_find_method_name)(cr, uid, data, context=context)

        invalid_param_method_name = '_%s_form_get_invalid_parameters' % acquirer_name
        if hasattr(self, invalid_param_method_name):
            invalid_parameters = getattr(self, invalid_param_method_name)(cr, uid, tx, data, context=context)

        if invalid_parameters:
            _error_message = '%s: incorrect tx data:\n' % (acquirer_name)
            for item in invalid_parameters:
                _error_message += '\t%s: received %s instead of %s\n' % (item[0], item[1], item[2])
            _logger.error(_error_message)
            return False

        feedback_method_name = '_%s_form_validate' % acquirer_name
        if hasattr(self, feedback_method_name):
            return getattr(self, feedback_method_name)(cr, uid, tx, data, context=context)

        return True

    # --------------------------------------------------
    # SERVER2SERVER RELATED METHODS
    # --------------------------------------------------

    def create_s2s(self, cr, uid, tx_values, cc_values, context=None):
        tx_id = self.create(cr, uid, tx_values, context=context)
        return tx_id
