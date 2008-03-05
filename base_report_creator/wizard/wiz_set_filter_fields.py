##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#					Fabien Pinckaers <fp@tiny.Be>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import wizard
import netsvc
import pooler

relation_type=['one2many','many2one','many2many']
char_type = ['char','text','selection']
date_type = ['date','datetime']
int_type = ['float','integer']
remaining_type = ['binary','boolean','reference']


select_field_form = """<?xml version="1.0"?>
<form string="Select Field to filter">
	<field name="field_id" nolabel="1">
	</field>
</form>
"""
select_field_fields = {
					   "field_id":{'string':'Filter Field','type':'many2one', 'relation':'ir.model.fields','required':True}
					   }
set_value_form = """<?xml version="1.0"?>
<form string="Set Filter Values">
	<separator colspan="4" string="Filter Values" />
	<field name="field_id" />
	<field name="operator" />
	<field name="value" colspan="4"/>
</form>
"""

mapping_fields = {'$': 'End With', 'not in': 'Not Contains', '<>': 'Not Equals', 'is': 'Is Empty', 'in': 'Contains', '>': 'Bigger', '=': 'Equals', '<': 'Smaller', 'is not': 'Is Not Empty', '^': 'Start With'}

set_value_fields = {
					'field_id':{'type':'many2one','relation':'ir.model.fields','string':'Field Name','required':True,'readonly':True},
					'operator':{'type':'selection','selection':[
											 ('=','Equals'),
											 ('in','Contains'),
											 ('<>','Not Equals'),
											 ('not in','Not Contains'),
											 ('^','Start With'),
											 ('$','End With'),
											 ('is','Is Empty'),
											 ('is not','Is Not Empty'),
											 ('<','Smaller'),
											 ('>','Bigger')
											 ],'string':'Operator'},
					'value':{'type':'char','string':'Values','size':256},
					}

def _set_field_domain(self,cr,uid,data,context):
	this_model = data.get('model')
	this_pooler = pooler.get_pool(cr.dbname).get(this_model)
	this_data = this_pooler.read(cr,uid,data.get('ids'),['model_ids'],context)[0]
	select_field_fields['field_id']['domain'] = [('model_id','in',this_data.get('model_ids')),('ttype','<>','many2many'),('ttype','<>','one2many')] 
	return {'field_id':False}

#def _set_field_value(self, cr, uid, data, context):
#	field_id = data['form']['field_id']
#	
#	return {}
#

def set_field_operator(self,field_name,field_type,search_operator,search_value):
		field_search = [field_name,search_operator,search_value]		
		if search_operator == '=':
			if field_type=='many2one':
				field_search[1]='in'
				field_search[2] = "("+','.join([str(x) for x in search_value])+")"
			elif field_type in char_type or field_type in date_type:
				field_search[2] = "'"+field_search[2]+"'"
		elif search_operator == '<>':
			if field_type=='many2one':
				field_search[1]='not in'
				field_search[2] = "("+','.join([str(x) for x in search_value])+")"
			elif field_type in char_type or field_type in date_type:
				field_search[2] = "'"+field_search[2]+"'"
		elif search_operator == 'in':
			if field_type=='many2one':
				field_search[2] = "("+','.join([str(x) for x in search_value])+")"
			else:
				field_search[1] = 'ilike'
				field_search[2] = "'%"+search_value+"%'"
			#end if field_type=='one2many':
		elif search_operator == 'not in':
			if field_type=='many2one':
				field_search[2] = "("+','.join([str(x) for x in search_value])+")"
			else:
				field_search[1] = 'not ilike'
				field_search[2] = "'%"+search_value+"%'"
			#end if field_type=='one2many':
		elif search_operator == '^':
			if field_type in char_type:
				field_search[1]='~'
				field_search[2]="'"+search_operator+search_value+"'"
			else:
				return False
			#end if field_type in char_type:
		elif search_operator == '$':
			if field_type in char_type:
				field_search[1]='~'
				field_search[2]="'"+search_value+search_operator+"'"
			else:
				return False
			#end if field_type in char_type:
		elif search_operator in ('is','is not'):
			field_search[2]=False
		elif search_operator in ('<','>'):
			if field_type not in int_type:
				return False
			#end if field_type not in int_type:
		return field_search
def _set_filter_value(self, cr, uid, data, context):
	form_data = data['form']
	value_data = form_data.get('value',False)
	value_field = set_value_fields.get('value')
	field_type = value_field.get('type',False)
	field_data = pooler.get_pool(cr.dbname).get('ir.model.fields').read(cr,uid,[form_data.get('field_id')],fields=['ttype','relation','model_id','name','field_description'])[0]
	model_name = field_data['model_id'][1]
	model_pool = pooler.get_pool(cr.dbname).get(model_name)
	table_name = model_pool._table
	model_name = model_pool._description
	
	if field_type:
		if field_type == 'many2many' and value_data and len(value_data):
			fields_list = set_field_operator(self,table_name+"."+field_data['name'],field_data['ttype'],form_data['operator'],value_data[0][2])
		else:
			fields_list = set_field_operator(self,table_name+"."+field_data['name'],field_data['ttype'],form_data['operator'],value_data)
		if fields_list and value_data:
			create_dict = {
						   'name':model_name + "/" +field_data['field_description'] +" "+ mapping_fields[form_data['operator']] + " " + fields_list[2],
						   'expression':' '.join(fields_list),
						   'report_id':data['id']
						   }
			pooler.get_pool(cr.dbname).get('base_report_creator.report.filter').create(cr,uid,create_dict)
		#end if field_type == 'many2many' and value_data and len(value_data):
#		pooler.get_pool(cr.dbname).get('custom.report.filter').create(cr,uid,form_data)
	#end if field_type:
	return {}

def _set_form_value(self, cr, uid, data, context):
	field_id = data['form']['field_id']
	field_data = pooler.get_pool(cr.dbname).get('ir.model.fields').read(cr,uid,[field_id])[0]
	fields_dict = pooler.get_pool(cr.dbname).get(field_data.get('model_id')[1]).fields_get(cr,uid,fields=[field_data.get('name')])
	value_field = set_value_fields.get('value')
#	print "fields_dict :",fields_dict.get(field_data.get('name'))
#	set_value_fields['value']= fields_dict.get(field_data.get('name'))
	for k,v in value_field.items():
		if k in ('size','relation','type'):
			del value_field[k]
	field_type = field_data.get('ttype',False)
	if field_type in ('one2many','many2many','many2one'):
		value_field['type'] = 'many2many'
		value_field['relation'] = field_data.get('relation')
	else:
		value_field['type'] = field_type
		if field_type == 'selection':
			selection_data = pooler.get_pool(cr.dbname).get(field_data['model']).fields_get(cr,uid,[field_data['name']])
			value_field['selection'] = selection_data.get(field_data['name']).get('selection')
	ret_dict={'field_id':field_id,'operator':'=','value':False}	
	return ret_dict


class set_filter_fields(wizard.interface):
	states = {
		'init': {
			'actions': [_set_field_domain],
			'result': {'type':'form', 'arch':select_field_form, 'fields':select_field_fields, 'state':[('end','Cancel'),('set_value_select_field','Continue')]}			
		},
		'set_value_select_field':{
			'actions': [_set_form_value],
			'result': {'type' : 'form', 'arch' : set_value_form, 'fields' : set_value_fields, 'state' : [('end', 'Cancel'),('set_value', 'Confirm Filter') ]}
		},
		'set_value':{
			'actions': [_set_filter_value],
			'result': {'type': 'state', 'state': 'end'}
		}
	}
set_filter_fields("base_report_creator.report_filter.fields")
