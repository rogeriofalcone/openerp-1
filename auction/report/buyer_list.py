##############################################################################
#
# Copyright (c) 2005 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id$
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


import pooler
import time
from report import report_sxw
from osv import osv

class buyer_list(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(buyer_list, self).__init__(cr, uid, name, context)
		self.localcontext.update({
			'time': time,
#			'sum_taxes': self.sum_taxes,
#			'sum_debit_buyer': self.sum_debit_buyer,
			'lines_lots_from_auction' : self.lines_lots_from_auction,
			'lines_lots_auct_lot' : self.lines_lots_auct_lot,
			'sum_adj_price':self.sum_adj_price

	})



	def lines_lots_from_auction(self,objects):
		print "*********in the function"


		auc_lot_ids = []
		print "OBJECTSS*********",objects
		for lot_id  in objects:
			print "LOTID",lot_id
			auc_lot_ids.append(lot_id.id)
		print "selected lots: ",auc_lot_ids
		self.cr.execute('select auction_id from auction_lots where id in ('+','.join(map(str,auc_lot_ids))+') group by auction_id')
		auc_date_ids = self.cr.fetchall()
		print "AUCTION DATE IDS***************",auc_date_ids
		auct_dat=[]
		for ad_id in auc_date_ids:
			print "s***********",ad_id[0]
			auc_dates_fields = self.pool.get('auction.dates').read(self.cr,self.uid,ad_id[0],['name'])
			print "AUCTION DATE FIELDS",auc_dates_fields
			auct_dat.append(auc_dates_fields)
		print "AUCT LIST",auct_dat
		print "LIST ******FIELDS",auct_dat[0]['name']
#		sql='#		 select id,name from auction_lots where auction_id in (select id from auction_dates where name = 'painting Exhibition');'
		print "RETURN************"
		return auct_dat


	def lines_lots_auct_lot(self,objects):
		print "*********in LOT FUNCTION"
		auc_lot_ids = []
		print "OBJECTSS*********",objects
		for lot_id  in objects:
			print "LOTID",lot_id
			auc_lot_ids.append(lot_id.id)
		print "selected lots: ",auc_lot_ids
		self.cr.execute('select auction_id from auction_lots where id in ('+','.join(map(str,auc_lot_ids))+') group by auction_id')
		auc_date_ids = self.cr.fetchall()
		print "AUCTION DATE IDS***************",auc_date_ids

		auct_dat=[]
		for ad_id in auc_date_ids:
			print "s***********",ad_id[0]
			auc_lots_ids = self.pool.get('auction.lots').search(self.cr,self.uid,([('auction_id','=',ad_id[0])]))
			print "*********auction_lot id",auc_lots_ids
			auc_lot_obj=self.pool.get('auction.lots').browse(self.cr,self.uid,auc_lots_ids)
			print "********AUCTION_LOT _OBJECT",auc_lot_obj[0].name
			for id in auc_lot_obj:
				print "IDSSSSSSSSSSS",id
				auct_dat.append(id)
		return auct_dat


#		print "AUCT LIST",auct_dat
#		print "LIST ******FIELDS",auct_dat[0]['name']
#		sql='#		 select id,name from auction_lots where auction_id in (select id from auction_dates where name = 'painting Exhibition');'
		print "RETURN************"



	def sum_adj_price(self,objects):
		print "*********in LOT FUNCTION"
		auc_lot_ids = []
		print "OBJECTSS*********",objects
		for lot_id  in objects:
			print "LOTID",lot_id
			auc_lot_ids.append(lot_id.id)
		print "selected lots: ",auc_lot_ids
		self.cr.execute('select auction_id from auction_lots where id in ('+','.join(map(str,auc_lot_ids))+') group by auction_id')
		auc_date_ids = self.cr.fetchall()
		print "AUCTION DATE IDS***************",auc_date_ids

		auct_dat=[]
		for ad_id in auc_date_ids:
			print "s***********",ad_id[0]
			auc_lots_ids = self.pool.get('auction.lots').search(self.cr,self.uid,([('auction_id','=',ad_id[0])]))
			print "*********auction_lot id",auc_lots_ids
			auc_lot_obj=self.pool.get('auction.lots').browse(self.cr,self.uid,auc_lots_ids)
			print "********AUCTION_LOT _OBJECT",auc_lot_obj[0].name


#		print "AUCT LIST",auct_dat
#		print "LIST ******FIELDS",auct_dat[0]['name']
#		sql='#		 select id,name from auction_lots where auction_id in (select id from auction_dates where name = 'painting Exhibition');'
		print "RETURN************"
		return auc_lot_obj


#	def sum_taxes(self, lot):
##		buyer_cost = self.pool.get('auction.dates').read(self.cr,self.uid,[auction_id],['buyer_costs'])[0]
##		total_amount = 0.0
##		for id in buyer_cost['buyer_costs'] :
##			amount = self.pool.get('account.tax').read(self.cr,self.uid,[id],['amount'])[0]['amount']
##			total_amount += (amount*obj_price)
##		 return total_amount
#		amount=0.0
#		taxes=[]
#		taxes = lot.product_id.taxes_id
#		taxes += lot.auction_id.buyer_costs
#		if lot.author_right:
#			taxes+=lot.author_right
#		tax=self.pool.get('account.tax').compute(self.cr,self.uid,taxes,lot.obj_price,1)
#		for t in tax:
#			amount+=t['amount']
#		print "amount",amount
#		print "tax",tax
#		return amount
#
#	def sum_debit_buyer(self,auc_id):
#		#auct_id=object.auction_id.id
##		 select id,name from auction_lots where auction_id in (select id from auction_dates where name = 'painting Exhibition');
#
#		self.cr.execute('select buyer_price,is_ok,obj_price,ach_uid, from auction_lots where auction_id=%d'%(auct_id,))
#		res = self.cr.fetchone()
#		print "***************VALUES OF RES",res[0]
#		return str(res[0] or 0)


report_sxw.report_sxw('report.buyer.list', 'auction.lots', 'addons/auction/report/buyer_list.rml', parser=buyer_list)

