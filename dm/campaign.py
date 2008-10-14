# -*- encoding: utf-8 -*-
import time
import datetime
import offer
import warnings
import netsvc
from mx import DateTime

from osv import fields
from osv import osv


class dm_campaign_group(osv.osv):
    _name = "dm.campaign.group"

    def po_generate(self,cr, uid, ids, *args):








        return True

    _columns = {
        'name': fields.char('Campaign group name', size=64, required=True),
        'code': fields.char('Code', size=64, required=True),
        'project_id' : fields.many2one('project.project', 'Project', readonly=True),
        'campaign_ids': fields.one2many('dm.campaign', 'campaign_group_id', 'Campaigns', domain=[('campaign_group_id','=',False)]),
    }
dm_campaign_group()


class dm_campaign_type(osv.osv):
    _name = "dm.campaign.type"

    _columns = {
        'name': fields.char('Description', size=64, required=True),
        'code': fields.char('Code', size=16, required=True),
    }
dm_campaign_type()


class dm_overlay(osv.osv):
    _name = 'dm.overlay'
    _rec_name = 'trademark_id'

    def create(self,cr,uid,vals,context={}):
        id = super(dm_overlay,self).create(cr,uid,vals,context)
        data = self.browse(cr, uid, id)
        overlay_country_ids = [country_ids.id for country_ids in data.country_ids]
        dealer_country_ids = [country_ids.id for country_ids in data.dealer_id.country_ids]
        for i in overlay_country_ids:
            if not i in dealer_country_ids:
                raise  osv.except_osv('Warning', "This country is not allowed for %s" % (data.dealer_id.name,) )
        return id
    
    def _overlay_code(self, cr, uid, ids, name, args, context={}):
        result ={}
        for id in ids:

            overlay = self.browse(cr,uid,id)
            trademark_code = overlay.trademark_id.code or ''
            dealer_code = overlay.dealer_id.ref or ''
            code1='-'.join([trademark_code, dealer_code])
            result[id]=code1
        return result

    _columns = {
        'code' : fields.function(_overlay_code,string='Code',type='char',method=True,readonly=True),
        'trademark_id' : fields.many2one('dm.trademark', 'Trademark', required=True),
        'dealer_id' : fields.many2one('res.partner', 'Dealer',domain=[('category_id','ilike','Dealer')], context={'category':'Dealer'}, required=True),
        'country_ids' : fields.many2many('res.country', 'overlay_country_rel', 'overlay_id', 'country_id', 'Country', required=True),
        'bank_account_id' : fields.many2one('account.account', 'Account'),
    }
dm_overlay()


class one2many_mod_task(fields.one2many):
    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
        if not context:
            context = {}
        if not values:
                values = {}
        res = {}
        for id in ids:
            res[id] = []
        for id in ids:
            query = "select project_id from dm_campaign where id = %i" %id
            cr.execute(query)
            project_ids = [ x[0] for x in cr.fetchall()]
            if name[0] == 'd':
                ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',project_ids),('type','=','DTP')], limit=self._limit)
            elif name[0] == 'm':
                ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',project_ids),('type','=','Mailing Manufacturing')], limit=self._limit)
            elif name[0] == 'c':
                ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',project_ids),('type','=','Customer List')], limit=self._limit)
            else :
                ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',project_ids),('type','=','Mailing Manufacturing')], limit=self._limit)
            for r in obj.pool.get(self._obj)._read_flat(cr, user, ids2, [self._fields_id], context=context, load='_classic_write'):
                res[id].append( r['id'] )
        return res

class dm_campaign(osv.osv):
    _name = "dm.campaign"
    _inherits = {'account.analytic.account': 'analytic_account_id'}
    _rec_name = 'name'

    def dtp_making_time_get(self, cr, uid, ids, name, arg, context={}):
        result={}
        for i in ids:
            result[i]=0.0
        return result

    def _campaign_code(self, cr, uid, ids, name, args, context={}):
        result ={}
        for id in ids:
            camp = self.browse(cr,uid,[id])[0]
            offer_code = camp.offer_id and camp.offer_id.code or ''
            trademark_code = camp.trademark_id and camp.trademark_id.code or ''
            dealer_code =camp.dealer_id and camp.dealer_id.ref or ''
            date_start = camp.date_start or ''
            country_code = camp.country_id.code or ''
            date = date_start.split('-')
            year = month = ''
            if len(date)==3:
                year = date[0][2:]
                month = date[1]
            final_date=month+year
            code1='-'.join([offer_code ,dealer_code ,trademark_code ,final_date ,country_code])
            result[id]=code1
        return result

    def _get_campaign_type(self,cr,uid,context={}):
        campaign_type = self.pool.get('dm.campaign.type')
        type_ids = campaign_type.search(cr,uid,[])
        type = campaign_type.browse(cr,uid,type_ids)
        return map(lambda x : [x.code,x.name],type)

    def onchange_lang_currency(self, cr, uid, ids, country_id):
        value = {}
        if country_id:
            country = self.pool.get('res.country').browse(cr,uid,[country_id])[0]
            value['lang_id'] =  country.main_language.id
            value['currency_id'] = country.main_currency.id
        else:
            value['lang_id']=0
            value['currency_id']=0
        return {'value':value}

    def _quantity_theorical_total(self, cr, uid, ids, name, args, context={}):
        result={}
        campaigns = self.browse(cr,uid,ids)
        for campaign in campaigns:
            quantity=0
            numeric=True
            for propo in campaign.proposition_ids:
                if propo.quantity_theorical.isdigit():
                    quantity += int(propo.quantity_theorical)
                else:
                    result[campaign.id]='Check Segments'
                    numeric=False
                    break
            if numeric:
                result[campaign.id]=str(quantity)
        return result

    def _quantity_wanted_total(self, cr, uid, ids, name, args, context={}):
        result={}
        campaigns = self.browse(cr,uid,ids)
        for campaign in campaigns:
            quantity=0
            numeric=True
            for propo in campaign.proposition_ids:
                if propo.quantity_wanted.isdigit():
                    quantity += int(propo.quantity_wanted)
                elif propo.quantity_wanted == "AAA for a Segment":
                    result[campaign.id]='AAA for a Segment'
                    numeric=False
                    break
                else:
                    result[campaign.id]='Check Segments'
                    numeric=False
                    break
            if numeric:
                result[campaign.id]=str(quantity)
        return result

    def _quantity_delivered_total(self, cr, uid, ids, name, args, context={}):
        result={}
        campaigns = self.browse(cr,uid,ids)
        for campaign in campaigns:
            quantity=0
            numeric=True
            for propo in campaign.proposition_ids:
                if propo.quantity_delivered.isdigit():
                    quantity += int(propo.quantity_delivered)
                else:
                    result[campaign.id]='Check Segments'
                    numeric=False
                    break
            if numeric:
                result[campaign.id]=str(quantity)
        return result

    def _quantity_real_total(self, cr, uid, ids, name, args, context={}):
        result={}
        campaigns = self.browse(cr,uid,ids)
        for campaign in campaigns:
            quantity=0
            numeric=True
            for propo in campaign.proposition_ids:
                if propo.quantity_real.isdigit():
                    quantity += int(propo.quantity_real)
                else:
                    result[campaign.id]='Check Segments'
                    numeric=False
                    break
            if numeric:
                result[campaign.id]=str(quantity)
        return result


    _columns = {
        'code1' : fields.function(_campaign_code,string='Code',type="char",size="64",method=True,readonly=True),
        'offer_id' : fields.many2one('dm.offer', 'Offer',domain=[('state','=','open'),('type','in',['new','standart','rewrite'])],
            help="Choose the commercial offer to use with this campaign, only offers in open state can be assigned"),
        'country_id' : fields.many2one('res.country', 'Country',required=True, 
            help="The language and currency will be automaticaly assigned if they are defined for the country"),
        'lang_id' : fields.many2one('res.lang', 'Language'),
        'trademark_id' : fields.many2one('dm.trademark', 'Trademark'),
        'project_id' : fields.many2one('project.project', 'Project', readonly=True,
            help="Generating the Retro Planning will create and assign the different tasks used to plan and manage the campaign"),
        'campaign_group_id' : fields.many2one('dm.campaign.group', 'Campaign group'),
        'notes' : fields.text('Notes'),
        'proposition_ids' : fields.one2many('dm.campaign.proposition', 'camp_id', 'Proposition'),
        'campaign_type' : fields.selection(_get_campaign_type,'Type',required=True),
        'analytic_account_id' : fields.many2one('account.analytic.account','Analytic Account', ondelete='cascade'),
        'planning_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Planning Status',readonly=True),
        'items_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Items Status',readonly=True),
        'translation_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Translation Status',readonly=True),
        'manufacturing_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Manufacturing Status',readonly=True),
        'customer_file_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Customers Files Status',readonly=True),
        'dealer_id' : fields.many2one('res.partner', 'Dealer',domain=[('category_id','ilike','Dealer')], context={'category':'Dealer'},
            help="The dealer is the partner the campaign is planned for"),
        'responsible_id' : fields.many2one('res.users','Responsible'),
        'manufacturing_responsible_id' : fields.many2one('res.users','Responsible'),
        'dtp_responsible_id' : fields.many2one('res.users','Responsible'),
        'files_responsible_id' : fields.many2one('res.users','Responsible'),
        'invoiced_partner_id' : fields.many2one('res.partner','Invoiced Partner'),
        'dtp_making_time' : fields.function(dtp_making_time_get, method=True, type='float', string='Making Time'),
        'deduplicator_id' : fields.many2one('res.partner','Deduplicator',domain=[('category_id','ilike','Deduplicator')], context={'category':'Deduplicator'},
            help="The deduplicator is a partner responsible to remove identical addresses from the customers list"),
        'cleaner_id' : fields.many2one('res.partner','Cleaner',domain=[('category_id','ilike','Cleaner')], context={'category':'Cleaner'},
            help="The cleaner is a partner responsible to remove bad addresses from the customers list"),
        'currency_id' : fields.many2one('res.currency','Currency',ondelete='cascade'),
        'manufacturing_cost_ids': fields.one2many('dm.campaign.manufacturing_cost','campaign_id','Manufacturing Costs'),
        'manufacturing_product': fields.many2one('product.product','Manufacturing Product'),
        'purchase_line_ids': fields.one2many('dm.campaign.purchase_line', 'campaign_id', 'Purchase Lines'),
        'overlay_id': fields.many2one('dm.overlay', 'Overlay'),
        'owner_id' : fields.many2one('res.partner', 'Owner',domain=[('category_id','ilike','Owner')], context={'category':'Owner'}),
        'router_id' : fields.many2one('res.partner', 'Router',domain=[('category_id','ilike','Router')], context={'category':'Router'}),
        'dtp_task_ids': one2many_mod_task('project.task', 'project_id', "DTP tasks",
                                                        domain=[('type','ilike','DTP')], context={'type':'DTP'}),
        'manufacturing_task_ids': one2many_mod_task('project.task', 'project_id', "Manufacturing tasks",
                                                        domain=[('type','ilike','Mailing Manufacturing')],context={'type':'Mailing Manufacturing'}),
        'cust_file_task_ids': one2many_mod_task('project.task', 'project_id', "Customer Lists tasks",
                                                        domain=[('type','ilike','Customers List')], context={'type':'Customers List'}),
        'quantity_theorical_total' : fields.function(_quantity_theorical_total, string='Total Theorical Quantity',type="char",size="64",method=True,readonly=True),
        'quantity_wanted_total' : fields.function(_quantity_wanted_total, string='Total Wanted Quantity',type="char",size="64",method=True,readonly=True),
        'quantity_delivered_total' : fields.function(_quantity_delivered_total, string='Total Delivered Quantity',type="char",size="64",method=True,readonly=True),
        'quantity_real_total' : fields.function(_quantity_real_total, string='Total Real Quantity',type="char",size="64",method=True,readonly=True),
    }

    _defaults = {
        'state': lambda *a: 'draft',
        'manufacturing_state': lambda *a: 'pending',
        'items_state': lambda *a: 'pending',
        'translation_state': lambda *a: 'pending',
        'customer_file_state': lambda *a: 'pending',
        'campaign_type': lambda *a: 'general',
        'responsible_id' : lambda obj, cr, uid, context: uid,
    }

    def state_draft_set(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'draft'})
        return True

    def state_close_set(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'close'})
        return True

    def state_pending_set(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'pending'})
        return True

    def state_open_set(self, cr, uid, ids, *args):
        camp = self.browse(cr,uid,ids)[0]
        if camp.offer_id:
            forbidden_state_ids = [state_id.country_id.id for state_id in camp.offer_id.forbidden_state_ids]
            forbidden_country_ids = [country_id.id for country_id in camp.offer_id.forbidden_country_ids]
            forbidden_country_ids.extend(forbidden_state_ids)
            if camp.offer_id.forbidden_country_ids and camp.country_id.id  in  forbidden_country_ids :
                raise osv.except_osv("Error!!","This offer is not valid in this country")
        if not camp.date_start or not camp.dealer_id or not camp.trademark_id :
            raise osv.except_osv("Error!!","Informations are missing. Check Date Start, Dealer and Trademark")
        super(dm_campaign,self).write(cr, uid, ids, {'state':'open','planning_state':'inprogress'})
        return True

    def write(self, cr, uid, ids, vals, context=None):
        res = super(dm_campaign,self).write(cr, uid, ids, vals, context)
        camp = self.pool.get('dm.campaign').browse(cr,uid,ids)[0]
        srch_offer_ids = self.search(cr, uid, [('offer_id', '=', camp.offer_id.id)])

        c = camp.country_id.id
        if 'date_start' in vals and vals['date_start'] and camp.project_id:
            self.pool.get('project.project').write(cr,uid,[camp.project_id.id],{'date_end':vals['date_start']})
        if camp.offer_id:
            d = camp.offer_id.id
            offers = self.pool.get('dm.offer').browse(cr, uid, d)
            list_off = []
            for off in offers.forbidden_country_ids:
                list_off.append(off.id)
                if c in list_off:
                    raise osv.except_osv("Error!!","You cannot use this offer in this country")

            """ In campaign, if no trademark is given, it gets the 'recommended trademark' from offer """
            if not camp.trademark_id:
                super(osv.osv, self).write(cr, uid, camp.id, {'trademark_id':offers.recommended_trademark.id})

        # check if an overlay exists else create it
        overlay_country_ids=[]
        camp1 = self.browse(cr, uid, camp.id)
        if camp1.trademark_id and camp1.dealer_id and camp1.country_id:
            overlay = self.pool.get('dm.overlay').search(cr, uid, [('trademark_id','=',camp1.trademark_id.id), ('dealer_id','=',camp1.dealer_id.id)])

            for o_id in overlay:
                browse_overlay = self.pool.get('dm.overlay').browse(cr, uid, o_id)
                overlay_country_ids = [country_ids.id for country_ids in browse_overlay.country_ids]

            if overlay and (camp1.country_id.id in overlay_country_ids):
                super(osv.osv, self).write(cr, uid, camp1.id, {'overlay_id':overlay[0]}, context)  
            elif overlay and not (camp1.country_id.id in overlay_country_ids):
                overlay_country_ids.append(camp1.country_id.id)
                self.pool.get('dm.overlay').write(cr, uid, browse_overlay.id, {'country_ids':[[6,0,overlay_country_ids]]}, context)
                super(osv.osv, self).write(cr, uid, camp1.id, {'overlay_id':overlay[0]}, context)
            else:
                overlay_country_ids.append(camp1.country_id.id)
                overlay_ids1 = self.pool.get('dm.overlay').create(cr, uid, {'trademark_id':camp1.trademark_id.id, 'dealer_id':camp1.dealer_id.id, 'country_ids':[[6,0,overlay_country_ids]]}, context)
                super(osv.osv, self).write(cr, uid, camp1.id, {'overlay_id':overlay_ids1}, context)
        else:
            super(osv.osv, self).write(cr, uid, camp1.id, {'overlay_id':0}, context)

        return res

    def create(self,cr,uid,vals,context={}):
        if context.has_key('campaign_type') and context['campaign_type']=='model':
            vals['campaign_type']='model'

        id_camp = super(dm_campaign,self).create(cr,uid,vals,context)

        data_cam = self.browse(cr, uid, id_camp)
        # Set campaign end date at one year after start date
        if (data_cam.date_start) and (not data_cam.date):
            time_format = "%Y-%m-%d"
            d = time.strptime(data_cam.date_start,time_format)
            d = datetime.date(d[0], d[1], d[2])
            date_end = d + datetime.timedelta(days=365)
            super(dm_campaign,self).write(cr, uid, id_camp, {'date':date_end})

        # Set trademark to offer's trademark only if trademark is null
        if not vals['campaign_type'] == 'model':
            if vals['offer_id'] and (not vals['trademark_id']):
                offer_id = self.pool.get('dm.offer').browse(cr, uid, vals['offer_id'])
                super(dm_campaign,self).write(cr, uid, id_camp, {'trademark_id':offer_id.recommended_trademark.id})

        # check if an overlay exists else create it
        data_cam1 = self.browse(cr, uid, id_camp)
        overlay_country_ids = []
        if data_cam1.trademark_id and data_cam1.dealer_id and data_cam1.country_id:
            overlay = self.pool.get('dm.overlay').search(cr, uid, [('trademark_id','=',data_cam1.trademark_id.id), ('dealer_id','=',data_cam1.dealer_id.id)])
            for o_id in overlay:
                browse_overlay = self.pool.get('dm.overlay').browse(cr, uid, o_id)
                overlay_country_ids = [country_ids.id for country_ids in browse_overlay.country_ids]
            if overlay and (data_cam1.country_id.id in overlay_country_ids):
                super(osv.osv, self).write(cr, uid, data_cam1.id, {'overlay_id':overlay[0]}, context)  
            elif overlay and not (data_cam1.country_id.id in overlay_country_ids):
                overlay_country_ids.append(data_cam1.country_id.id)
                self.pool.get('dm.overlay').write(cr, uid, browse_overlay.id, {'country_ids':[[6,0,overlay_country_ids]]}, context)
                super(osv.osv, self).write(cr, uid, data_cam1.id, {'overlay_id':overlay[0]}, context)
            else:
                overlay_country_ids.append(data_cam1.country_id.id)
                overlay_ids1 = self.pool.get('dm.overlay').create(cr, uid, {'trademark_id':data_cam1.trademark_id.id, 'dealer_id':data_cam1.dealer_id.id, 'country_ids':[[6,0,overlay_country_ids]]}, context)
                super(osv.osv, self).write(cr, uid, data_cam1.id, {'overlay_id':overlay_ids1}, context)

        return id_camp

    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False):
        result = super(dm_campaign,self).fields_view_get(cr, user, view_id, view_type, context, toolbar)
        if context.has_key('campaign_type'):
            if context['campaign_type'] == 'model' :
                if result.has_key('toolbar'):
                    result['toolbar']['action'] =[]
        return result

    def copy_campaign(self,cr, uid, ids, *args):
        camp = self.browse(cr,uid,ids)[0]
        default={}
        default['name']='New campaign from model %s' % camp.name
        default['campaign_type'] = 'recruiting'
        default['responsible_id'] = uid
        self.copy(cr,uid,ids[0],default)
        return True

    def copy(self, cr, uid, id, default=None, context={}):
        cmp_id = super(dm_campaign, self).copy(cr, uid, id, default)
        data = self.browse(cr, uid, cmp_id, context)
        default='Copy of %s' % data.name
        super(dm_campaign, self).write(cr, uid, cmp_id, {'name':default, 'date_start':0, 'date':0, 'project_id':0})
        return cmp_id

dm_campaign()


class dm_campaign_proposition(osv.osv):
    _name = "dm.campaign.proposition"
    _inherits = {'account.analytic.account': 'analytic_account_id'}

    def write(self, cr, uid, ids, vals, context=None):
        res = super(dm_campaign_proposition,self).write(cr, uid, ids, vals, context)
        camp = self.pool.get('dm.campaign.proposition').browse(cr,uid,ids)[0]
        c = camp.camp_id.id
        id = self.pool.get('dm.campaign').browse(cr, uid, c)
        if not camp.date_start:
            super(osv.osv, self).write(cr, uid, camp.id, {'date_start':id.date_start})
        return res

    def create(self,cr,uid,vals,context={}):
        id = self.pool.get('dm.campaign').browse(cr, uid, vals['camp_id'])
        if not vals['date_start']:
            if id.date_start:
                vals['date_start']=id.date_start
        return super(dm_campaign_proposition, self).create(cr, uid, vals, context)

    def copy(self, cr, uid, id, default=None, context={}):
        """
        Function to duplicate segments only if 'keep_segments' is set to yes else not to duplicate segments
        """
        proposition_id = super(dm_campaign_proposition, self).copy(cr, uid, id, default, context=context)
        data = self.browse(cr, uid, proposition_id, context)
        default='Copy of %s' % data.name
        super(dm_campaign_proposition, self).write(cr, uid, proposition_id, {'name':default, 'date_start':0, 'initial_proposition_id':id})
        if data.keep_segments == False:
            l = []
            for i in data.segment_ids:
                 l.append(i.id)
                 self.pool.get('dm.campaign.proposition.segment').unlink(cr,uid,l)
                 super(dm_campaign_proposition, self).write(cr, uid, proposition_id, {'segment_ids':[(6,0,[])]})
            return proposition_id
        """
        Function to duplicate segments only if 'keep_prices' is set to yes else not to duplicate products
        """
        if data.keep_prices == False:
            l = []
            for i in data.product_ids:
                 l.append(i.id)
                 self.pool.get('dm.product').unlink(cr,uid,l)
                 super(dm_campaign_proposition, self).write(cr, uid, proposition_id, {'product_ids':[(6,0,[])]})
            return proposition_id
        return proposition_id

    def _proposition_code(self, cr, uid, ids, name, args, context={}):
        result ={}
        for id in ids:
            pro = self.browse(cr,uid,[id])[0]
            camp_code = pro.camp_id.code1 or ''
            offer_code = pro.camp_id.offer_id and pro.camp_id.offer_id.code or ''
            trademark_code = pro.camp_id.trademark_id and pro.camp_id.trademark_id.name or ''
            dealer_code =pro.camp_id.dealer_id and pro.camp_id.dealer_id.ref or ''
            date_start = pro.date_start or ''
            date = date_start.split('-')
            year = month = ''
            if len(date)==3:
                year = date[0][2:]
                month = date[1]
            country_code = pro.camp_id.country_id.code or ''
            seq = '%%0%sd' % 2 % id
            final_date = month+year
            code1='-'.join([camp_code, seq])
            result[id]=code1
        return result

    def _quantity_wanted_get(self, cr, uid, ids, name, args, context={}):
        result ={}
        for propo in self.browse(cr,uid,ids):
            if not propo.segment_ids:
                result[propo.id]='No segments defined'
                continue
            qty = 0
            numeric=True
            for segment in propo.segment_ids:
                if segment.AAA:
                    result[propo.id]='AAA for a Segment'
                    numeric=False
                    continue
                if not segment.quantity_wanted:
                    result[propo.id]='Wanted Quantity missing in a Segment'
                    numeric=False
                    continue
                qty += segment.quantity_wanted
            if numeric:
                result[propo.id]=str(qty)
        return result

    def _quantity_theorical_get(self, cr, uid, ids, name, args, context={}):
        result ={}
        for propo in self.browse(cr,uid,ids):
            if not propo.segment_ids:
                result[propo.id]='No segments defined'
                continue
            qty = 0
            for segment in propo.segment_ids:
                if segment.quantity_theorical == 0:
                    result[propo.id]='Theorical Quantity missing in a Segment'
                    continue
                qty += segment.quantity_theorical
            result[propo.id]=str(qty)
        return result

    def _quantity_delivered_get(self, cr, uid, ids, name, args, context={}):
        result ={}
        for propo in self.browse(cr,uid,ids):
            if not propo.segment_ids:
                result[propo.id]='No segments defined'
                continue
            qty = 0
            for segment in propo.segment_ids:
                if segment.quantity_delivered == 0:
                    result[propo.id]='Delivered Quantity missing in a Segment'
                    continue
                qty += segment.quantity_delivered
            result[propo.id]=str(qty)
        return result

    def _quantity_real_get(self, cr, uid, ids, name, args, context={}):
        result={}
        for propo in self.browse(cr,uid,ids):
            if not propo.segment_ids:
                result[propo.id]='No segments defined'
                continue
            qty = 0
            for segment in propo.segment_ids:
                if segment.quantity_real == 0:
                    result[propo.id]='Real Quantity missing in a Segment'
                    continue
                qty += segment.quantity_real
            result[propo.id]=str(qty)
        return result


    def _default_camp_date(self, cr, uid, context={}):
        if 'date1' in context and context['date1']:
            dd = context['date1']
            return dd
        return []

    _columns = {
        'code1' : fields.function(_proposition_code,string='Code',type="char",size="64",method=True,readonly=True),
        'camp_id' : fields.many2one('dm.campaign','Campaign',ondelete = 'cascade',required=True),
        'delay_ids' : fields.one2many('dm.campaign.delay', 'proposition_id', 'Delays', ondelete='cascade'),
        'sale_rate' : fields.float('Sale Rate (%)', digits=(16,2),
                    help='This is the estimated sale rate (in percent) for this commercial proposition'),
        'proposition_type' : fields.selection([('init','Initial'),('relaunching','Relauching'),('split','Split')],"Type"),
        'initial_proposition_id': fields.many2one('dm.campaign.proposition', 'Initial proposition', readonly=True),
        'segment_ids' : fields.one2many('dm.campaign.proposition.segment','proposition_id','Segment', ondelete='cascade'),
        'quantity_theorical' : fields.function(_quantity_theorical_get,string='Theorical Quantity',type="char",size="64",method=True,readonly=True,
                    help='The theorical quantity is an estimation of the real quantity of addresses you  will get after delivery, deduplication and cleaning\n' \
                            'This is usually the quantity used to order the manufacturing of the mailings'),
        'quantity_wanted' : fields.function(_quantity_wanted_get,string='Wanted Quantity',type="char",size="64",method=True,readonly=True,
                    help='The wanted quantity is the number of addresses you wish to get for that segment.\n' \
                            'This is usually the quantity used to order customers files\n' \
                            'The wanted quantity could be AAA for All Addresses Available'),
        'quantity_delivered' : fields.function(_quantity_delivered_get,string='Delivered Quantity',type="char",size="64",method=True,readonly=True,
                    help='The delivered quantity is the number of addresses you receive from the broker.'),
        'quantity_real' : fields.function(_quantity_real_get,string='Real Quantity',type="char",size="64",method=True,readonly=True,
                    help='The real quantity is the number of addresses you have after delivery, deduplication and cleaning.'),
        'starting_mail_price' : fields.float('Starting Mail Price',digits=(16,2)),
        'customer_pricelist_id':fields.many2one('product.pricelist','Items Pricelist', required=False),
        'forwarding_charges' : fields.float('Forwarding Charges', digits=(16,2)),
        'notes':fields.text('Notes'),
        'analytic_account_id' : fields.many2one('account.analytic.account','Analytic Account', ondelete='cascade'),
        'product_ids' : fields.one2many('dm.product', 'proposition_id', 'Catalogue'),
#        'product_ids' : fields.many2many('dm.product', 'proposition_product_rel', 'proposition_id', 'product_id', 'Catalogue'),
        'payment_methods' : fields.many2many('account.journal','campaign_payment_method_rel','proposition_id','journal_id','Payment Methods',domain=[('type','=','cash')]),
        'keep_segments' : fields.boolean('Keep Segments'),
        'keep_prices' : fields.boolean('Keep Prices At Duplication'),
        'force_sm_price' : fields.boolean('Force Starting Mail Price'),
        'sm_price' : fields.float('Starting Mail Price', digits=(16,2)),
#        'prices_prog_id' : fields.many2one('dm.campaign.proposition.prices_progression', 'Prices Progression'),
        'manufacturing_costs': fields.float('Manufacturing Costs',digits=(16,2)),
    }

    _defaults = {
        'proposition_type' : lambda *a : 'init',
        'date_start' : _default_camp_date,
        'keep_segments' : lambda *a : True,
        'keep_prices' : lambda *a : True
    }

    def _check(self, cr, uid, ids=False, context={}):
        '''
        Function called by the scheduler to create workitem from the segments of propositions.
        '''
        ids = self.search(cr,uid,[('date_start','=',time.strftime('%Y-%m-%d %H:%M:%S'))])
        for id in ids:
            res = self.browse(cr,uid,[id])[0]
            offer_step_id = self.pool.get('dm.offer.step').search(cr,uid,[('offer_id','=',res.camp_id.offer_id.id),('flow_start','=',True)])
            if offer_step_id :
                for segment in res.segment_ids:
                    vals = {'step_id':offer_step_id[0],'segment_id':segment.id}
                    new_id = self.pool.get('dm.offer.step.workitem').create(cr,uid,vals)
        return True

dm_campaign_proposition()

class dm_campaign_proposition_segment(osv.osv):

    _name = "dm.campaign.proposition.segment"
    _inherits = {'account.analytic.account': 'analytic_account_id'}
    _description = "Segment"

    def _quantity_real_get(self, cr, uid, ids, name, args, context={}):
        result ={}
        for segment in self.browse(cr,uid,ids):
            result[segment.id]=segment.quantity_delivered - segment.quantity_dedup - segment.quantity_cleaned
        return result

    def write(self, cr, uid, ids, vals, context=None):
        list_name = self.pool.get('dm.customers_list').browse(cr, uid, vals['list_id'])
        segs = self.browse(cr, uid, ids)[0]
        if 'start_census' in vals and vals['start_census']:
            start_census = vals['start_census']
        else:
            start_census = segs.start_census
        if 'end_census' in vals and vals['end_census']:
            end_census = vals['end_census']
        else:
            end_census = segs.end_census
        vals['name'] = list_name.name + '-' + str(start_census) + '/' + str(end_census)
        return super(dm_campaign_proposition_segment,self).write(cr, uid, ids, vals, context)

    def create(self,cr,uid,vals,context={}):
        list_name = self.pool.get('dm.customers_list').browse(cr, uid, vals['list_id'])
        vals['name'] = list_name.name + '-' + str(vals['start_census']) + '/' + str(vals['end_census'])
        return super(dm_campaign_proposition_segment, self).create(cr, uid, vals, context)

    def _segment_code(self, cr, uid, ids, name, args, context={}):
        result ={}
        for id in ids:
            seg = self.browse(cr,uid,[id])[0]
            country_code = seg.proposition_id.camp_id.country_id.code or ''
            if seg.list_id:
                cust_file_code =  seg.list_id.code
                seq = '%%0%sd' % 2 % id
                code1='-'.join([country_code[:3], cust_file_code[:3], seq[:4]])
            else:
                code1='No File Defined'
            result[id]=code1
        return result

    _columns = {
        'code1' : fields.function(_segment_code,string='Code',type="char",size="64",method=True,readonly=True),
        'proposition_id' : fields.many2one('dm.campaign.proposition','Proposition', ondelete='cascade'),
        'list_id': fields.many2one('dm.customers_list','Customers List',required=True),
        'quantity_theorical' : fields.integer('Theorical Quantity'),
        'quantity_wanted' : fields.integer('Wanted Quantity'),
        'quantity_delivered' : fields.integer('Delivered Quantity'),
        'quantity_dedup' : fields.integer('Deduplication Quantity'),
        'quantity_cleaned' : fields.integer('Cleaned Quantity'),
        'quantity_real' : fields.function(_quantity_real_get,string='Real Quantity',type="integer",method=True,readonly=True),
        'AAA': fields.boolean('All Adresses Available'),
        'split_id' : fields.many2one('dm.campaign.proposition.segment','Split'),
        'start_census' :fields.integer('Start Census (days)'),
        'end_census' : fields.integer('End Census (days)'),
        'deduplication_level' : fields.integer('Deduplication Level'),
        'active' : fields.boolean('Active'),
        'reuse_id' : fields.many2one('dm.campaign.proposition.segment','Reuse'),
        'analytic_account_id' : fields.many2one('account.analytic.account','Analytic Account', ondelete='cascade'),
        'note' : fields.text('Notes'),
        'segmentation_criteria': fields.text('Segmentation Criteria'),
        'price_per_thousand' : fields.integer('Price per 1000'),
    }
    _order = 'deduplication_level'

dm_campaign_proposition_segment()

class dm_campaign_delay(osv.osv):
    _name = "dm.campaign.delay"
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'value' : fields.integer('Value'),
        'proposition_id' : fields.many2one('dm.campaign.proposition', 'Proposition')
    }

dm_campaign_delay()


PURCHASE_LINE_TRIGGERS = [
    ('draft','At Draft'),
    ('open','At Open'),
    ('planned','At Planning'),
    ('close','At Close'),
    ('manual','Manual'),
]

PURCHASE_LINE_STATES = [
    ('pending','Pending'),
    ('requested','Quotations Requested'),
    ('ordered','Ordered'),
    ('delivered','Delivered'),
]

PURCHASE_LINE_TYPES = [
    ('manufacturing','Manufacturing'),
    ('items','Items'),
    ('customer_file','Customer Files'),
    ('translation','Translation'),
    ('dtp','DTP'),
]

QTY_TYPES = [
    ('quantity_theorical','Theorical Quantity'),
    ('quantity_wanted','Wanted Quantity'),
    ('quantity_delivered','Delivered Quantity'),
    ('quantity_real','Real Quantity'),
    ('quantity_free','Free Quantity'),
]

DOC_TYPES = [
    ('po','Purchase Order'),
    ('rfq','Request For Quotation'),
]

class dm_campaign_purchase_line(osv.osv):
    _name = 'dm.campaign.purchase_line'
    _rec_name = 'product_id'

    def onchange_product(self, cr, uid, ids, product_id):
        value = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr,uid,[product_id])[0]
            if product.categ_id.name not in ['Mailing Manufacturing','Customers List','DTP','Item','Translation']:
                raise  osv.except_osv('Warning', 'The category of that product is not valid for a purchase line creation\n' \
                                            'Product category should be :\n' \
                                                '* Mailing Manufacturing\n' \
                                                '* Customers List\n' \
                                                '* Item\n' \
                                                '* DTP\n' \
                                                '* Translation\n' \
                                                )
            else:
                value['type_product'] = product.categ_id.name
        else:
            value['type_product'] = 'No Product Defined'
        return {'value':value}

    def _get_uom_id(self, cr, uid, *args):
        cr.execute('select id from product_uom order by id limit 1')
        res = cr.fetchone()
        return res and res[0] or False

    def quantity_get(self,cr, uid, ids, *args):
        value = {}
        quantity = 0

        pline = self.browse(cr, uid, ids)[0]
        if not pline.campaign_id:
            raise  osv.except_osv('Warning', "You must first save this Purchase Line and the campaign before using this button")

        if pline.type_quantity == 'quantity_free':
            quantity = 0
        elif pline.type_quantity == 'quantity_theorical':
            if pline.campaign_id.quantity_theorical_total.isdigit():
                quantity = pline.campaign_id.quantity_theorical_total
            else : 
                raise osv.except_osv('Warning',
                    'Cannot get wanted quantity, check prososition segments')
        elif pline.type_quantity == 'quantity_wanted':
            if pline.campaign_id.quantity_wanted_total.isdigit():
                quantity = pline.campaign_id.quantity_wanted_total
            elif pline.campaign_id.quantity_wanted_total == 'AAA for a Segment':
                quantity = 0
            else :
                raise osv.except_osv('Warning',
                    "Cannot get wanted quantity, check prososition segments")
        elif pline.type_quantity == 'quantity_delivered':
            if pline.campaign_id.quantity_delivered_total.isdigit():
                quantity = pline.campaign_id.quantity_delivered_total
            else : 
                raise osv.except_osv('Warning',
                    "Cannot get delivered quantity, check prososition segments")
        elif pline.type_quantity == 'quantity_real':
            if pline.campaign_id.quantity_real_total.isdigit():
                quantity = pline.campaign_id.quantity_real_total
            else : 
                raise osv.except_osv('Warning',
                    "Cannot get real quantity, check prososition segments")
        else:
            raise osv.except_osv('Warning','Error getting quantity')

        pline.write({'quantity':quantity})

        return True


    def po_generate(self,cr, uid, ids, *args):
        plines = self.browse(cr, uid ,ids)
        if not plines:
            raise  osv.except_osv('Warning', "There's no purchase lines defined for this campaign")
        for pline in plines:
            if pline.state == 'pending':

                if not pline.quantity and pline.type_quantity != 'quantity_free' and pline.type_quantity != 'quantity_wanted':
                    raise  osv.except_osv('Warning', "There's no quantity defined for this purchase line")

                if not pline.product_id.seller_ids:
                    raise  osv.except_osv('Warning', "There's no supplier defined for this product : %s" % (pline.product_id.name,) )

                # Create a po / supplier
                for supplier in pline.product_id.seller_ids:
                    partner_id = supplier.id
                    partner = supplier.name

                    address_id = self.pool.get('res.partner').address_get(cr, uid, [partner.id], ['default'])['default']
                    if not address_id:
                        raise osv.except_osv('Warning', "There's no default address defined for this partner : %s" % (partner.name,) )
                    pricelist_id = partner.property_product_pricelist_purchase.id
                    if not pricelist_id:
                        raise osv.except_osv('Warning', "There's no purchase pricelist defined for this partner : %s" % (partner.name,) )
                    price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id], pline.product_id.id, pline.quantity, False, {'uom': pline.uom_id.id})[pricelist_id]
                    newdate = DateTime.strptime(pline.date_planned, '%Y-%m-%d %H:%M:%S') - DateTime.RelativeDateTime(days=pline.product_id.product_tmpl_id.seller_delay or 0.0)

                    if not pline.campaign_id.offer_id:
                        raise osv.except_osv('Warning', "There's no offer defined for this campaign : %s" % (pline.campaign_id.name,) )
                    if not pline.campaign_id.proposition_ids:
                        raise osv.except_osv('Warning', "There's no proposition defined for this campaign : %s" % (pline.campaign_id.name,) )

                    # Get constraints
                    constraints = []
                    if pline.type_product == 'Mailing Manufacturing':
                        for step in pline.campaign_id.offer_id.step_ids:
                            for const in step.manufacturing_constraint_ids:
                                if not const.country_ids:
                                    constraints.append("---------------------------------------------------------------------------")
                                    constraints.append(const.name)
                                    constraints.append(const.constraint)
                                elif pline.campaign_id.country_id in const.country_ids:
                                    constraints.append("---------------------------------------------------------------------------")
                                    constraints.append(const.name + ' for country :' +  pline.campaign_id.country_id.name)
                                    constraints.append(const.constraint)
                            if pline.notes:
                                constraints.append("---------------------------------------------------------------------------")
                                constraints.append(pline.notes)
                            else:
                                constraints.append(' ')
                    elif pline.type_product == 'Item':
                        raise osv.except_osv('Warning', "Purchase of items is not yet implemented")
                        for step in pline.campaign_id.offer_id.step_ids:
                            for item in step.product_ids:
                                constraints.append("---------------------------------------------------------------------------")
                                constraints.append(item.product_id.name)
                                constraints.append(item.purchase_constraints)
                    elif pline.type_product == 'Customers List':
                        raise osv.except_osv('Warning', "Purchase of customers files is not yet implemented")
                    elif pline.type == 'Translation':
                        if not pline.campaign_id.lang_id:
                            raise osv.except_osv('Warning', "There's no language defined for this campaign : %s" % (pline.campaign_id.name,) )
                        if pline.notes:
                            constraints.append(pline.notes)
                        else:
                            constraints.append(' ')
                    elif pline.type_product == False:
                        if pline.notes:
                            constraints.append(pline.notes)
                        else:
                            constraints.append(' ')

                    # Create po
                    purchase_id = self.pool.get('purchase.order').create(cr, uid, {
                        'origin': pline.campaign_id.code1,
                        'partner_id': partner.id,
                        'partner_address_id': address_id,
                        'location_id': 1,
                        'pricelist_id': pricelist_id,
                        'notes': "\n".join(constraints),
                        'dm_campaign_purchase_line': pline.id
                    })

                    ''' If Translation Order => Get Number of documents in Offer '''
                    if pline.type_product == 'Translation':
                        line = self.pool.get('purchase.order.line').create(cr, uid, {
                           'order_id': purchase_id,
                           'name': pline.campaign_id.code1,
                           'product_qty': pline.quantity,
                           'product_id': pline.product_id.id,
                           'product_uom': pline.uom_id.id,
                           'price_unit': price,
                           'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                           'taxes_id': [(6, 0, [x.id for x in pline.product_id.product_tmpl_id.supplier_taxes_id])],
                           'account_analytic_id': pline.campaign_id.analytic_account_id,
                        })
                    elif pline.type_product == 'Mailing Manufacturing':
                        ''' Create po lines for each proposition'''
                        lines = []
                        for propo in pline.campaign_id.proposition_ids:
                            line_name = propo.code1 + '-' + propo.type

                            if pline.type_quantity == 'quantity_free':
                                line_quantity = pline.quantity
                            elif pline.type_quantity == 'quantity_theorical':
                                if propo.quantity_theorical.isdigit():
                                    quantity = propo.quantity_theorical
                                else : 
                                    raise osv.except_osv('Warning',
                                        'Cannot get theorical quantity, check prososition %s' % (propo.name,)) 
                            elif pline.type_quantity == 'quantity_wanted':
                                if propo.quantity_wanted.isdigit():
                                    quantity = propo.quantity_wanted
                                elif propo.quantity_wanted == 'AAA for a Segment':
                                    quantity = 0
                                    line_name = propo.code1 + '-' + propo.type + '-AAA (All Addresses Available)'
                                else :
                                    raise osv.except_osv('Warning',
                                        'Cannot get wanted quantity, check prososition %s' % (propo.name,)) 
                            elif pline.type_quantity == 'quantity_delivered':
                                if propo.quantity_delivered.isdigit():
                                    quantity = propo.quantity_delivered
                                else : 
                                    raise osv.except_osv('Warning',
                                        'Cannot get delivered quantity, check prososition %s' % (propo.name,)) 
                            elif pline.type_quantity == 'quantity_real':
                                if propo.quantity_real.isdigit():
                                    quantity = propo.quantity_real
                                else : 
                                    raise osv.except_osv('Warning',
                                        'Cannot get delivered quantity, check prososition %s' % (propo.name,)) 
                            else:
                                raise osv.except_osv('Warning','Error getting quantity for proposition %s' % (propo.name,))

                            line = self.pool.get('purchase.order.line').create(cr, uid, {
                               'order_id': purchase_id,
                               'name': line_name,
                               'product_qty': quantity,
                               'product_id': pline.product_id.id,
                               'product_uom': pline.uom_id.id,
                               'price_unit': price,
                               'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                               'taxes_id': [(6, 0, [x.id for x in pline.product_id.product_tmpl_id.supplier_taxes_id])],
                               'account_analytic_id': propo.analytic_account_id,
                            })

                    if pline.type_document == 'po':
                        print "Set as Purchase Order"

                    '''
                    # Set campaign supervision states
                    if pline.type == 'translation':
                        pline.campaign_id.write({'translation_state':'inprogress'})
                    elif pline.type == 'manufacturing':
                        pline.campaign_id.write({'manufacturing_state':'inprogress'})
                    elif pline.type == 'items':
                        pline.campaign_id.write({'items_state':'inprogress'})
                    elif pline.type == 'customer_file':
                        pline.campaign_id.write({'customer_file_state':'inprogress'})
                    '''

        return True

    def _default_date(self, cr, uid, context={}):
        if 'date1' in context and context['date1']:
            dd = context['date1']
            newdate =  DateTime.strptime(dd + ' 09:00:00','%Y-%m-%d %H:%M:%S')
            #print "From _default_date : ",newdate.strftime('%Y-%m-%d %H:%M:%S')
            return newdate.strftime('%Y-%m-%d %H:%M:%S')
        return []


    def _state_get(self, cr, uid, ids, name, args, context={}):
        result = {}
        for pline in self.browse(cr, uid, ids):
            delivered=False
            ordered=False
            if pline.purchase_order_ids:
                for po in pline.purchase_order_ids:
                    if delivered:
                        continue
                    if po.shipped:
                        result[pline.id]='delivered'
                        delivered=True
                        if pline.type == 'translation':
                            trans_id = self.pool.get('dm.offer.translation').create(cr, uid,
                                {'offer_id': pline.campaign_id.offer_id.id,
                                 'date': pline.date_delivery,
                                 'language_id': pline.campaign_id.lang_id.id,
                                 'translator_id':  po.partner_id.id,
                                 'notes': pline.notes,
                                 })
                        continue
                    if ordered:
                        continue
                    if po.state == 'confirmed' or po.state == 'approved':
                        result[pline.id]='ordered'
                        ordered=True
                    if po.state == 'draft':
                        result[pline.id]='requested'
            else:
                result[pline.id] = 'pending'
        return result

    def _delivery_date_get(self, cr, uid, ids, name, args, context={}):
        result = {}
        for pline in self.browse(cr, uid, ids):
            result[pline.id] = False
            for po in pline.purchase_order_ids:
                if po.shipped:
                    result[pline.id] = po.picking_ids[0].date_done
                    continue
        return result

    _columns = {
        'campaign_id': fields.many2one('dm.campaign', 'Campaign'),
        'product_id' : fields.many2one('product.product', 'Product', required=True, context={'flag':True}),
        'quantity' : fields.integer('Quantity', readonly=False, required=True),
        'type_quantity' : fields.selection(QTY_TYPES, 'Quantity Type', size=32),
        'type_document' : fields.selection(DOC_TYPES, 'Document Generated', size=32),
        'type_product' : fields.char('Product Type',size=64, readonly=True),
        'uom_id' : fields.many2one('product.uom','UOM', required=True),
        'date_order': fields.datetime('Order date', readonly=True),
        'date_planned': fields.datetime('Scheduled date', required=True),
        'date_delivery': fields.function(_delivery_date_get, method=True, type='datetime', string='Delivery Date', readonly=True),
        'trigger' : fields.selection(PURCHASE_LINE_TRIGGERS, 'Trigger'),
        'type' : fields.selection(PURCHASE_LINE_TYPES, 'Type'),
        'purchase_order_ids' : fields.one2many('purchase.order','dm_campaign_purchase_line','DM Campaign Purchase Line'),
        'notes': fields.text('Notes'),
        'state' : fields.function(_state_get, method=True, type='selection', selection=[
            ('pending','Pending'),
            ('requested','Quotations Requested'),
            ('ordered','Ordered'),
            ('delivered','Delivered'),
            ], string='State', store=True, readonly=True),
    }

    _defaults = {
#        'date_planned' : _default_date,
        'quantity' : lambda *a : 0,
        'uom_id' : _get_uom_id,
        'trigger': lambda *a : 'manual',
        'state': lambda *a : 'pending',
        'type_quantity': lambda *a : 'quantity_wanted',
        'type_document': lambda *a : 'rfq',
    }
dm_campaign_purchase_line()

class dm_campaign_manufacturing_cost(osv.osv):
    _name = 'dm.campaign.manufacturing_cost'
    _columns = {
        'name' : fields.char('Description', size=64, required=True),
        'amount': fields.float('Amount', digits=(16,2)),
        'campaign_id' : fields.many2one('dm.campaign','Campaign'),
    }
dm_campaign_manufacturing_cost()

class dm_campaign_proposition_prices_progression(osv.osv):
    _name = 'dm.campaign.proposition.prices_progression'
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'fixed_prog' : fields.float('Fixed Prices Progression', digits=(16,2)),
        'percent_prog' : fields.float('Percentage Prices Progression', digits=(16,2)),
    }
dm_campaign_proposition_prices_progression()


class Country(osv.osv):
    _name = 'res.country'
    _inherit = 'res.country'
    _columns = {
                'main_language' : fields.many2one('res.lang','Main Language',ondelete='cascade',),
                'main_currency' : fields.many2one('res.currency','Main Currency',ondelete='cascade'),
    }
Country()

class res_partner(osv.osv):
    _name = "res.partner"
    _inherit="res.partner"
    _columns = {
        'country_ids' : fields.many2many('res.country', 'partner_country_rel', 'partner_id', 'country_id', 'Allowed Countries'),
        'state_ids' : fields.many2many('res.country.state','partner_state_rel', 'partner_id', 'state_id', 'Allowed States'),
    }
    def _default_category(self, cr, uid, context={}):
        if 'category' in context and context['category']:
            id_cat = self.pool.get('res.partner.category').search(cr,uid,[('name','ilike',context['category'])])[0]
            return [id_cat]
        return []

    def _default_all_country(self, cr, uid, context={}):
        id_country = self.pool.get('res.country').search(cr,uid,[])
        return id_country
    
    def _default_all_state(self, cr, uid, context={}):
        id_state = self.pool.get('res.country.state').search(cr,uid,[])
        return id_state
    
    _defaults = {
        'category_id': _default_category,
        'country_ids': _default_all_country,
        'state_ids': _default_all_state,
    }
res_partner()

class purchase_order(osv.osv):
    _name = 'purchase.order'
    _inherit = 'purchase.order'
    _columns = {
        'dm_campaign_purchase_line' : fields.many2one('dm.campaign.purchase_line','DM Campaign Purchase Line'),
    }
purchase_order()

class project_task(osv.osv):
    _name = "project.task"
    _inherit = "project.task"

    def _default_type(self, cr, uid, context={}):
        if 'type' in context and context['type']:
            id_cat = self.pool.get('project.task.type').search(cr,uid,[('name','ilike',context['type'])])[0]
            return [id_cat]
        return []

    _columns = {
        'date_reviewed': fields.datetime('Reviewed Date'),
        'date_planned': fields.datetime('Planned Date'),
     }
    _defaults = {
        'type': _default_type,
    }
project_task()

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
