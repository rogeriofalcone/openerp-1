# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

from osv import osv, fields
import time

class training_course_category(osv.osv):
    _name = 'training.course_category'
    _inherits = {
        'account.analytic.account' : 'analytic_account_id',
    }

    def _get_child_ids( self, cr, uid, ids, name, args, context ):
        res = {}
        for object in self.browse(cr, uid, ids):
            child_ids = self.pool.get('account.analytic.account').search(cr, uid, [('parent_id', '=', object.analytic_account_id.id)])
            res[object.id] = self.search(cr, uid, [('analytic_account_id', 'in', child_ids)])

        return res

    _columns = {
        'analytic_account_id' : fields.many2one( 'account.analytic.account', 'Analytic Account' ),
        'description' : fields.text('Description'),
        'child_ids' : fields.function( _get_child_ids, method=True, type='one2many', relation="training.course", string='Children'),
    }

training_course_category()

class training_course_type(osv.osv):
    _name = 'training.course_type'

    _columns = {
        'name' : fields.char('Name', size=32, required=True, select=1),
        'objective' : fields.text('Objective'),
        'description' : fields.text('Description'),
        'min_limit' : fields.integer('Minimum Limit', required=True, select=2),
        'max_limit' : fields.integer('Maximum Limit', required=True, select=2),
    }

training_course_type()

class training_course(osv.osv):
    _name = 'training.course'
training_course()

class training_course_purchase_line(osv.osv):
    _name = 'training.course.purchase_line'
    _rec_name = 'course_id'
    _columns = {
        'course_id' : fields.many2one('training.course', 'course', required=True),
        'product_id' : fields.many2one('product.product', 'Product', required=True),
        'quantity' : fields.integer('Quantity', required=True),
        'uom_id' : fields.many2one('product.uom', 'UoM', required=True),
    }
training_course_purchase_line()

class training_offer(osv.osv):
    _name = 'training.offer'
training_offer()

class training_course(osv.osv):
    _name = 'training.course'
    _inherits = {
        'account.analytic.account' : 'analytic_account_id'
    }

    def _total_duration_compute(self,cr,uid,ids,name,args,context):
        res = {}
        for object in self.browse( cr, uid, ids, context=context ):
            res[object.id] = 0.0
        return res

    def _get_child_ids( self, cr, uid, ids, name, args, context ):
        res = {}
        for object in self.browse(cr, uid, ids):
            child_ids = self.pool.get('account.analytic.account').search(cr, uid, [('parent_id', '=', object.analytic_account_id.id)])
            res[object.id] = self.search(cr, uid, [('analytic_account_id', 'in', child_ids)])
        return res

    _columns = {
        'duration' : fields.time('Duration',
                                 required=True,
                                 help="Duration for a standalone course"),
        'children' : fields.function(_get_child_ids,
                                     method=True,
                                     type='one2many',
                                     relation="training.course",
                                     string='Children'),
        'total_duration' : fields.function(_total_duration_compute,
                                           string='Total Duration',
                                           readonly=True,
                                           store=True,
                                           method=True,
                                           type="time"),
        'sequence' : fields.integer('Sequence'),
        'target_public' : fields.char('Target Public',
                                      size=256,
                                      help="Allows the participants to select a course whose can participate"),
        'reference_id' : fields.many2one('training.course',
                                         'Master Course',
                                         help="The master course is necessary if the user wants to link certain courses together to easy the managment"),
        'analytic_account_id' : fields.many2one( 'account.analytic.account', 'Account' ),
        'course_type_id' : fields.many2one('training.course_type', 'Type',
                                           required=True),
        'lecturer_ids' : fields.many2many('res.partner', 
                                            'training_course_partner_rel',
                                            'course_id',
                                            'partner_id',
                                            'Lecturers',
                                            help="The lecturers who give the course"
                                           ),
        'internal_note' : fields.text('Note'),
        'lang_id' : fields.many2one('res.lang', 'Language', required=True),
        'offer_ids' : fields.many2many('training.offer',
                                       'training_course_offer_rel',
                                       'course_id',
                                       'offer_id',
                                       'Offers',
                                       help="The offers containing the course"
                                      ),
        'state_course' : fields.selection([('draft', 'Draft'),
                                           ('pending', 'Pending'),
                                           ('inprogress', 'In Progress'),
                                           ('deprecated', 'Deprecated'),
                                           ('validate', 'Validate'),
                                          ],
                                          'State',
                                          required=True,
                                          readonly=True,
                                          select=1
                                         ),
        'purchase_line_ids' : fields.one2many('training.course.purchase_line', 'course_id',
                                              'Supplier Commands'),
    }

    _defaults = {
        'state_course' : lambda *a: 'draft',
    }

training_course()

class training_offer(osv.osv):
    _name = 'training.offer'
    _columns = {
        'name' : fields.char('Name', size=64, required=True, select=1),
        'product_id' : fields.many2one('product.product', 'Product'),
        'course_ids' : fields.many2many('training.course',
                                        'training_course_offer_rel',
                                        'offer_id',
                                        'course_id',
                                        'Courses',
                                        domain="[('state', '=', 'validate')]"
                                       ),
        'objective' : fields.text('Objective'),
        'description' : fields.text('Description'),
        'state' : fields.selection([('draft', 'Draft'),
                                    ('validate', 'Validate'),
                                    ('deprecated', 'Deprecated')
                                   ],
                                   'State',
                                   required=True,
                                   readonly=True,
                                   select=1),
    }

    _defaults = {
        'state' : lambda *a: 'draft',
    }

training_offer()

class training_catalog(osv.osv):
    _name = 'training.catalog'
    _rec_name = 'year'
    _columns = {
        'year' : fields.integer('Year', size=4, required=True, select=1),
        'session_ids' : fields.one2many('training.session', 'catalog_id', 'Sessions'),
        'note' : fields.text('Note'),
        'state' : fields.selection([('draft','Draft'),
                                    ('inprogress', 'In Progress'),
                                    ('done','Done')],
                                   'State',
                                   required=True,
                                   readonly=True,
                                   select=1),
    }

    _defaults = {
        'year' : lambda *a: int(time.strftime('%Y'))+1,
        'state' : lambda *a: 'draft',
    }

training_catalog()

class training_event(osv.osv):
    _name = 'training.event'
training_event()

class training_session(osv.osv):
    _name = 'training.session'
    _columns = {
        'name' : fields.char('Name', size=64, required=True, select=1),
        'state' : fields.selection([('draft', 'Draft'),
                                    ('open_pending', 'Open and Pending'),
                                    ('inprogress', 'In Progress'),
                                    ('validate', 'Validate'),
                                    ('closed', 'Closed'),
                                    ('cancel', 'Cancel')],
                                   'State',
                                   required=True,
                                   readonly=True,
                                   select=1
                                  ),
        'offer_id' : fields.many2one('training.offer', 'Offer', select=1, required=True),
        'catalog_id' : fields.many2one('training.catalog', 'Catalog', select=1),
        'event_ids' : fields.many2many('training.event',
                                       'training_session_event_rel',
                                       'session_id',
                                       'event_id',
                                       'Events',
                                       ondelete='cascade'),
        'date' : fields.datetime('Date', required=True),
        'purchase_line_ids' : fields.one2many('training.session.purchase_line', 'session_id', 'Supplier Commands'),
    }

    def _find_catalog_id(self,cr,uid,data,context=None):
        new_year = int(time.strftime('%Y')) + 1
        catalog_proxy = self.pool.get('training.catalog')
        catalog_ids = catalog_proxy.search(cr,uid,[('year', '=', new_year)],context=context)
        if catalog_ids:
            return catalog_ids[0]
        else:
            return None

    _defaults = {
        'catalog_id' : _find_catalog_id,
        'state' : lambda *a: 'draft',
    }


training_session()

class training_session_purchase_line(osv.osv):
    _name = 'training.session.purchase_line'
    _rec_name = 'session_id'

    _columns = {
        'session_id' : fields.many2one('training.session', 'Session', required=True),
        'product_id' : fields.many2one('product.product', 'Product', required=True),
        'quantity' : fields.integer('Quantity', required=True),
        'uom_id' : fields.many2one('product.uom', 'UoM', required=True),
    }

training_session_purchase_line()

class training_massive_subscription_wizard(osv.osv_memory):
    _name = 'wizard.training.massive.subscription'

    def action_cancel(self, cr, uid, ids, context = None):
        return { 'type' : 'ir.actions.act_window_close' }

    def action_apply(self, cr, uid, ids, context = None):
        # Creation des inscriptions dans l'objet training.subscription
        this = self.browse(cr, uid, ids)[0]

        subscription_proxy = self.pool.get('training.subscription')
        for partner in this.partner_ids:
            for session in this.session_ids:
                vals = {
                    'partner_id' : partner.id,
                    'session_id' : session_id,
                }
                subscription_id = subscription_proxy.create(cr, uid, vals, context = context )
        return { 'type' : 'ir.actions.act_window_close' }

    _columns = {
        'partner_ids' : fields.many2many('res.partner.contact',
                                         'tmi_partner_rel',
                                         'wiz_id',
                                         'partner_id',
                                         'Partners',
                                         required=True ),
        'session_ids' : fields.many2many('training.session',
                                         'tmi_session_rel',
                                         'wiz_id',
                                         'session_id',
                                         'Sessions',
                                         required=True ),
    }

training_massive_subscription_wizard()

class training_location(osv.osv):
    _name = 'training.location'

    _columns = {
        'name' : fields.char('Name', size=32, select=True, required=True),
    }

training_location()

class training_group(osv.osv):
    _name = 'training.group'
    _columns = {
        'name': fields.char('Name', size=64, required=True, select=True),
    }
training_group()

class training_subscription(osv.osv):
    _name = 'training.subscription'
training_subscription()

class training_event(osv.osv):
    _name = 'training.event'

    def _check_date(self,cr,uid,ids,context=None):
        return self.browse(cr, uid, ids)[0].date > time.strftime('%Y-%m-%d')

    def _support_ok_get( self, cr, uid, ids, name, args, context ):
        return {}.fromkeys(ids, True)

    _columns = {
        'name' : fields.char('Name', size=64, select=1, required=True),
        'session_ids' : fields.many2many('training.session',
                                         'training_session_event_rel',
                                         'event_id',
                                         'session_id',
                                         'Sessions',
                                         ondelete='cascade'),
        # Attention, la date doit etre obligatoire
        'date' : fields.datetime('Date', required=False, select=1),
        'duration' : fields.time('Duration', required=False, select=1),
        'location_id' : fields.many2one('training.location', 'Location', select=1),
        'participant_ids' : fields.many2many('training.subscription',
                                             'training_participation',
                                             'event_id',
                                             'subscription_id',
                                             'Participants',
                                             domain="[('group_id', '=', group_id)]" ),
        'group_id' : fields.many2one('training.group', 'Group'),
        'support_ok' : fields.function(_support_ok_get, 
                                       method=True,
                                       type="boolean",
                                       string="Support OK",
                                       readonly=True),
        'state' : fields.selection([('draft', 'Draft'),
                                    ('open_pending', 'Open and Pending'),
                                    ('validate', 'Validate'),
                                    ('inprogress', 'In Progress'),
                                    ('closed', 'Closed'),
                                    ('cancel', 'Cancel')],
                                   'State',
                                   required=True,
                                   readonly=True,
                                   select=1
                                  ),
    }

    _constraints = [
        ( _check_date, "Errorr, Can you check your start date", ['date']),
    ]

    _defaults = {
        'state' : lambda *a: 'draft',
        'date' : lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

training_event()

class training_seance(osv.osv):
    _name = 'training.seance'
    _inherits = { 'training.event' : 'event_id' }

    _columns = {
        'partner_ids' : fields.many2many('res.partner', 'training_seance_partner_rel', 'seance_id', 'partner_id', 'StakeHolders'),
        'event_id' : fields.many2one('training.event', 'Event'),
        'course_id' : fields.many2one('training.course', 'Course', required=True),
        #'copies' : fields.integer('Copies'),
        #'printed' : fields.boolean('Printed'),
        'reserved' : fields.boolean('Reserved'),
        'layout' : fields.char('Layout', size=32),
        'place' : fields.char('Place', size=32),
        'room' : fields.char('Room', size=32),
        #'limit' : fields.integer('Limit'), 
        'purchase_line_ids' : fields.one2many('training.seance.purchase_line', 'seance_id', 'Supplier Commands'),
    }

training_seance()

class training_seance_purchase_line(osv.osv):
    _name = 'training.seance.purchase_line'
    _rec_name = 'product_id'

    _columns = {
        'seance_id' : fields.many2one('training.seance', 'Seance', required=True),
        'product_id' : fields.many2one('product.product', 'Product', required=True),
        'quantity' : fields.integer('Quantity', required=True),
        'uom_id' : fields.many2one('product.uom', 'UoM', required=True),
        'procurement_id' : fields.many2one('mrp.procurement', readonly=True),
    }

training_seance_purchase_line()

class training_subscription(osv.osv):
    _name = 'training.subscription'
    _columns = {
        'name' : fields.char( 'Reference', size=32, required=True, select=1,readonly=True ),
        'date' : fields.datetime( 'Date', required=True, select=True ),
        'session_id' : fields.many2one( 'training.session', 'Session', select=1, required=True),
        'contact_id' : fields.many2one( 'res.partner.contact', 'Contact', select=1, required=True),
        'partner_id' : fields.many2one( 'res.partner', 'Partner', select=1, required=True),
        'address_id' : fields.many2one( 'res.partner.address', 'Invoice Address', select=1, required=True),
        # Pour le group ID, discuter pour savoir si on doit utiliser le seuil pédagogique du groupe pour savoir si on crée un nouveau group ou non
        'invoice_id' : fields.many2one( 'account.invoice', 'Invoice' ),
        'group_id' : fields.many2one( 'training.group', 'Group'),
        'state' : fields.selection([('draft', 'Draft'),
                                    ('confirm','Confirm'),
                                    ('cancel','Cancel'),
                                    ('done', 'Done')
                                   ],
                                   'State',
                                   readonly=True,
                                   required=True,
                                   select=1),
        'price' : fields.float('Price', digits=(16,2), required=True),
        'paid' : fields.boolean('Paid'),
    }

    _defaults = {
        'state' : lambda *a: 'draft',
        'paid' : lambda *a: False,
        'name' : lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'training.subscription'),
    }

training_subscription()

class training_participation(osv.osv):
    _name = 'training.participation'
    _columns = {
        'event_id' : fields.many2one('training.event', 'Event' ),
        'subscription_id' : fields.many2one('training.subscription', 'Subscription', select=True, required=True),
    }

training_participation()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
