# -*- coding: utf-'8' "-*-"

from openerp.osv import osv

import logging

_logger = logging.getLogger(__name__)


class TransferPaymentAcquirer(osv.Model):
    _inherit = 'payment.acquirer'


class TransferPaymentTransaction(osv.Model):
    _inherit = 'payment.transaction'
