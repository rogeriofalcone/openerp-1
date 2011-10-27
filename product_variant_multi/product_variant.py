# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Copyright (C) 2010-2011 Akretion (www.akretion.com). All Rights Reserved
#    @author Sebatien Beau <sebastien.beau@akretion.com>
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#       update to use a single "Generate/Update" button & price computation code
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

from osv import fields, osv
import decimal_precision as dp
import netsvc
# Lib to eval python code with security
from tools.safe_eval import safe_eval
from tools.translate import _

#
# Dimensions Definition
#
class product_variant_dimension_type(osv.osv):
    _name = "product.variant.dimension.type"
    _description = "Dimension Type"

    _columns = {
        'description': fields.char('Description', size=64, translate=True),
        'name' : fields.char('Dimension', size=64, required=True),
        'sequence' : fields.integer('Sequence', help="The product 'variants' code will use this to order the dimension values"),
        'option_ids' : fields.one2many('product.variant.dimension.option', 'dimension_id', 'Dimension Option'),
        'product_tmpl_id': fields.many2many('product.template', 'product_template_dimension_rel', 'dimension_id', 'template_id', 'Product Template'),
        'allow_custom_value': fields.boolean('Allow Custom Value', help="If true, custom values can be entered in the product configurator"),
        'mandatory_dimension': fields.boolean('Mandatory Dimension', help="If false, variant products will be created with and without this dimension"),
    }

    _defaults = {
        'mandatory_dimension': lambda *a: 1,
        }
    
    _order = "sequence, name"

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=None):
        if context.get('product_tmpl_id', False):
            return super(product_variant_dimension_type, self).name_search(cr, user, '', args, 'ilike', None, None)
        else:
            return super(product_variant_dimension_type, self).name_search(cr, user, '', None, 'ilike', None, None)

product_variant_dimension_type()

class product_variant_dimension_option(osv.osv):
    _name = "product.variant.dimension.option"
    _description = "Dimension Option"

    def _get_dimension_values(self, cr, uid, ids, context={}):
        return self.pool.get('product.variant.dimension.value').search(cr, uid, [('dimension_id', 'in', ids)], context=context)

    _columns = {
        'name' : fields.char('Dimension Value', size=64, required=True),
        'sequence' : fields.integer('Sequence'),
        'dimension_id' : fields.many2one('product.variant.dimension.type', 'Dimension Type', ondelete='cascade'),
    }

    _order = "dimension_id, sequence, name"

product_variant_dimension_option()


class product_variant_dimension_value(osv.osv):
    _name = "product.variant.dimension.value"
    _description = "Dimension Value"

    def unlink(self, cr, uid, ids, context=None):
        for value in self.browse(cr, uid, ids, context=context):
            if value.product_ids:
                product_list = '\n    - ' + '\n    - '.join([product.name for product in value.product_ids])
                raise osv.except_osv(_('Dimension value can not be removed'), _("The value %s is use in the product : %s \n Please remove this products before removing the value"%(value.option_id.name, product_list)))
        return super(product_variant_dimension_value, self).unlink(cr, uid, ids, context)

    def _get_dimension_values(self, cr, uid, ids, context={}):
        return self.pool.get('product.variant.dimension.value').search(cr, uid, [('dimension_id', 'in', ids)], context=context)

    _columns = {
        'option_id' : fields.many2one('product.variant.dimension.option', 'Option', required=True),
        'sequence' : fields.integer('Sequence'),
        'price_extra' : fields.float('Sale Price Extra', digits_compute=dp.get_precision('Sale Price')),
        'price_margin' : fields.float('Sale Price Margin', digits_compute=dp.get_precision('Sale Price')),
        'cost_price_extra' : fields.float('Cost Price Extra', digits_compute=dp.get_precision('Purchase Price')),
        'dimension_id' : fields.related('option_id', 'dimension_id', type="many2one", relation="product.variant.dimension.type", string="Dimension Type", store=True),
        'product_tmpl_id': fields.many2one('product.template', 'Product Template', ondelete='cascade'),
        'dimension_sequence': fields.related('dimension_id', 'sequence', string="Related Dimension Sequence",#used for ordering purposes in the "variants"
             store={
                'product.variant.dimension.type': (_get_dimension_values, ['sequence'], 10),
            }),
        'product_ids': fields.many2many('product.product', 'product_product_dimension_rel', 'dimension_id', 'product_id', 'Variant', readonly=True),
        'active' : fields.boolean('Active?', help="If false, this value will be not use anymore for generating variant"),
    }

    _defaults = {
        'active': lambda *a: 1,
        }

    _order = "dimension_sequence, sequence, option_id"
    
product_variant_dimension_value()

class product_variant_osv(osv.osv):
    _register = False # Set to false if the model shouldn't be automatically discovered.
    _duplicated_fields = ['name']

    def get_vals_to_write(self, vals):
        vals_to_write = {}
        for field in self._duplicated_fields:
            if field in vals.keys():
                vals_to_write[field] = vals[field]
        return vals_to_write


class product_template(product_variant_osv):
    _inherit = "product.template"

    _columns = {
        'dimension_type_ids':fields.many2many('product.variant.dimension.type', 'product_template_dimension_rel', 'template_id', 'dimension_id', 'Dimension Types'),
        'value_ids': fields.one2many('product.variant.dimension.value', 'product_tmpl_id', 'Dimension Values'),
        'variant_ids':fields.one2many('product.product', 'product_tmpl_id', 'Variants'),
        'variant_model_name':fields.char('Variant Model Name', size=64, required=True, help='[NAME] will be replaced by the name of the dimension and [VALUE] by is value. Example of Variant Model Name : "[NAME] - [VALUE]"'),
        'variant_model_name_separator':fields.char('Variant Model Name Separator', size=64, help= 'Add a separator between the elements of the variant name'),
        'code_generator' : fields.char('Code Generator', size=64, help='enter the model for the product code, all parameter between [_o.my_field_] will be replace by the product field. Example product_code model : prefix_[_o.variants_]_suffixe ==> result : prefix_2S2T_suffix'),
        'is_multi_variants' : fields.boolean('Is Multi Variants?'),
        'variant_track_production' : fields.boolean('Track Production Lots on variants ?'),
        'variant_track_incoming' : fields.boolean('Track Incoming Lots on variants ?'),
        'variant_track_outgoing' : fields.boolean('Track Outgoing Lots on variants ?'),
    }
    
    _defaults = {
        'variant_model_name': lambda *a: '[NAME] - [VALUE]',
        'variant_model_name_separator': lambda *a: ' - ',
        'is_multi_variants' : lambda *a: False,
                }

    def unlink(self, cr, uid, ids, context=None):
        if context and context.get('unlink_from_product_product', False):
            for template in self.browse(cr, uid, ids, context):
                if not template.is_multi_variants:
                    super(product_template, self).unlink(cr, uid, [template.id], context)
        return True

    def write(self, cr, uid, ids, vals, context=None):
        # When your write the name on a simple product from the menu product template you have to update the name on the product product
        # Two solution was posible overwritting the write function or overwritting the read function
        # I choose to overwrite the write function because read is call more often than the write function
        if isinstance(ids, (int, long)):
            ids = [ids]
        if context is None:
            context = {}

        res = super(product_template, self).write(cr, uid, ids, vals.copy(), context=context)

        if not context.get('iamthechild', False):
            obj_product = self.pool.get('product.product')
            if vals.get('is_multi_variants', 'wrong') != 'wrong':
                if vals['is_multi_variants']:
                    prod_tmpl_ids_simple = False
                else:
                    prod_tmpl_ids_simple = ids
            else:            
                prod_tmpl_ids_simple = self.search(cr, uid, [['id', 'in', ids], ['is_multi_variants', '=', False]], context=context)
            
            if prod_tmpl_ids_simple:
                #NB in the case that the user have just unchecked the option 'is_multi_variants' without changing any field the vals_to_write is empty
                vals_to_write = obj_product.get_vals_to_write(vals)
                if vals_to_write:
                    ctx = context.copy()
                    ctx['iamthechild'] = True
                    product_ids = obj_product.search(cr, uid, [['product_tmpl_id', 'in', prod_tmpl_ids_simple]])
                    obj_product.write(cr, uid, product_ids, vals_to_write, context=ctx)
        return res

    def add_all_option(self, cr, uid, ids, context=None):
        #Reactive all unactive values
        value_obj = self.pool.get('product.variant.dimension.value')
        for template in self.browse(cr, uid, ids, context=context):
            values_ids = value_obj.search(cr, uid, [['product_tmpl_id','=', template.id], '|', ['active', '=', False], ['active', '=', True]], context=context)
            value_obj.write(cr, uid, values_ids, {'active':True}, context=context)
            existing_option_ids = [value.option_id.id for value in value_obj.browse(cr, uid, values_ids,context=context)]
            vals = {'value_ids' : []}
            for dim in template.dimension_type_ids:
                for option in dim.option_ids:
                    if not option.id in existing_option_ids:
                        vals['value_ids'] += [[0, 0, {'option_id': option.id}]]
            self.write(cr, uid, template.id, vals, context=context)    
        return True

    def get_products_from_product_template(self, cr, uid, ids, context={}):
        product_tmpl = self.read(cr, uid, ids, ['variant_ids'], context=context)
        return [id for vals in product_tmpl for id in vals['variant_ids']]
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'variant_ids':False,})
        return super(product_template, self).copy(cr, uid, id, default, context)

    def copy_translations(self, cr, uid, old_id, new_id, context=None):
        if context is None:
            context = {}
        # avoid recursion through already copied records in case of circular relationship
        seen_map = context.setdefault('__copy_translations_seen',{})
        if old_id in seen_map.setdefault(self._name,[]):
            return
        seen_map[self._name].append(old_id)
        return super(product_template, self).copy_translations(cr, uid, old_id, new_id, context=context)

    def _create_variant_list(self, cr, ids, uid, vals, context=None):
        
        def cartesian_product(args):
            if len(args) == 1: return [x and [x] or [] for x in args[0]]
            return [(i and [i] or []) + j for j in cartesian_product(args[1:]) for i in args[0]]
        
        return cartesian_product(vals)

    def button_generate_variants(self, cr, uid, ids, context=None):
        logger = netsvc.Logger()
        variants_obj = self.pool.get('product.product')
        temp_val_list=[]

        for product_temp in self.browse(cr, uid, ids, context):
            #for temp_type in product_temp.dimension_type_ids:
            #    temp_val_list.append([temp_type_value.id for temp_type_value in temp_type.value_ids] + (not temp_type.mandatory_dimension and [None] or []))
                #TODO c'est quoi ça??
                # if last dimension_type has no dimension_value, we ignore it
            #    if not temp_val_list[-1]:
            #        temp_val_list.pop()
            res = {}
            for value in product_temp.value_ids:
                if res.get(value.dimension_id, False):
                    res[value.dimension_id] += [value.id]
                else:
                    res[value.dimension_id] = [value.id]
            for dim in res:
                temp_val_list += [res[dim] + (not dim.mandatory_dimension and [None] or [])]

            if temp_val_list:
                list_of_variants = self._create_variant_list(cr, uid, ids, temp_val_list, context)
                existing_product_ids = variants_obj.search(cr, uid, [('product_tmpl_id', '=', product_temp.id)])
                existing_product_dim_value = variants_obj.read(cr, uid, existing_product_ids, ['dimension_value_ids'])
                list_of_variants_existing = [x['dimension_value_ids'] for x in existing_product_dim_value]
                for x in list_of_variants_existing:
                    x.sort()
                for x in list_of_variants:
                    x.sort()        
                list_of_variants_to_create = [x for x in list_of_variants if not x in list_of_variants_existing]
                
                logger.notifyChannel('product_variant_multi', netsvc.LOG_INFO, "variant existing : %s, variant to create : %s" % (len(list_of_variants_existing), len(list_of_variants_to_create)))
                count = 0
                for variant in list_of_variants_to_create:
                    count += 1
                    
                    vals={}
                    vals['track_production'] = product_temp.variant_track_production
                    vals['track_incoming'] = product_temp.variant_track_incoming
                    vals['track_outgoing'] = product_temp.variant_track_outgoing
                    vals['product_tmpl_id'] = product_temp.id
                    vals['dimension_value_ids'] = [(6,0,variant)]
    
                    var_id=variants_obj.create(cr, uid, vals, {'generate_from_template' : True})
                                        
                    if count%50 == 0:
                        cr.commit()
                        logger.notifyChannel('product_variant_multi', netsvc.LOG_INFO, "product created : %s" % (count,))
                logger.notifyChannel('product_variant_multi', netsvc.LOG_INFO, "product created : %s" % (count,))

        product_ids = self.get_products_from_product_template(cr, uid, ids, context=context)
        # FIRST, Generate/Update variant names ('variants' field)
        logger.notifyChannel('product_variant_multi', netsvc.LOG_INFO, "Starting to generate/update variant names...")
        self.pool.get('product.product').build_variants_name(cr, uid, product_ids, context=context)
        logger.notifyChannel('product_variant_multi', netsvc.LOG_INFO, "End of the generation/update of variant names.")
        # SECOND, Generate/Update product codes and properties (we may need variants name for that)
        logger.notifyChannel('product_variant_multi', netsvc.LOG_INFO, "Starting to generate/update product codes and properties...")
        self.pool.get('product.product').build_product_code_and_properties(cr, uid, product_ids, context=context)
        logger.notifyChannel('product_variant_multi', netsvc.LOG_INFO, "End of the generation/update of product codes and properties.")

        logger.notifyChannel('product_variant_multi_advanced', netsvc.LOG_INFO, "Starting to generate/update product names...")
        context['variants_values'] = {}
        for product in self.pool.get('product.product').read(cr, uid, product_ids, ['variants'], context=context):
            context['variants_values'][product['id']] = product['variants']
        self.pool.get('product.product').build_product_name(cr, uid, product_ids, context=context)
        logger.notifyChannel('product_variant_multi_advanced', netsvc.LOG_INFO, "End of generation/update of product names.")
        return True
        
product_template()


class product_product(product_variant_osv):
    _inherit = "product.product"

    def init(self, cr):
        #For the first installation if you already have product in your database the name of the existing product will be empty, so we fill it
        cr.execute("update product_product set name=name_template where name is null;")
        return True
  
    def unlink(self, cr, uid, ids, context=None):
        if not context:
            context={}
        context['unlink_from_product_product']=True
        return super(product_product, self).unlink(cr, uid, ids, context)

    def build_product_name(self, cr, uid, ids, context=None):
        return self.build_product_field(cr, uid, ids, 'name', context=None)

    def build_product_field(self, cr, uid, ids, field, context=None):
        def get_description_sale(product):
            return self.parse(cr, uid, product, product.product_tmpl_id.description_sale, context=context)

        def get_name(product):
            if context.get('variants_values', False):
                return (product.product_tmpl_id.name or '' )+ ' ' + (context['variants_values'][product.id] or '')
            return (product.product_tmpl_id.name or '' )+ ' ' + (product.variants or '')

        if not context:
            context={}
        context['is_multi_variants']=True
        obj_lang=self.pool.get('res.lang')
        lang_ids = obj_lang.search(cr, uid, [('translatable','=',True)], context=context)
        lang_code = [x['code'] for x in obj_lang.read(cr, uid, lang_ids, ['code'], context=context)]
        for code in lang_code:
            context['lang'] = code
            for product in self.browse(cr, uid, ids, context=context):
                new_field_value = eval("get_" + field + "(product)") # TODO convert to safe_eval
                cur_field_value = safe_eval("product." + field, {'product': product})
                if new_field_value != cur_field_value:
                    self.write(cr, uid, product.id, {field: new_field_value}, context=context)
        return True


    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        if context is None:
            context = {}
        res = super(product_product, self).write(cr, uid, ids, vals.copy(), context=context)

        ids_simple = self.search(cr, uid, [['id', 'in', ids], ['is_multi_variants', '=', False]], context=context)

        if not context.get('iamthechild', False) and ids_simple:
            vals_to_write = self.get_vals_to_write(vals)

            if vals_to_write:
                obj_tmpl = self.pool.get('product.template')
                ctx = context.copy()
                ctx['iamthechild'] = True
                tmpl_ids = obj_tmpl.search(cr, uid, [['variant_ids', 'in', ids_simple]])
                obj_tmpl.write(cr, uid, tmpl_ids, vals_to_write, context=ctx)
        return res

    def create(self, cr, uid, vals, context=None):
        #TAKE CARE for inherits objects openerp will create firstly the product_template and after the product_product
        # and so the duplicated fields (duplicated field = field which are on the template and on the variant) will be on the product_template and not on the product_product
        #Also when a product is created the duplicated field are empty for the product.product, this is why the field name can not be a required field
        #This should be fix in the orm in the futur
        ids = super(product_product, self).create(cr, uid, vals.copy(), context=context) #using vals.copy() if not the vals will be changed by calling the super method
        ####### write the value in the product_product
        ctx = context.copy()
        ctx['iamthechild'] = True
        vals_to_write = self.get_vals_to_write(vals)
        if vals_to_write:
            self.write(cr, uid, ids, vals_to_write, context=ctx)
        return ids



    def parse(self, cr, uid, o, text, context=None):
        if not text:
            return ''
        vals = text.split('[_')
        description = ''
        for val in vals:
            if '_]' in val:
                sub_val = val.split('_]')
                description += (safe_eval(sub_val[0], {'o' :o, 'context':context}) or '' ) + sub_val[1]
            else:
                description += val
        return description


    def generate_product_code(self, cr, uid, product_obj, code_generator, context=None):
        '''I wrote this stupid function to be able to inherit it in a custom module !'''
        return self.parse(cr, uid, product_obj, code_generator, context=context)

    def build_product_code_and_properties(self, cr, uid, ids, context=None):
        for product in self.browse(cr, uid, ids, context=context):
            new_default_code = self.generate_product_code(cr, uid, product, product.product_tmpl_id.code_generator, context=context)
            current_values = {
                'default_code': product.default_code,
                'track_production': product.track_production,
                'track_outgoing': product.track_outgoing,
                'track_incoming': product.track_incoming,
            }
            new_values = {
                'default_code': new_default_code,
                'track_production': product.product_tmpl_id.variant_track_production,
                'track_outgoing': product.product_tmpl_id.variant_track_outgoing,
                'track_incoming': product.product_tmpl_id.variant_track_incoming,
            }
            if new_values != current_values:
                self.write(cr, uid, product.id, new_values, context=context)
        return True

    def product_ids_variant_changed(self, cr, uid, ids, res, context=None):
        '''it's a hook for product_variant_multi advanced'''
        return True

    def generate_variant_name(self, cr, uid, product_id, context=None):
        '''Do the generation of the variant name in a dedicated function, so that we can
        inherit this function to hack the code generation'''
        product = self.browse(cr, uid, product_id, context=context)
        model = product.variant_model_name
        r = map(lambda dim: [dim.dimension_id.sequence, model.replace('[NAME]', (dim.dimension_id.name or '')).replace('[VALUE]', dim.option_id.name or '-')], product.dimension_value_ids)
        r.sort()
        r = [x[1] for x in r]
        new_variant_name = (product.variant_model_name_separator or '').join(r)
        return new_variant_name


    def build_variants_name(self, cr, uid, ids, context=None):
        for product in self.browse(cr, uid, ids, context=context):
            new_variant_name = self.generate_variant_name(cr, uid, product.id, context=context)
            if new_variant_name != product.variants:
                self.write(cr, uid, product.id, {'variants': new_variant_name}, context=context)
        return True

    def _check_dimension_values(self, cr, uid, ids): # TODO: check that all dimension_types of the product_template have a corresponding dimension_value ??
        for p in self.browse(cr, uid, ids, {}):
            buffer = []
            for value in p.dimension_value_ids:
                buffer.append(value.dimension_id)
            unique_set = set(buffer)
            if len(unique_set) != len(buffer):
                return False
        return True

    def compute_product_dimension_extra_price(self, cr, uid, product_id, product_price_extra=False, dim_price_margin=False, dim_price_extra=False, context=None):
        if context is None:
            context = {}
        dimension_extra = 0.0
        product = self.browse(cr, uid, product_id, context=context)
        for dim in product.dimension_value_ids:
            if product_price_extra and dim_price_margin and dim_price_extra:
                dimension_extra += safe_eval('product.' + product_price_extra, {'product': product}) * safe_eval('dim.' + dim_price_margin, {'dim': dim}) + safe_eval('dim.' + dim_price_extra, {'dim': dim})
            elif not product_price_extra and not dim_price_margin and dim_price_extra:
                dimension_extra += safe_eval('dim.' + dim_price_extra, {'dim': dim})
            elif product_price_extra and dim_price_margin and not dim_price_extra:
                dimension_extra += safe_eval('product.' + product_price_extra, {'product': product}) * safe_eval('dim.' + dim_price_margin, {'dim': dim})
            elif product_price_extra and not dim_price_margin and dim_price_extra:
                dimension_extra += safe_eval('product.' + product_price_extra, {'product': product}) + safe_eval('dim.' + dim_price_extra, {'dim': dim})

        if 'uom' in context:
            product_uom_obj = self.pool.get('product.uom')
            uom = product.uos_id or product.uom_id
            dimension_extra = product_uom_obj._compute_price(cr, uid,
                uom.id, dimension_extra, context['uom'])
        return dimension_extra


    def compute_dimension_extra_price(self, cr, uid, ids, result, product_price_extra=False, dim_price_margin=False, dim_price_extra=False, context=None):
        if context is None:
            context = {}
        for product in self.browse(cr, uid, ids, context=context):
            dimension_extra = self.compute_product_dimension_extra_price(cr, uid, product.id, product_price_extra=product_price_extra, dim_price_margin=dim_price_margin, dim_price_extra=dim_price_extra, context=context)
            result[product.id] += dimension_extra
        return result



    def price_get(self, cr, uid, ids, ptype='list_price', context=None):
        if context is None:
            context = {}
        result = super(product_product, self).price_get(cr, uid, ids, ptype, context=context)
        if ptype == 'list_price': #TODO check if the price_margin on the dimension is very usefull, maybe we will remove it
            result = self.compute_dimension_extra_price(cr, uid, ids, result, product_price_extra='price_extra', dim_price_margin='price_margin', dim_price_extra='price_extra', context=context)

        elif ptype == 'standard_price':
            result = self.compute_dimension_extra_price(cr, uid, ids, result, product_price_extra='cost_price_extra', dim_price_extra='cost_price_extra', context=context)
        return result

    def _product_lst_price(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = super(product_product, self)._product_lst_price(cr, uid, ids, name, arg, context=context)
        result = self.compute_dimension_extra_price(cr, uid, ids, result, product_price_extra='price_extra', dim_price_margin='price_margin', dim_price_extra='price_extra', context=context)
        return result


    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'variant_ids':False,})
        return super(product_product, self).copy(cr, uid, id, default, context)

    _columns = {
        'name': fields.char('Name', size=128, translate=True, select=True),
        'dimension_value_ids': fields.many2many('product.variant.dimension.value', 'product_product_dimension_rel', 'product_id','dimension_id', 'Dimensions', domain="[('product_tmpl_id','=',product_tmpl_id)]"),
        'cost_price_extra' : fields.float('Purchase Extra Cost', digits_compute=dp.get_precision('Purchase Price')),
        'lst_price' : fields.function(_product_lst_price, method=True, type='float', string='List Price', digits_compute=dp.get_precision('Sale Price')),
    }
    _constraints = [ (_check_dimension_values, 'Several dimension values for the same dimension type', ['dimension_value_ids']),]

product_product()
