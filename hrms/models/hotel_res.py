from openerp.exceptions import except_orm, ValidationError
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp import models, fields, api, _
from openerp import workflow
from openerp.exceptions import Warning as UserError
import time

# from datetime import datetime
import datetime
# from datetime import datetime, timedelta
from datetime import date
#from openerp.osv import fields, osv
from openerp.tools.translate import _
#from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.osv import osv
from datetime import timedelta
from docutils.nodes import line
from pychart.arrow import default
from openerp.osv import expression
from lxml import etree
import dateutil.parser
import pytz



import logging
#from Crypto.Util.number import size
#from translate import _

_logger = logging.getLogger(__name__)

#from time import strftime

to_19 = ( 'Zero',  'One',   'Two',  'Three', 'Four',   'Five',   'Six',
		  'Seven', 'Eight', 'Nine', 'Ten',   'Eleven', 'Twelve', 'Thirteen',
		  'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen' )
tens  = ( 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety')
denom = ( '',
		  'Thousand',     'Million',         'Billion',       'Trillion',       'Quadrillion',
		  'Quintillion',  'Sextillion',      'Septillion',    'Octillion',      'Nonillion',
		  'Decillion',    'Undecillion',     'Duodecillion',  'Tredecillion',   'Quattuordecillion',
		  'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Novemdecillion', 'Vigintillion' )

# class AccountInv(models.Model):
#         _inherit = 'account.invoice'
#
#
#         def create(self,cr,uid,vals,context=None):
#             vals['number2'] = self.pool.get('ir.sequence').get(cr,uid,'account.invoice',context=context)
#
#             return super(AccountInv,self).create(cr,uid,vals,context)

class product_product(models.Model):
        _inherit = 'product.product'
	
	state = fields.Selection([('',''),('draft', 'In Development'),('sellable','Normal'),('end','End of Lifecycle'),('obsolete','Obsolete'),('blocked','Blocked')], 'Status')
	
	
	is_laundry = fields.Boolean('Is Laundry',
								help='Required For calculating seperate amount in final invoice')
	is_hotel_service = fields.Boolean('Hotel Service',help='Hotel Service')
	room_status2 = fields.Boolean('Room Status')
	tax = fields.Float('Tax')


#
#     @api.multi
#     def name_get(self):
#         result = []
#         for product in self:
#             if product.room_status2 == True:
#                 print 'test============================='
#                 reservations = self.env['hotel.room.reservation.line'].search([('status','=','done')])
#                 result.append((product.id,u"%s (%s)" % (product.name, 'asasassa')))
#         return result

#         @api.model
#         def name_search(self, name, args=None, operator='ilike', limit=100):
#             args = args or []
#             recs = self.browse()
#             if name:
#                 recs = self.search([('number', '=', name)] + args, limit=limit)
#             if not recs:
#                 recs = self.search([('name', operator, name)] + args, limit=limit)
#             return recs.name_get()


class HotelReservationLine(models.Model):
	
	_inherit = "hotel_reservation.line"
	
	reserved = fields.One2many('hotel.room.new','room_id')
	room_allocate = fields.Char('Rooms', compute="_get_rooms", store=True)
	
	
	@api.model
	def create(self, vals):
		print "vals================", len(vals)
		res = super(HotelReservationLine, self).create(vals)
		return res
	
	
	
	# @api.multi
	# def write(self, vals):
	#     res = super(HotelReservationLine, self).write(vals)
	#     print 'tst========================', res, dasdasd
	#     if vals.get('eff_rate'):
	#         pass
	#     return res
	
	
	@api.multi
	@api.depends('reserved')
	def _get_rooms(self):
		for line in self:
			line.room_allocate = ''
			for lines in line.reserved:
				line.room_allocate = lines.name.name + ','  + line.room_allocate
	
	
	@api.onchange('categ_id')
	def on_change_categ(self):
		if self.line_id.reservation_type == 'category_based':
			record = self.env['hotel.reservation'].search([('id','=',self.line_id.id)])
			list = []
			for lines in record.add_category:
				list.append(lines.category_id.cat_id.id)
			return {'domain': {'categ_id': [('id', 'in', list)]}}
		if self.line_id.reservation_type == 'room_based':
			
			hotel_room_obj = self.env['hotel.room']
			hotel_room_ids = hotel_room_obj.search([('categ_id', '=',
													 self.categ_id.id)])
			room_ids = []
			# if not self.line_id.checkin:
			# 	raise except_orm(_('Warning'),
			# 					 _('Before choosing a room,\n You have to select \
			# 					 a Check in date or a Check out date in \
			# 					 the reservation form.'))
			for room in hotel_room_ids:
				
				assigned = False
				for line in room.room_reservation_line_ids:
					if line.status not in ['cancel','checkout']:
						
						if (line.check_in <= self.line_id.checkin <
							line.check_out) or (line.check_in <
												self.line_id.checkout <=
												line.check_out):
							assigned = True
				for rm_line in room.room_line_ids:
					if rm_line.status not in ['cancel','checkout']:
						
						if (rm_line.check_in <= self.line_id.checkin <=
							rm_line.check_out) or (rm_line.check_in <=
												   self.line_id.checkout <=
												   rm_line.check_out):
							assigned = True
				if not assigned:
					room_ids.append(room.id)
			domain = {'reserved': [('name', 'in', room_ids)]}
			return {'domain': domain}


#     @api.onchange('categ_id')
#     def on_change_categ(self):
#         '''
#         When you change categ_id it check checkin and checkout are
#         filled or not if not then raise warning
#         -----------------------------------------------------------
#         @param self: object pointer
#         '''

#         hotel_room_obj = self.env['hotel.room']
#         hotel_room_ids = hotel_room_obj.search([('categ_id', '=',
#                                                  self.categ_id.id)])
#         room_ids = []
#         if not self.line_id.checkin:
#             raise except_orm(_('Warning'),
#                              _('Before choosing a room,\n You have to select \
#                              a Check in date or a Check out date in \
#                              the reservation form.'))
#         for room in hotel_room_ids:

#             assigned = False
#             for line in room.room_reservation_line_ids:
#                 if line.status not in ['cancel','checkout']:
#                     checkout2 = self.line_id.checkout
#                     end_dt = datetime.datetime.strptime(checkout2, "%Y-%m-%d %H:%M:%S")
#                     h=end_dt.hour+5
#           #          print 'h================',h
#                     m=end_dt.minute+1
#                     mytime = datetime.datetime.strptime(checkout2, "%Y-%m-%d %H:%M:%S")
#                     mytime -= timedelta(hours=h,minutes=m)
#         #            print mytime.strftime("%Y.%m.%d %H:%M:%S")
#                     dummy_check_out=mytime.strftime("%Y-%m-%d %H:%M:%S")
# #                     print 'dummy_check_out================', dummy_check_out

#                     checkin2 = self.line_id.checkin
#                     str_dt = datetime.datetime.strptime(checkin2, "%Y-%m-%d %H:%M:%S")
#                     h2=str_dt.hour+5
#           #          print 'h================',h2
#                     m2=str_dt.minute-1
#                     mytime = datetime.datetime.strptime(checkin2, "%Y-%m-%d %H:%M:%S")
#                     mytime -= timedelta(hours=h2,minutes=m2)
#           #          print mytime.strftime("%Y.%m.%d %H:%M:%S")
#                     dummy_check_in=mytime.strftime("%Y-%m-%d %H:%M:%S")
# #                     print 'dummy_check_in================', dummy_check_in


# #                     print 'line.check_in=====================', line.check_in
# #                     print 'self.line_id.checkin===============', self.line_id.checkin
# #                     print 'dummy_check_in=================================' ,dummy_check_in
# #                     print 'line.check_out=====================', line.check_out
# #                     print 'line.check_in=====================', line.check_in
# #                     print 'dummy_check_out==============================', dummy_check_out
# #                     print 'self.line_id.checkout===============', self.line_id.checkout
# #                     print 'line.check_out=====================', line.check_out

#                     if (line.check_in <= dummy_check_in <=
#                         line.check_out) or (line.check_in <=
#                                             dummy_check_out <=
#                                             line.check_out):
#                         assigned = True
# #                     if dummy_check_out < line.check_out:
#             for rm_line in room.room_line_ids:
#                 if rm_line.status not in ['cancel','checkout']:

#                     if (rm_line.check_in <= self.line_id.checkin <=
#                         rm_line.check_out) or (rm_line.check_in <=
#                                             self.line_id.checkout <=
#                                             rm_line.check_out):
#                         assigned = True
#             if not assigned:
#                 room_ids.append(room.id)
#         domain = {'reserve': [('id', 'in', room_ids)]}
#         return {'domain': domain}

class HotelRoomNew(models.Model):
	_name = 'hotel.room.new'
	
	@api.one
	@api.onchange('name')
	def onchange_rooms(self):
		category = self.env['add.category.line'].search([('line_id','=',self.room_id.line_id.id),('category_id.cat_id','=',self.room_id.categ_id.id)], limit=1)
		# print 'line_id==================', category, self.room_id.line_id.id, self.room_id.categ_id.id,asd
		if category:
			self.list_price = category.rate
		
		# self.extra_adult = category.extra_adult
		# self.extra_child = category.extra_child
		else:
			self.list_price = self.room_id.categ_id.rate
		
		self.extra_adult = self.name.extra_adult
		self.extra_child = self.name.extra_child
		self.capacity = self.name.capacity
		# taxes_ids = []
		self.categ_id = self.name.categ_id.id
	# tax = self.env['hotel.room.type'].search([('name','=',self.name.categ_id.name)])
	# for vals in tax.tax_ids.ids:
	# 	taxes_ids.append(vals)
	# self.taxes_id = [(6, 0, taxes_ids)]
	
	@api.onchange('list_price')
	def onchange_list_price(self):
		if self.list_price:
			tax = self.env['tax.mapping'].search([])
			for val in tax:
				
				if val.price_from <= self.list_price and val.price_to >= self.list_price:
					self.taxes_id = False
					self.taxes_id = [(6, 0, [i.id for i in val.tax_id])]
	
	
	
	
	@api.one
	@api.depends('list_price','capacity','adults','children')
	def onchange_actual_rate(self):
		print "#######################################"
		# if self
		if (self.adults+self.children) <= self.capacity:
			# print 'test=======================1'
			self.actual_price = self.list_price + ((self.room_id.line_id.ml_plan.adult_rate)*self.adults) + ((self.room_id.line_id.ml_plan.child_rate)*self.children)
			print"$$$$$$$$$$$$$$$$$$$$$$$$$",self.actual_price
	
	
	@api.one
	@api.depends('list_price','capacity','adults','children')
	def onchange_eff_rate(self):
		print 'test================================='
		# if self
		if (self.adults+self.children) <= self.capacity:
			# print 'test=======================1'
			self.eff_rate = self.list_price + ((self.room_id.line_id.ml_plan.adult_rate)*self.adults) + ((self.room_id.line_id.ml_plan.child_rate)*self.children)
		if (self.adults+self.children) > self.capacity:
			# print 'test=======================2',self.list_price , (self.adults - self.capacity)*self.name.extra_adult , self.children*self.name.extra_child , ((self.room_id.line_id.ml_plan.adult_rate)*self.adults) , ((self.room_id.line_id.ml_plan.child_rate)*self.children)
			self.eff_rate = self.list_price + (self.adults - self.capacity)*self.name.extra_adult + self.children*self.name.extra_child + ((self.room_id.line_id.ml_plan.adult_rate)*self.adults) + ((self.room_id.line_id.ml_plan.child_rate)*self.children)
	
	
	
	room_id = fields.Many2one('hotel_reservation.line')
	name = fields.Many2one('hotel.room', 'Name')
	taxes_id = fields.Many2many('account.tax','tax_id_room_rel','room_id','tax_id','Tax')
	list_price = fields.Float('Rate')
	adults = fields.Integer('Adults')
	children = fields.Integer('Children with Bed')
	# categ_id = fields.Many2one('product.category','Internal Category',compute="_compute_fields_room")
	capacity = fields.Integer('Capacity',readonly=True)
	eff_rate = fields.Float(compute='onchange_eff_rate', string="Effective Rate", store=True)
	actual_price = fields.Float('Actual Price',compute='onchange_actual_rate')
	extra_adult = fields.Float('Extra Adult Rate')
	extra_child = fields.Float('Extra Child Rate')
	kids = fields.Integer('Children without bed')
	
	
	@api.model
	def create(self, vals):
		result = super(HotelRoomNew, self).create(vals)
		result.capacity = result.name.capacity
		
		return result
	
	# @api.multi
	# @api.depends('list_price','capacity','adults','children')
	# def _compute_effective_rate(self):
	#     for line in self:
	#         line.eff_rate = 0.0
	#         if line.adults > line.capacity:
	#             line.eff_rate += line.children*1000 + line.list_price + (line.adults - line.capacity)*2000
	#         else:
	#             line.eff_rate += line.children*1000 + line.list_price
	
	
	@api.onchange('room_id','name')
	def on_change_categ(self):
		'''
		When you change categ_id it check checkin and checkout are
		filled or not if not then raise warning
		-----------------------------------------------------------
		@param self: object pointer
		'''
		hotel_room_obj = self.env['hotel.room']
		hotel_room_ids = hotel_room_obj.search([('categ_id', '=',
												 self.room_id.categ_id.id)])
		room_ids = []
		
		# if not self.room_id.line_id.checkin:
		# 	raise except_orm(_('Warning'),
		# 					 _('Before choosing a room,\n You have to select \
		# 					 a Check in date or a Check out date in \
		# 					 the reservation form.'))
		for room in hotel_room_ids:
			
			
			assigned = False
			for line in room.room_reservation_line_ids:
				if line.status != 'cancel':
					if (line.check_in <= self.room_id.line_id.checkin < line.check_out) :
						
						print "ffffffffffffffffffffff",line.check_in,self.room_id.line_id.checkin,line.check_out,room.name
						assigned = True
			if not assigned:
				room_ids.append(room.id)
		domain = {'name': [('id', 'in', room_ids)]}
		# self.rooms_avail = len(room_ids)
		return {'domain': domain}
	
	
	
	@api.multi
	@api.depends('name')
	def _compute_fields_room(self):
		for lines in self:
			taxes_ids = []
			lines.categ_id = lines.name.categ_id.id
			# taxes_ids = [x.ids for x in lines.name.taxes_id]
			for vals in lines.name.taxes_id.ids:
				taxes_ids.append(vals)
			# taxes_ids.append(vals)
			# print "listtttttttttttttttttttttttttt", taxes_ids
			lines.taxes_id = [(6, 0, taxes_ids)]

# @api.multi
# def write(self, vals):
#     if vals.get('eff_rate'):
#         self.room_id.line_id.rack_rate = self.room_id.line_id.room_only + self.room_id.line_id.extra_cash+ self.room_id.line_id.tax_amount
#     res = super(HotelRoomNew, self).write(vals)
#     return res




class sale_order_line(models.Model):
	_inherit = 'sale.order.line'
	
	@api.multi
	@api.depends('product_id','price_unit','product_uom_qty','tax_id')
	def _compute_total_with_tax(self):
		for line in self:
			tax = 0
			included = False
			for lines in line.tax_id:
				tax += lines.amount
				if lines.price_include == True:
					included = True
			line.total_with_tax = (1 + tax)*line.price_unit*line.product_uom_qty
			line.tax_amount = tax*line.price_unit*line.product_uom_qty
			if included == True:
				line.total_with_tax = line.price_unit*line.product_uom_qty
				line.tax_amount = tax*((line.price_unit*line.product_uom_qty)/(1+tax))
	
	
	
	#     product_uom_qty = fields.Float(related='folio_id.duration', string='Qty')
	total_with_tax = fields.Float(compute='_compute_total_with_tax', string='Total', store=True)
	tax_amount = fields.Float(compute='_compute_total_with_tax', string='Tax', store=True)
	pro = fields.Integer('product Id', default=0)


class HotelReservationOrder(models.Model):
	_inherit = 'hotel.reservation.order'
	
	date = fields.Date('Order Date')
	reservation_id = fields.Many2one('hotel.reservation', 'Reservation')
	type = fields.Selection([('Breakfast', 'Breakfast'),
							 ('Lunch', 'Lunch'),
							 ('Dinner', 'Dinner')], 'Type')
	partner_id = fields.Many2one(related='reservation_id.partner_id', string='Guest')
	order_generated = fields.Boolean('Order Generated', default=False)
	
	@api.multi
	def reservation_generate_order(self):
		table_obj = self.env['hotel.restaurant.order']
		table_obj_line = self.env['hotel.restaurant.order.list']
		folio_id = self.env['hotel.folio'].search([('reservation_id','=',self.reservation_id.id)])
		if folio_id.id == False:
			raise except_orm(_('Error'),_('The folio no for this particular guest is not generated'))
			self.room_no = rec.folio_id.room_lines[0].product_id.id
		values = {'is_folio': True,
				  'o_date': self.date,
				  'folio_id': folio_id.id,
				  'room_no': folio_id.room_lines[0].product_id.id,
				  'ml_plan': self.reservation_id.ml_plan,
				  'cname': self.reservation_id.partner_id.id,
				  }
		order_id = table_obj.create(values)
		for lines in  self.order_list:
			values2 = {'name': lines.name.id,
					   'item_qty': lines.item_qty,
					   'item_rate': lines.item_rate,
					   'o_list': order_id.id}
		table_obj_line.create(values2)
		self.order_generated = True
		self.state = 'done'

class ReservationAdvance(models.Model):
	_name = 'reservation.advance'
	
	@api.one
	@api.depends('amount','taxes_id')
	def compute_total_amount(self):
		self.ensure_one()
		if self.taxes_id:
			if self.taxes_id.price_include == True:
				self.total_amount = self.amount
			if self.taxes_id.price_include == False:
				self.total_amount = (1+self.taxes_id.amount)*self.amount
			self.sub_total = self.amount/(1+self.taxes_id.amount)
		else:
			self.total_amount = self.amount
	
	
	date = fields.Date('Date')
	amount = fields.Float('Amount')
	# mode = fields.Selection([('bank', 'Bank'),
	#                           ('card', 'Card'),
	#                           ('cash', 'Cash'),],string='Mode of Payment')
	
	mode = fields.Many2one('account.journal',string='Mode of Payment', domain=[('type','in',['cash','bank'])])
	bank_name = fields.Selection([('sbi', 'SBI'),
								  ('bob', 'BOB'),
								  ('hdfc', 'HDFC')], 'Bank')
	reservation_id = fields.Many2one('hotel.reservation', 'Reservation')
	partner_id = fields.Many2one('res.partner', store=True, string="Customer")
	folio_id = fields.Many2one('hotel.folio', 'Folio')
	state = fields.Selection(related='reservation_id.state', string="State")
	room_no_list = fields.Char(related='reservation_id.room_no_list', string="Rooms")
	taxes_id = fields.Many2one('account.tax', 'Tax')
	total_amount = fields.Float(compute='compute_total_amount', string='Amount', store=True)
	
	
	_defaults = {
		'date': date.today(),
	}
	tax_amount = fields.Float('Tax Amount', compute="_compute_amt")
	amt_without_tax = fields.Float('Amount Without Tax', compute="_compute_amt")
	move_id = fields.Many2one('account.move', string='Move Id')
	
	
	@api.multi
	@api.depends('taxes_id','amount')
	def _compute_amt(self):
		for advance in self:
			advance_tax_ex = 0
			advance_tax_in = 0
			amt_ex = 0
			amt_in = 0
			for tax_id in advance.taxes_id:
				if tax_id.price_include == False:
					advance_tax_ex += advance.amount*tax_id.amount
					amt_ex += advance.amount
				else:
					advance_tax_in += advance.amount - (advance.amount/(1+tax_id.amount))
					amt_in += advance.amount - advance_tax_in
			
			advance.tax_amount = advance_tax_ex + advance_tax_in
			advance.amt_without_tax = amt_ex + amt_in
	
	
	
	@api.onchange('reservation_id','folio_id','amount','date')
	def onchange_partner_id(self):
		if self.reservation_id:
			print 'aaaaaa'
			self.partner_id = self.reservation_id.partner_id.id
		if self.folio_id:
			self.partner_id = self.folio_id.partner_id.id
	
	
	@api.model
	def create(self, vals):
		vals1 = 0
		vals2 = 0
		res = super(ReservationAdvance, self).create(vals)
		moves = self.env['account.move'].create({
			'journal_id':res.mode.id,
			# 'period_id':03,
			'date':res.date,
			'state':'draft'
		})
		
		lines = self.env['account.move.line']
		vals1 = {'move_id':moves.id,
				 'partner_id':res.partner_id.id,
				 'state': 'valid',
				 'name':'Advance',
				 'account_id':res.mode.default_debit_account_id.id,
				 # 'acc_balance':res['mode'].default_debit_account_id.balance,
				 'debit':res.total_amount,
				 'credit':0,
				 # 'current_balance':(res['mode'].default_debit_account_id.balance)-res['amount']
				 }
		lines.create(vals1)
		if res.folio_id.id:
			vals2 = {'move_id':moves.id,
					 'partner_id':res.partner_id.id,
					 'state': 'valid',
					 'name':'Advance',
					 'account_id':res.partner_id.property_account_receivable.id,
					 'debit':0,
					 'credit':res.total_amount,
					 'reserv_id':res.folio_id.reservation_id.id
					 }
		else:
			vals2 = {'move_id':moves.id,
					 'partner_id':res.partner_id.id,
					 'state': 'valid',
					 'name':'Advance',
					 'account_id':res.partner_id.property_account_receivable.id,
					 'debit':0,
					 'credit':res.total_amount,
					 'reserv_id': res.reservation_id.id
					 }
		
		lines.create(vals2)
		moves.button_validate()
		res.move_id = moves.id
		
		# if res['taxes_id'].id:
		#     tax_amount = res['amount']*(res['taxes_id'].amount)
		#     vals3 = {'move_id':moves.id,
		#             'partner_id':res['partner_id'].id,
		#             'state': 'valid',
		#             'name':res['taxes_id'].name,
		#             'account_id':res['taxes_id'].account_collected_id.id,
		#             'debit':0,
		#             'credit':tax_amount,
		#             'reserv_id': res['reservation_id'].id
		#             }
		#     lines.create(vals3)
		return res
	
	@api.multi
	def write(self, vals):
		
		res = super(ReservationAdvance, self).write(vals)
		for record in self:
			if 'move_id' not in vals or 'folio_id' not in vals:
				moves = self.env['account.move'].search([('id','=', record.move_id.id)])
				
				moves.button_cancel()
				for lines in moves.line_id:
					lines.unlink()
				moves.write({
					'journal_id':record.mode.id,
					# 'period_id':03,
					'date':record.date,
					# 'state':'posted'
				})
				
				vals1 = {'move_id':moves.id,
						 'partner_id':record.partner_id.id,
						 # 'state': 'valid',
						 'name':'Advance',
						 'account_id':record.mode.default_debit_account_id.id,
						 'debit':record.total_amount,
						 'credit':0,
						 }
				lines1 = self.env['account.move.line']
				# print '1111========================', lines1
				# lines1.is_posted = False
				lines1.create(vals1)
				
				if record.folio_id.id:
					vals2 = {'move_id':moves.id,
							 'partner_id':record.partner_id.id,
							 'name':'Advance',
							 'account_id':record.partner_id.property_account_receivable.id,
							 'debit':0,
							 'credit':record.total_amount,
							 'reserv_id':record.folio_id.reservation_id.id
							 }
				else:
					vals2 = {'move_id':moves.id,
							 'partner_id':record.partner_id.id,
							 'name':'Advance',
							 'account_id':record.partner_id.property_account_receivable.id,
							 'debit':0,
							 'credit':record.total_amount,
							 'reserv_id':record.reservation_id.id
							 }
				
				# lines2 = self.env['account.move.line'].search([('move_id','=', moves.id)])[1]
				lines1.create(vals2)
				moves.button_validate()
		
		return res
	
	@api.multi
	def unlink(self):
		res = super(ReservationAdvance, self)
		moves = self.env['account.move'].search([('id','=', self.move_id.id)])
		for move in moves:
			move.state = 'draft'
			move.unlink()
		return res.unlink()



class HotelReservation(models.Model):
	_inherit = 'hotel.reservation'
	_order = 'seq desc'
	
	
	# children = fields.Integer('Children', size=64, readonly=True,
	#                              states={'draft': [('readonly', Tru)]},
	#                              help='Number of children there in guest list.')
	
	
	@api.onchange("partner_order_id")
	def onchange_agency_line(self):
		record = self.env['res.partner'].search([('agency','=',True)])
		ids = []
		for item in record:
			ids.append(item.id)
		return {'domain': {'partner_order_id': [('id', 'in', ids)]}}
	
	@api.onchange("partner_id")
	def onchange_partner_line(self):
		record = self.env['res.partner'].search([('agency','!=',True),('customer','=', True)])
		ids = []
		for item in record:
			ids.append(item.id)
		self.partner_order_id =False
		return {'domain': {'partner_id': [('id', 'in', ids)]}}
	
	
	dob = fields.Date('DOB', related="partner_id.dob")
	wdng_day = fields.Date('Wedding Anniversary Date', related="partner_id.wdng_day")
	
	
	@api.one
	@api.depends('reservation_line')
	def _find_room_nos(self):
		self.room_no_list = ' '
		for line in self:
			for lines in line.reservation_line:
				for lines2 in lines.reserved:
					for lines3 in lines2.name.product_id:
						line.room_no_list = lines3.name + ','  + line.room_no_list
	
	@api.multi
	@api.depends('block_ids','reservation_line')
	def _compute_room_no(self):
		block_ids =[]
		for line in self:
			if line.reservation_line:
				block_ids = [block.id for block in self.env['room.type.reservation'].search([('reservation_id','=',line.id)])]
				if block_ids != []:
					for lines in line.block_ids:
						line.no_rooms+=lines.nos
				else:
					for lines in line.reservation_line:
						line.no_rooms += len(lines.reserved)
	# @api.multi
	# @api.onchange('reservation_line','room_only','extra_cash','tax_amount')
	# def _compute_rack_rate(self):
	#     print "aaaaaaa111222222"
	#     for line in self:
	#         line.rack_rate = line.room_only + line.extra_cash + line.tax_amount
	
	
	@api.onchange('rack_rate')
	def onchange_rackrate(self):
		nos = 0
		for line1 in self.reservation_line:
			for room1 in line1.reserved:
				nos += 1
		# print 'nos=====================', nos
		amount = 0
		if nos != 0:
			amount = self.rack_rate/(self.no_nights*nos)
		# print 'amount=======================', amount
		room_only = 0
		room_tax = 0
		for line in self.reservation_line:
			for lines in line.reserved:
				taxi = 0
				taxe = 0
				for tax in lines.taxes_id:
					if tax.price_include == True:
						taxi += tax.amount
					if tax.price_include == False:
						taxe = tax.amount
				room_only += amount/(1+taxi+taxe)
				room_tax += amount-amount/(1+taxi+taxe)
				lines.write({'eff_rate':amount/(1+taxe)})
		
		tax_amount = 0
		service_tax = 0
		extra_cash = 0
		for service in self.extra_line:
			if service.complimentary == True:
				extra_cash += 0
				service_tax += 0
			else:
				if service.every_day == True:
					service_tax += service.tax_amount*self.no_nights
					extra_cash += self.no_nights*service.amt_without_tax
				else:
					service_tax += service.tax_amount
					extra_cash += service.amt_without_tax
		
		self.extra_cash = extra_cash
		
		self.tax_amount = (room_tax*self.no_nights) + service_tax
		self.room_only = room_only*self.no_nights
	
	
	
	@api.multi
	@api.depends('reservation_line', 'extra_line', 'checkin', 'checkout', 'add_category')
	def _compute_tax_amount(self):
		for line in self:
			line.tax_amount = 0
			service_tax = 0
			extra_cash = 0
			for service in line.extra_line:
				if service.complimentary == True:
					extra_cash += 0
					service_tax += 0
				else:
					if service.every_day == True:
						service_tax += service.tax_amount * line.no_nights
						extra_cash += line.no_nights * service.amt_without_tax
					else:
						service_tax += service.tax_amount
						extra_cash += service.amt_without_tax

					# line.extra_cash = extra_cash
			room_tax = 0
			room_only = 0
			extra_rate = 0
			if not line.reservation_line:
				ml_plan_total = 0
				for reserv in line.add_category:
					taxi = 0
					taxe = 0
					if reserv.capacity * reserv.selected_rooms < (float(reserv.adult) + reserv.child):
						if float(reserv.adult) <= reserv.capacity * reserv.selected_rooms:
							# print "ppppppppppppppppp"
							extra_rate += (((float(
								reserv.adult) + reserv.child) - reserv.capacity * reserv.selected_rooms) * reserv.category_id.extra_child) / reserv.selected_rooms
						elif reserv.adult > reserv.capacity * reserv.selected_rooms and reserv.child != 0:
							# print "kjkkkkkkkkkkkkkkkkkkkk"
							extra_rate += ((reserv.adult - (
									reserv.capacity * reserv.selected_rooms)) * reserv.category_id.extra_adult + reserv.child * reserv.category_id.extra_child) / reserv.selected_rooms
						else:
							# print "jhdkjfhjkfjkdfkhdjhgjjgjh"
							extra_rate += (((float(
								reserv.adult) + reserv.child) - reserv.capacity * reserv.selected_rooms) * reserv.category_id.extra_child) / reserv.selected_rooms

					# print "extra_rate====================", extra_rate
					ml_plan_rate = reserv.adult * reserv.line_id.ml_plan.adult_rate + reserv.child * reserv.line_id.ml_plan.child_rate
					ml_plan_total += ml_plan_rate
					for tax in reserv.tax_ids:
						if tax.price_include == True:
							taxi += tax.amount
						if tax.price_include == False:
							taxe += tax.amount

					ml_taxi = 0
					ml_taxe = 0
					if line.ml_plan.tax_id.price_include == True:
						ml_taxi = line.ml_plan.tax_id.amount
					if line.ml_plan.tax_id.price_include == False:
						ml_taxe = line.ml_plan.tax_id.amount

					# print " reserv.category_id.rate============",  reserv.category_id.rate, 1+taxi
					room_only += ((reserv.rate + extra_rate) * reserv.selected_rooms) / (1 + taxi) + ml_plan_rate / (
							1 + ml_taxi)
					room_tax += ((reserv.rate + extra_rate) * reserv.selected_rooms) / (1 + taxi) * (
							taxi + taxe) + ml_plan_rate / (1 + ml_taxi) * (ml_taxi + ml_taxe)
			# raise UserError(str(room_only))
			else:

				# for reserv in line.reservation_line:
				#     eff_rate = 0
				#     ml_plan_amount = 0

				for reserv in line.reservation_line:
					eff_rate = 0
					ml_plan_amount = 0
					total_ml_taxi = 0
					total_ml_taxe = 0
					taxi = 0
					taxe = 0
					room_amount = 0
					room_amount_tax = 0
					total_amount = 0
					total_tax = 0
					for room_line in reserv.particulars_ids:

						if not room_line.particulars_id.is_room_rent:

							ml_plan_amount += room_line.total
							ml_taxi = 0
							ml_taxe = 0
							taxx = 0
							for tax in room_line.taxes_id:
								taxx = tax.amount
								if tax.price_include == True:
									ml_taxi = tax.amount
									
								if tax.price_include == False:
									ml_taxe = tax.amount
									
							if ml_taxi != 0:
								total_ml_taxi = room_line.total * ml_taxi
								total_amount += ml_plan_amount - total_ml_taxi
							if ml_taxe != 0:
								total_ml_taxe = room_line.total * ml_taxe
								total_amount += (room_line.rate * room_line.number)
							total_tax += (room_line.rate * room_line.number)* taxx
							total_ml_taxe += room_line.total * ml_taxe
							
						else:
							room_amount += room_line.total
							taxi = 0
							taxe = 0
							for tax in room_line.taxes_id:
								if tax.price_include == True:
									taxi = tax.amount
								if tax.price_include == False:
									taxe = tax.amount
							room_amount_tax = room_amount * taxi
						
					room_only = reserv.total
					room_tax = reserv.tax_amount
			# raise UserError(str(room_tax))

			no_date = 0
			if line.checkout and line.checkin:
				date_format = "%Y-%m-%d"
				checkin = datetime.datetime.strptime(line.checkin, date_format)
				checkout = datetime.datetime.strptime(line.checkout, date_format)
				no_date = (checkout - checkin).days
				if no_date < 1:
					no_date = 1

			# print "rooomonly=======================", room_only, no_date
			
			line.room_only = room_only * no_date
			# print "room_tax===================", room_tax
			# print "nights=====================", line.no_nights

			line.tax_amount = (room_tax * line.no_nights) + service_tax



	@api.multi
	@api.depends('reservation_line','add_category')
	def _compute_special_rate(self):
		for line in self:
			line.special_rate = 0
			line.adults = 0
			line.children = 0
			for lines in line.reservation_line:
				for rooms in lines.particulars_ids:
					if rooms.particulars_id.name == 'Children With Bed':
						line.children += rooms.number
					elif rooms.particulars_id.name == 'Children Without Bed':
						line.kids += rooms.number
					elif rooms.particulars_id.name == 'Adults':
						line.adults += rooms.number
					
					
					
					
			if not line.reservation_line:
				for categ in line.add_category:
					line.adults += categ.adult
					line.children += categ.child
	
	@api.multi
	@api.depends('rack_rate','advance','discount')
	def _compute_balance(self):
		# print "hsgdhfsjfdjfj"
		for line in self:
			# print "aaaaaaaaaaaaaaaaaaaaaaaaa", line.rack_rate
			line.balance = line.rack_rate - line.advance - line.discount
	
	
	@api.multi
	@api.depends('advance_lines')
	def _compute_advance(self):
		for line in self:
			line.advance = 0
			advance = 0
			advance_tax = 0
			for lines in line.advance_lines:
				line.advance += lines.total_amount
	
	@api.multi
	@api.depends('reservation_line')
	def _find_room_category(self):
		for line in self:
			line.room_type = ''
			for lines in line.reservation_line:
				line.room_type +=  ','
	
	
	
	@api.onchange('cutoff_date','checkin')
	def _cut_off_date_check(self):
		print 'test==================='
		if self.cutoff_date > self.checkin:
			self.cutoff_date = False
			return {
				'warning': {'title': _('Warning'), 'message': _('Cutoff date \
					should be greater than Checkin date.')}
			}
	
	
	
	# @api.onchange('date_order')
	# def onchange_date_order(self):
	# 	if self.date_order:
	# 		days = timedelta(days=self.company_id.cutoff_date)
	# 		date_order = datetime.datetime.strptime(self.date_order, "%Y-%m-%d %H:%M:%S")
	# 		cutoff_date = date_order + days
	# 		self.cutoff_date = cutoff_date
	
	
	
	@api.multi
	@api.depends('room_only','tax_amount','extra_cash')
	def compute_rack_rate_line(self):
		for line in self:
			line.rack_rate = line.room_only+line.tax_amount+line.extra_cash
	
	
	@api.multi
	@api.depends('seq')
	def compute_no(self):
		for rec in self:
			# print 'test========================dddd'
			if rec.seq:
				rec.grc_no = 'A/'+str(rec.seq)
	
	
	
	# @api.model
	# def create(self, vals):
	# 	last_id = self.env['hotel.reservation'].search([])[-1].id
	# 	print 'last id ====================================',last_id
	
	# cnt = vals.get('seq')
	# cnt_val = self.env['hotel.reservation'].browse(cnt)
	# student_rec = self.env['student.student'].search([('student_class', '=',cnt)])
	# print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$', student_rec,cnt_val
	# if len(student_rec) == 0:
	# 	vals['grc_no'] = 'A' + '/' + '1'
	# 	vals['seq'] = 1
	# else:
	# 	update_id = self.env['student.student'].search([('student_class', '=',cnt)],order='id desc', limit=1).seq+1
	# 	print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$', update_id
	# 	vals['grc_no'] = 'A' + '/' + str(update_id)
	# 	vals['seq'] = update_id
	
	
	# print 'vals===========================', vals
	
	# return super(HotelReservation, self).create(vals)
	
	
	
	# @api.multi
	# @api.depends('seq2')
	# def comute_reservation_no(self):
	# 	for rec in self:
	# 		rec.reservation_no = 'R/'+str(rec.seq2)
	
	
	
	
	READONLY_STATES = {
		'confirm': [('readonly', True)],
		'cancel': [('readonly', True)],
		'done': [('readonly', True)],
	}
	
	READONLY_STATES1 = {
		'cancel': [('readonly', True)],
		'done': [('readonly', True)],
	}
	
	READONLY_STATES2 = {
		'cancel': [('readonly', True)],
		'confirm': [('readonly', True)],
		'done': [('readonly', True)],
		'checkout': [('readonly', True)],
	}
	
	READONLY_STATES3 = {
		'cancel': [('readonly', True)],
		'checkout': [('readonly', True)],
	}
	
	# seq_new = fields.Integer('seq')
	guest_nick = fields.Char('Quick Name')
	advance = fields.Float(compute='_compute_advance', store=True, string='Advance payment')
	#    read=['hrms.hotel_receptionist'], write=['hrms.hotel_account']
	service_line = fields.One2many('hotel.services', 'line_id_reservation',
								   'Services Line',
								   help='Service details')
	identification_id = fields.Char('ID No', size=64)
	id_type = fields.Selection([('passport', 'Passport'),
								('adhar', 'Adhar Card'),
								('voter', 'Voter ID'),
								('pan', 'PAN Card'),
								('licence', 'Licence'), ], 'Type of ID Card')
	extra_amount_bed = fields.Float('Extra Bed Amount', default=0.0, states=READONLY_STATES)
	extra_bed_no = fields.Float('No of Extra Bed Per Night', default=0.0, states=READONLY_STATES)
	pre_extra_amount_bed= fields.Float('Pre Extra Bed', default=0.0)
	pre_extra_amount_withoutbed= fields.Float('Pre Without Bed', default=0.0)
	extra_amount_withoutbed = fields.Float('Without Bed', default=0.0, states=READONLY_STATES)
	# adults = fields.Integer('Adults', size=64,compute='_compute_special_rate', store=True,
	# 						help='List of adults there in guest list. ', states=READONLY_STATES)
	adults = fields.Integer('Adults', size=64,
							help='List of adults there in guest list. ')
	children = fields.Integer('Children With Bed', size=64,readonly=True, states={'draft': [('readonly', True)]},store=True,
							  help='Number of children there in guest list.',compute='_compute_special_rate')
	ml_plan_rate = fields.Float('Rate', default=0.0, states=READONLY_STATES)
	# ml_plan = fields.Selection([('Breakfast', 'Breakfast'),
	#                           ('Lunch', 'Lunch'),
	#                           ('Dinner', 'Dinner')], 'Meal Plan', states=READONLY_STATES)
	ml_plan = fields.Many2one('meal.plan',string='Meal Plan')
	special_rate = fields.Float(compute='_compute_special_rate', store=True, string='Special Rate')
	tax_amount = fields.Float(compute='_compute_tax_amount', string='Tax Amount')
	room_only = fields.Float(compute='_compute_tax_amount', string='Rooms /-')
	extra_cash = fields.Float(compute='_compute_tax_amount', string='Extra', store=True)
	rack_rate = fields.Float(string='Rack Rate',compute="compute_rack_rate_line")
	balance = fields.Float(compute='_compute_balance', string='Balance')
	cutoff_date = fields.Date('Cutoff Date', help="Reconfirm the booking with advance payment on or before the Cutoff date otherwise booking will consider as invalid")
	# no_rooms = fields.Integer(compute='_compute_room_no', string='No of Rooms')
	no_rooms = fields.Integer(string='No of Rooms')
	no_nights = fields.Float('No of Nights')
	room_type = fields.Char(compute='_find_room_category', string='Room Category', store=True)
	rate_without_service = fields.Float('Rate Without Service')
	checkin_dummy = fields.Datetime('Dummy-Date-Arrival')
	checkout_dummy = fields.Datetime('Dummy-Date-Departure')
	extra_line = fields.One2many('extra.service.line', 'line_id_extra',
								 'Extras',
								 help='Extras')
	account_id = fields.Many2one('account.account', 'Account')
	journal_id = fields.Many2one('account.journal', 'Journal')
	period_id = fields.Many2one('account.period', 'Journal')
	is_validated = fields.Boolean('Is validated', default=False, readonly=True)
	partner_id = fields.Many2one('res.partner', 'Guest Name', readonly=True,
								 required=True, domain=[('agency','!=',True)],
								 states={'draft': [('readonly', False)],'confirm': [('readonly', False)]})
	#         partner_invoice_id = fields.Many2one('res.partner', 'Invoice Address', readonly=True,
	#                                  required=True,
	#                                  states={'draft': [('readonly', False)],'confirm': [('readonly', False)]})
	#         partner_order_id = fields.Many2one('res.partner', 'Traveling Agent', readonly=True,
	#                                  required=True,
	#                                  states={'draft': [('readonly', False)],'confirm': [('readonly', False)]})
	folio_id = fields.Many2one('hotel.folio', 'Folio Id')
	room_no_list = fields.Char(compute='_find_room_nos', store=True, string='Rooms')
	block_ids = fields.One2many('room.type.reservation', 'reservation_id', 'Reservations')
	#         company_id = fields.Many2one('res.company', string='Company', change_default=True,
	#                                      required=True, readonly=True, states={'draft': [('readonly', False)]},
	#                                      default=lambda self: self.env['res.company']._company_default_get('hotel.reservation'))
	company_id = fields.Many2one('res.company', 'Company', required=True)
	warehouse_id = fields.Many2one('stock.warehouse', 'Hotel', required=False)
	payment_mode = fields.Char('Payment Mode', states=READONLY_STATES)
	reservation_line = fields.One2many('hotel_reservation.line', 'line_id',
									   'Reservation Line',
									   help='Hotel room reservation details.',states=READONLY_STATES1)
	discount = fields.Float('Discount')
	food_order_lines = fields.One2many('hotel.reservation.order', 'reservation_id', 'Food Order')
	kids = fields.Integer('Children Without Bed', size=64,readonly=True, states={'draft': [('readonly', True)]},store=True,
						  help='Number of children there in guest list.',compute='_compute_special_rate')
	remarks = fields.Text('Remarks')
	
	# guest_type = fields.Selection([('room', 'Room Guest'),
	#                       ('op', 'Out Patient'),
	#                       ('casual', 'Casual'),
	#                       ('advance', 'Advance Booking')], 'Guest Type', states=READONLY_STATES)
	
	guest_type = fields.Selection([('room', 'Direct'),('ota','OTA'),
								   ('advance', 'Through Agency')],
								  'Guest Type',default="room", states=READONLY_STATES3,)
	partner_order_id = fields.Many2one('res.partner', 'Ordering Contact',
									   states=READONLY_STATES3,
									   help="The name and address of the "
											"contact that requested the order "
											"or quotation.")
	advance_lines = fields.One2many('reservation.advance', 'reservation_id', 'Advance Payments')
	state = fields.Selection([('draft', 'Draft'),('block','Blocked'), ('confirm', 'Confirm'),
							  ('done', 'Checkin'),('checkout', 'Checkout'),('cancel', 'Cancel')],
							 'State', readonly=True,
							 default=lambda *a: 'draft')
	checkin_time = fields.Char('Check In Time')
	check_in_time = fields.Datetime('Check In Time')
	can_edit = fields.Boolean('Can Edit', default=False)
	arrived_from = fields.Char('Arrived From')
	proceed_to = fields.Char('Proceeding To')
	visit_purpose = fields.Char('Purpose of Visit')
	is_foreigner = fields.Boolean(related="partner_id.is_foreigner")
	arrival_date = fields.Date('Date of arrival in India')
	employed_in_india = fields.Boolean('Whether Employed in India')
	duration_india = fields.Char('Proposed duration of stay in India')
	checkin = fields.Date('Expected-Date-Arrival',required=True,
						  )
	checkout = fields.Date('Expected-Date-Departure', required=True,
						   )
	add_category = fields.One2many('add.category.line','line_id', states=READONLY_STATES2)
	reservation_type = fields.Selection([('room_based','Room based'),('category_based','Category Based')],default="category_based",states=READONLY_STATES2)
	visible_res = fields.Boolean(default=False)
	seq = fields.Integer('Sequence')
	grc_no = fields.Char(compute='compute_no', string='GRC No:')
	seq2 = fields.Integer('Sequence2')
	reservation_no = fields.Char( string='Reservation No')
	direct_walking = fields.Boolean(string='Direct Walking',copy=False,default=False)
	given_rooms_ids = fields.Many2many('hotel.room','hote_reservation_room_rel','reservation_id','room_id',string="Given Rooms")
	
	
	
	
	
	
	
	
	@api.onchange('reservation_type')
	def onchange_reservation_type(self):
		if self.reservation_type == 'room_based':
			self.visible_res = True
		else:
			self.visible_res = False
	
	_defaults = {
		'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
		
	}
	
	@api.multi
	def block(self):
		self.state = 'block'
	
	@api.onchange('checkin')
	def onchange_checkin(self):
		if self.checkin:
			self.checkout = self.checkin
	@api.multi
	def make_editable(self):
		for line in self:
			line.can_edit = True
	
	
	
	
	@api.constrains('checkin', 'checkout')
	def check_in_out_dates(self):
		"""
		When date_order is less then checkin date or
		Checkout date should be greater than the checkin date.
		"""
	#if self.checkout and self.checkin:
	#    if self.checkin < self.date_order:
	#        raise except_orm(_('Warning'), _('Checkin date should be \
	#        greater than the current date.'))
	#    if self.checkout < self.checkin:
	#        raise except_orm(_('Warning'), _('Checkout date \
	#        should be greater than Checkin date.'))
	
	@api.constrains('reservation_line', 'adults', 'children')
	def check_reservation_rooms(self):
		'''
		This method is used to validate the reservation_line.
		-----------------------------------------------------
		@param self: object pointer
		@return: raise a warning depending on the validation
		'''
		for reservation in self:
			if len(reservation.reservation_line) == 0:
				print '1'
			#                     raise ValidationError(_('Please Select Rooms \
			#                     For Reservation.'))
			for rec in reservation.reservation_line:
				if len(rec.reserved) == 0:
					print '1'
				#                         raise ValidationError(_('Please Select Rooms \
				#                         For Reservation.'))
				cap = 0
				for room in rec.reserved:
					cap += room.capacity
				if (self.adults + self.children) > cap:
					print '1'
	#                             raise ValidationError(_('Room Capacity \
	#                             Exceeded \n Please Select Rooms According to \
	#                             Members Accomodation.'))
	
	def default_get(self,cr,uid,fields,context=None):
		res = super(HotelReservation, self).default_get(cr, uid, fields, context=context)
		if context.get('default_direct_walking',False):
			res.update({'reservation_no':'/'})
		else:
			res.update({'reservation_no':"SBR/" + datetime.datetime.now().strftime("%y/%m/%d") + '/'})
		
		return res
	
	def create(self, cr, uid, vals, context=None):
		
		date_format = "%Y-%m-%d"
		checkin = datetime.datetime.strptime(vals['checkin'], date_format)
		checkout = datetime.datetime.strptime(vals['checkout'], date_format)
		no_date = (checkout-checkin).days
		
		
		if no_date <1:
			no_date = 1
		
		
		
		
		# vals['reservation_no']= self.pool.get('ir.sequence').get(cr,uid,'hotel.reservation')
		vals['no_nights']=no_date
		reservation = self.pool.get('hotel.reservation').search(cr, uid,[], order='seq2 desc', limit=1)
		# print 'reservation======================', reservation.seq, asd
		# if not reservation:
		# 	vals['seq2'] = 1
		# else:
		# 	vals['seq2'] = self.pool.get('hotel.reservation').browse(cr,uid, reservation).seq2 + 1
		
		
		
		
		# reservation_no = self.pool['ir.sequence'
		#                               ].get(cr, uid, 'hotel.reservation').encode('utf-8')
		# nos = ''.join(filter(str.isdigit, reservation_no))
		# code = self.pool.get('res.users').browse(cr, uid, uid).company_id.code
		# if code:
		#     vals['reservation_no'] = code+'/'+nos
		
		if vals.get('external_user') == True:
			vals['partner_id'] = self.pool.get('res.users').browse(cr, uid, uid).partner_id.id
			vals['pricelist_id'] = self.pool.get('res.users').browse(cr, uid, uid).partner_id.property_product_pricelist.id
			vals['partner_shipping_id'] = self.pool.get('res.users').browse(cr, uid, uid).partner_id.id
			
			date_order = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
			days = timedelta(self.pool.get('res.company').browse(cr, uid, vals.get('company_id')).cutoff_date)
			date_order = datetime.datetime.strptime(date_order, "%Y-%m-%d %H:%M:%S")
			cutoff_date = date_order + days
			vals['cutoff_date'] = cutoff_date
		
		
		# if vals.get('reservation_no',False) == '/':
		
		#   vals['reservation_no'] = datetime.now()
		# vals['saved'] = True
		
		
		# reservation_no = datetime.datetime.now().strftime("%y/%m/%d")
		if context.get('default_direct_walking',False):
			vals['reservation_no'] = self.pool['ir.sequence'].get(cr, uid, 'hotel.reservation').encode('utf-8')

		if self.search(cr,uid,[('reservation_no','=',vals['reservation_no'])],context=None):
			raise except_orm(_('ValidateError'), _('Reservation Number should be Unique'))
		
		
		model = super(HotelReservation, self).create(cr, uid, vals, context=context)
		return model
	
	def write(self, cr, uid, ids, vals, context=None):
		res = super(HotelReservation, self).write(cr, uid, ids, vals, context=context)
		
		
		if 'partner_id' in vals:
			partner_shipping_id=vals['partner_id']
			res = super(HotelReservation, self).write(cr, uid, ids, { 'partner_shipping_id': partner_shipping_id}, context=None)
		#self_obj.write({'tax': tax1, 'serv': temp},context=None)
		
		if 'checkin' in vals or 'checkout' in vals:
			block_ids = self.browse(cr,uid,ids,context).block_ids
			if 'checkin' in vals:
				for lines in block_ids:
					checkin = vals['checkin']
					# mytime = datetime.datetime.strptime(checkin, "%Y-%m-%d %H:%M:%S")
					# mytime += timedelta(hours=5,minutes=30)
					# check_in = mytime.strftime("%Y-%m-%d %H:%M:%S")
					lines.check_in = datetime.datetime.strptime(checkin, '%Y-%m-%d').date()
			
			if 'checkout' in vals:
				for lines in block_ids:
					checkout = vals['checkout']
					# mytime = datetime.datetime.strptime(checkout, "%Y-%m-%d %H:%M:%S")
					# mytime += timedelta(hours=5,minutes=30)
					# check_out = mytime.strftime("%Y-%m-%d %H:%M:%S")
					lines.check_out=datetime.datetime.strptime(checkout, '%Y-%m-%d').date()
		
		if 'block_ids' in vals:
			block_ids = self.browse(cr,uid,ids,context).block_ids
			for lines in block_ids:
				#                     lines.check_in = self.browse(cr,uid,ids,context).checkin
				checkin = self.browse(cr,uid,ids,context).checkin
				# mytime = datetime.datetime.strptime(checkin, "%Y-%m-%d %H:%M:%S")
				# mytime += timedelta(hours=5,minutes=30)
				# check_in = mytime.strftime("%Y-%m-%d %H:%M:%S")
				lines.check_in = datetime.datetime.strptime(checkin, '%Y-%m-%d').date()
				
				#                     lines.check_out = self.browse(cr,uid,ids,context).checkout
				checkout = self.browse(cr,uid,ids,context).checkout
				# mytime = datetime.datetime.strptime(checkout, "%Y-%m-%d %H:%M:%S")
				# mytime += timedelta(hours=5,minutes=30)
				# check_out = mytime.strftime("%Y-%m-%d %H:%M:%S")
				lines.check_out=datetime.datetime.strptime(checkout, '%Y-%m-%d').date()
		
		
		
		no_date = 0
		if 'checkout' in vals:
			date_a = vals['checkout']
		else:
			date_a = self.browse(cr,uid,ids,context).checkout
		if 'checkin' in vals:
			date_b = vals['checkin']
		else:
			date_b = self.browse(cr,uid,ids,context).checkin
		
		date_format = "%Y-%m-%d"
		# date_format = "%Y-%m-%d %H:%M:%S"
		# checkout=datetime.datetime.strptime(self.date_a, date_format).date()
		if date_a and date_b:
			checkout = datetime.datetime.strptime(date_a, date_format)
			checkin = datetime.datetime.strptime(date_b, date_format)
			no_date = (checkout-checkin).days
			# print "no_date2222222222222222222222", no_date
		if no_date <1:
			no_date = 1
		
		if no_date != 0:
			res = super(HotelReservation, self).write(cr, uid, ids, { 'no_nights': no_date}, context=None)
		
		if 'rack_rate' in vals and self.browse(cr,uid,ids,context).can_edit == True:
			# print 'test==========================123',self.pool.get('hotel.reservation').browse(cr, uid, ids[0], context).saved
			rec = self.pool.get('hotel.reservation').browse(cr, uid, ids[0], context)
			# print 'res.rack_rate======================================adadasd', self.browse(cr,uid,ids,context).extra_line, self.browse(cr,uid,ids,context).reservation_line
			line = self.browse(cr,uid,ids,context)
			# nos = len(line.reservation_line.reserved)
			nos = 0
			for line1 in line.reservation_line:
				for room1 in line1.reserved:
					nos+=1
			amount = 0
			if nos != 0 and line.no_nights !=0:
				amount = line.rack_rate/(line.no_nights*nos)
			room_only = 0
			room_tax = 0
			for room in line.reservation_line:
				for lines in room.reserved:
					taxi = 0
					taxe = 0
					for tax in lines.taxes_id:
						if tax.price_include == True:
							taxi += tax.amount
						if tax.price_include == False:
							taxe = tax.amount
					room_only += amount/(1+taxi+taxe)
					room_tax += (amount-amount/(1+taxi+taxe))
				# lines.write({'eff_rate':amount})
			
			tax_amount = 0
			service_tax = 0
			for service in line.extra_line:
				if service.complimentary == True:
					service_tax += 0
				else:
					if service.every_day == True:
						service_tax += service.tax_amount*line.no_nights
					else:
						service_tax += service.tax_amount
			
			line.room_only = room_only*line.no_nights
			line.tax_amount = (room_tax*line.no_nights) + service_tax
			line.can_edit = False
		
		return res
	
	
	# def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=80):
	# 	if args is None:
	# 		args = []
	# 	if operator in expression.NEGATIVE_TERM_OPERATORS:
	# 		domain = [('reservation_no', operator, name)]
	# 	else:
	# 		domain = [('reservation_no', operator, name)]
	# 	ids = self.search(cr, user, expression.AND([domain, args]), limit=limit, context=context)
	# 	return self.name_get(cr, user, ids, context=context)
	
	# def name_get(self, cr, uid, ids, context=None):
	# 	if not ids:
	# 		return []
	# 	if isinstance(ids, (int, long)):
	# 				ids = [ids]
	# 	reads = self.read(cr, uid, ids, ['reservation_no', 'seq'], context=context)
	# 	res = []
	# 	for record in reads:
	# 		name = record['seq']
	# 		if record['reservation_no']:
	# 			name = 'A/' + str(name)
	# 		res.append((record['id'], name))
	# 	return res
	
	
	@api.multi
	def unlink(self):
		for rec in self:
			up = self.env['hotel.reservation'].search([('seq','>',rec.seq)], order='seq desc')
			if up:
				for line in up:
					line.seq -= 1
					line.seq2 -= 1
		result = super(HotelReservation, self).unlink()
	
	@api.multi
	def confirmed_reservation(self):
		# print('###################################### work flow')
		if self.reservation_type == 'category_based':
			if not self.add_category:
				raise except_orm(_('Error'),_('No Category is selected.'))
			else:
				for lines in self.add_category:
					self.env['room.type.reservation'].sudo().create({
						'status':'assigned',
						'state':'assigned',
						'check_in':self.checkin,
						'check_out':self.checkout,
						'reservation_id':self.id,
						'nos':lines.selected_rooms,
						'room_type_id':lines.category_id.id
					})
		else:
			categs = []
			for line in self.reservation_line:
				if not line.categ_id.id in categs:
					categs.append(line.categ_id.id)
			for categ in categs:
				for lines in self.reservation_line:
					if lines.categ_id.id == categ:
						l = len(lines.reserved)
						self.env['room.type.reservation'].sudo().create({
							'status':'assigned',
							'state':'assigned',
							'check_in':self.checkin,
							'check_out':self.checkout,
							'reservation_id':self.id,
							'nos':l,
							'room_type_id':self.env['hotel.room.type'].search([('cat_id','=',categ)]).id
						})
		state = ['block','confirm','done']
		for lines in self.reservation_line:
			for rooms in lines.reserved:
				room_id = rooms.name.id
				room = self.env['hotel.room.reservation.line'].search([('room_id','=',room_id),('status','in',state)])
				for line in room:
					if line.check_in <= self.checkin <= line.check_out:
						raise except_orm(_('Warning'),_('Sorry..!! The Room Is Blocked Already..'))
					elif line.check_in <= self.checkout <= line.check_out:
						raise except_orm(_('Warning'),_('Sorry..!! The Room Is Blocked Already..'))
		
		reservation_line_obj = self.env['hotel.room.reservation.line']
		for reservation in self:
			self._cr.execute("select count(*) from hotel_reservation as hr "
							 "inner join hotel_reservation_line as hrl on \
							 hrl.line_id = hr.id "
							 "inner join hotel_reservation_line_room_rel as \
							 hrlrr on hrlrr.room_id = hrl.id "
							 "where (checkin,checkout) overlaps \
							 ( timestamp %s, timestamp %s ) "
							 "and hr.id <> cast(%s as integer) "
							 "and hr.state = 'confirm' "
							 "and hrlrr.hotel_reservation_line_id in ("
							 "select hrlrr.hotel_reservation_line_id \
							 from hotel_reservation as hr "
							 "inner join hotel_reservation_line as \
							 hrl on hrl.line_id = hr.id "
							 "inner join hotel_reservation_line_room_rel \
							 as hrlrr on hrlrr.room_id = hrl.id "
							 "where hr.id = cast(%s as integer) )",
							 (reservation.checkin, reservation.checkout,
							  str(reservation.id), str(reservation.id)))
			res = self._cr.fetchone()
			roomcount = res and res[0] or 0.0
			# print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
			if roomcount:
				raise except_orm(_('Warning'), _('You tried to confirm \
					reservation with room those already reserved in this \
					reservation period'))
			else:
				self.write({'state': 'block'})
				for line_id in reservation.reservation_line:
					line_id = line_id.reserved
					# print '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@22 ck'
					for room_id in line_id:
						vals = {
							'room_id': room_id.name.id,
							'check_in': reservation.checkin,
							'check_out': reservation.checkout,
							'state': 'assigned',
							'reservation_id': reservation.id,
						}
						room_id.name.write({'isroom': False, 'status': 'block'})
						reservation_line_obj.create(vals)
	# self.create_folio()
	# rec = self.env['ir.attachment'].search([('res_model','=','hotel.reservation'),('res_name','=',self.reservation_no+'...')])
	# # print '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^',rec
	# if len(rec) == 0:
	# 	return {
	# 			'name': 'Warning Message',
	# 			'view_type': 'form',
	# 			'view_mode': 'form',
	# 			'res_model': 'warning.attachment',
	# 			'view_id': self.env.ref('hrms.view_warning_message_form').id,
	# 			'target': 'new',
	# 			'type': 'ir.actions.act_window',
	# 			'context': {}
	# 					}
	# self.write({'state':'block'})
	
	
	
	# @api.multi
	# def confirmed_reservation(self):
	#     print "hjkkkkkkkkkkkkkkkkkkkkkkkkkk"
	#     state = ['block','confirm','done']
	#     for lines in self.reservation_line:
	#         for rooms in lines.reserved:
	#             room_id = rooms.name.id
	#             room = self.env['hotel.room.reservation.line'].search([('room_id','=',room_id),('status','in',state)])
	#             for line in room:
	#                 if line.check_in <= self.checkin < line.check_out:
	#                    raise except_orm(_('Warning'),_('Sorry..!! The Room Is Blocked Already..'))
	#                 elif line.check_in < self.checkout <= line.check_out:
	#                    raise except_orm(_('Warning'),_('Sorry..!! The Room Is Blocked Already..'))
	
	#     reservation_line_obj = self.env['hotel.room.reservation.line']
	#     for reservation in self:
	#         self._cr.execute("select count(*) from hotel_reservation as hr "
	#                          "inner join hotel_reservation_line as hrl on \
	#                          hrl.line_id = hr.id "
	#                          "inner join hotel_reservation_line_room_rel as \
	#                          hrlrr on hrlrr.room_id = hrl.id "
	#                          "where (checkin,checkout) overlaps \
	#                          ( timestamp %s, timestamp %s ) "
	#                          "and hr.id <> cast(%s as integer) "
	#                          "and hr.state = 'confirm' "
	#                          "and hrlrr.hotel_reservation_line_id in ("
	#                          "select hrlrr.hotel_reservation_line_id \
	#                          from hotel_reservation as hr "
	#                          "inner join hotel_reservation_line as \
	#                          hrl on hrl.line_id = hr.id "
	#                          "inner join hotel_reservation_line_room_rel \
	#                          as hrlrr on hrlrr.room_id = hrl.id "
	#                          "where hr.id = cast(%s as integer) )",
	#                          (reservation.checkin, reservation.checkout,
	#                           str(reservation.id), str(reservation.id)))
	#         res = self._cr.fetchone()
	#         roomcount = res and res[0] or 0.0
	#         if roomcount:
	#             raise except_orm(_('Warning'), _('You tried to confirm \
	#             reservation with room those already reserved in this \
	#             reservation period'))
	#         else:
	#             self.write({'state': 'block'})
	#             for line_id in reservation.reservation_line:
	#                 line_id = line_id.reserved
	#                 for room_id in line_id:
	#                     vals = {
	#                         'room_id': room_id.name.id,
	#                         'check_in': reservation.checkin,
	#                         'check_out': reservation.checkout,
	#                         'state': 'assigned',
	#                         'reservation_id': reservation.id,
	#                         }
	#                     room_id.name.write({'isroom': False, 'status': 'occupied'})
	#                     reservation_line_obj.create(vals)
	
	
	#     return True
	
	@api.multi
	def open_room_booking_wizard2(self):
		self.ensure_one()
		formview_id = self.env.ref('hrms.hotel_reservation_line_form2').id
		
		return {
			'name': 'Add Rooms',
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'hotel_reservation.line',
			'view_id': formview_id,
			'target': 'new',
			'context': {'default_line_id':self.id}
		}
	
	@api.multi
	def add_category_line(self):
		self.ensure_one()
		formview_id = self.env.ref('hrms.hotel_reservation_category').id
		
		return {
			'name': 'Add Category',
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'add.category.line',
			'view_id': formview_id,
			'target': 'new',
			'context': {'default_line_id':self.id}
		}
	
	
	@api.multi
	def cancel_reservation(self):
		"""
		This method cancel recordset for hotel room reservation line
		------------------------------------------------------------------
		@param self: The object pointer
		@return: cancel record set for hotel room reservation line.
		"""
		room_res_line_obj = self.env['hotel.room.reservation.line']
		hotel_res_line_obj = self.env['hotel_reservation.line']
		self.write({'state': 'cancel'})
		room_reservation_line = room_res_line_obj.search([('reservation_id',
														   'in', self.ids)])
		room_reservation_line.unlink()
		reservation_lines = hotel_res_line_obj.search([('line_id',
														'in', self.ids)])
		for reservation_line in reservation_lines:
			reservation_line.reserve.write({'isroom': True,
											'status': 'available'})
		rooom_type_reservation = self.env['room.type.reservation'].search([('reservation_id','=',self.id)])
		rooom_type_reservation.unlink()
		return True
	
	@api.multi
	def action_confirm(self):
		for line in self:
			for liner in line.reservation_line:
				for reserv in liner.reserved:
					self.env['hotel.room.reservation.line'].sudo().create({
						'status': 'confirm',
						'state': 'assigned',
						'check_in': line.checkin,
						'check_out': line.checkout,
						'reservation_id': line.id,
						'room_id': reserv.name.id
					})
	
	@api.multi
	def action_block(self):
		for line in self:
			for liner in line.reservation_line:
				for reserv in liner.reserved:
					self.env['hotel.room.reservation.line'].sudo().create({
						'status': 'block',
						'state': 'assigned',
						'check_in': line.checkin,
						'check_out': line.checkout,
						'reservation_id': line.id,
						'room_id': reserv.name.id
					})
	
	
	@api.multi
	def send_reservation_maill(self):
		if not self.partner_id.email and not self.partner_order_id.email:
			raise except_orm(_('Error'), _('Enter the email address of Guest or Agency'))
		else:
			assert len(self._ids) == 1, 'This is for a single id at a time.'
			ir_model_data = self.env['ir.model.data']
			try:
				template_id = (ir_model_data.get_object_reference
				('hrms','email_template_hotel_reservation10')[1])
			except ValueError:
				template_id = False
			try:
				compose_form_id = (ir_model_data.get_object_reference
				('mail',
				 'email_compose_message_wizard_form')[1])
			except ValueError:
				compose_form_id = False
			ctx = dict()
			ctx.update({
				'default_model': 'hotel.reservation',
				'default_res_id': self._ids[0],
				'default_use_template': bool(template_id),
				'default_template_id': template_id,
				'default_composition_mode': 'comment',
				'force_send': True,
				'mark_so_as_sent': True
			})
			self.action_block()
			
			return {
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'mail.compose.message',
				'views': [(compose_form_id, 'form')],
				'view_id': compose_form_id,
				'target': 'new',
				'context': ctx,
				'force_send': True
			}
	
	@api.multi
	def send_acknowlegdement_maill(self):
		if not self.partner_id.email and not self.partner_order_id.email:
			raise except_orm(_('Error'), _('Enter the email address of Guest or Agency'))
		else:
			assert len(self._ids) == 1, 'This is for a single id at a time.'
			ir_model_data = self.env['ir.model.data']
			try:
				template_id = (ir_model_data.get_object_reference
				('hrms', 'email_template_hotel_reservation_acknowledgement')[1])
			except ValueError:
				template_id = False
			try:
				compose_form_id = (ir_model_data.get_object_reference
				('mail',
				 'email_compose_message_wizard_form')[1])
			except ValueError:
				compose_form_id = False
			ctx = dict()
			ctx.update({
				'default_model': 'hotel.reservation',
				'default_res_id': self._ids[0],
				'default_use_template': bool(template_id),
				'default_template_id': template_id,
				'default_composition_mode': 'comment',
				'force_send': True,
				'mark_so_as_sent': True,
				'acknowlegdement':True
			})
			self.action_confirm()
			return {
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'mail.compose.message',
				'views': [(compose_form_id, 'form')],
				'view_id': compose_form_id,
				'target': 'new',
				'context': ctx,
				'force_send': True
			}
	
	
	
	@api.multi
	def create_folio(self):
		# rec = self.env['ir.attachment'].search([('res_model','=','hotel.reservation'),('res_name','=',self.reservation_no+'...')])
		# if len(rec)==0:
		# raise except_orm(_('Warning'),_('Attachment Must Contain Atleast One File'))
		# else:
		if not self.reservation_line:
			raise except_orm(_('Error'),_('No room is selected.'))
		if self.folio_id.id != False:
			for reservation in self:
				hotel_folio_obj = self.env['hotel.folio'].browse(reservation.folio_id.id)
				room_line_object =  hotel_folio_obj.room_lines
				
				
				hotel_folio_obj.write({'room_no_list': reservation.room_no_list})
				reservation.write({'state': 'done'})
		
		if self.folio_id.id == False:
			# raise UserError("222")
			hotel_folio_obj = self.env['hotel.folio']
			room_obj = self.env['hotel.room']
			for reservation in self:
				# raise UserError(str(reservation))
				folio_lines = []
				extrabed_lines = []
				extrabed_dict = {}
				checkin_date = reservation['checkin']
				checkout_date = reservation['checkout']
				print 'self======================',self.checkin,self.checkout
				if not self.checkin <= self.checkout:
					raise except_orm(_('Error'),
									 _('Checkout date should be greater \
										 than or Equal to the Checkin date.'))
				# duration_vals = (self.onchange_check_dates
				#                  (checkin_date=checkin_date,
				#                   checkout_date=checkout_date, duration=False))
				# duration = duration_vals.get('duration') or 0.0
				duration = self.no_nights
				folio_vals = {
					'date_order': reservation.date_order,
					'warehouse_id': reservation.warehouse_id.id,
					'partner_id': reservation.partner_id.id,
					'pricelist_id': reservation.pricelist_id.id,
					'partner_invoice_id': reservation.partner_id.id,
					'partner_shipping_id': reservation.partner_id.id,
					'checkin_date': reservation.checkin,
					'checkout_date': reservation.checkout,
					'duration': duration,
					'grc_no':reservation.grc_no,
					'reservation_id': reservation.id,
					'service_lines': reservation['folio_id'],
					'is_agency' :True if reservation.guest_type == 'advance' else False,
					'travel_agency' : reservation.partner_order_id.id if reservation.guest_type == 'advance' else reservation.partner_id.id,
					#                         'advance': reservation['advance'],
					'discount': reservation['discount'],
					'grand_total': reservation['rack_rate'],
					'last_total': reservation['balance'],
					'checkout_dummy': reservation['checkout_dummy'],
					'extra_amount_bed': reservation['extra_amount_bed']*reservation.no_nights,
					'extra_amount_withoutbed': reservation['extra_amount_withoutbed']*reservation.no_nights,
					'partner_order_id': reservation.partner_order_id.id,
					'room_no_list': reservation.room_no_list
				}
				# date_a = (datetime.datetime
				#           (*time.strptime(reservation['checkout'],
				#                           DEFAULT_SERVER_DATETIME_FORMAT)[:5]))
				# date_b = (datetime.datetime
				#           (*time.strptime(reservation['checkin'],
				#                           DEFAULT_SERVER_DATETIME_FORMAT)[:5]))
				tax_extra_list = []
				for line in reservation.reservation_line:
					print "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww111",line
					for r in line.reserved:
						print "qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq111", r.name.name
						for parti in line.particulars_ids:
							if parti.particulars_id.is_room_rent:
								folio_lines.append((0, 0, {
									'checkin_date': checkin_date,
									'checkout_date': checkout_date,
									'product_id': r.name.product_id and r.name.product_id.id,
									'name': reservation['reservation_no'],
									'price_unit': parti.rate,
									'product_uom_qty': parti.number,
									 'tax_id': [(6, 0, parti.taxes_id.ids)],
									'is_reserved': True}))
							
							res_obj = room_obj.browse([r.name.id])
							res_obj.write({'status': 'occupied', 'isroom': False})
						
						
						
						
						
				# raise UserError(str(adult_total))
				
				
				# print 'tax_extra_list============================', tax_extra_list
				print "ttttttttttttttttttttttttttttttttt"
				folio_vals.update({'room_lines': folio_lines,
								   })
				# folio_vals.update({'extrabed_lines': extrabed_lines})
				# print 'test===============================1'
				folio = hotel_folio_obj.create(folio_vals)
				# print 'test===============================2'
				self._cr.execute('insert into hotel_folio_reservation_rel'
								 '(order_id, invoice_id) values (%s,%s)',
								 (reservation.id, folio.id)
								 )
				# print "ggggggggggggggggggggggggggggggggg"
				reservation.write({'state': 'done', 'folio_id': folio.id})
			
			hotel_folio_obj = self.env['hotel.folio']
			hsl_obj = self.env['hotel.service.line']
			
			for line in reservation.reservation_line:
				print
				"wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww111", line
				for parti in line.particulars_ids:
					if not parti.particulars_id.is_room_rent:
						reservation.folio_id.extrabed_lines.create({
								'folio_id2': reservation.folio_id.id,
								'checkin_date': checkin_date,
								'checkout_date': checkout_date,
								'desc': parti.particulars_id.name,
								
								'name': reservation['reservation_no'],
								'price_unit': parti.rate,
								'product_uom_qty': parti.number,
								'tax_id': [(6, 0, parti.taxes_id.ids)],
								'order_id': folio.order_id.id,
							})
			
			
			if reservation['extra_line']:
				for reservation in self:
					hotelfolio = folio
					for line2 in reservation['extra_line']:
						duration2 = 1*line2.product_uom_qty
						if line2.every_day == True:
							duration2 = duration*line2.product_uom_qty
						taxes_ids = []
						taxes_ids = [tax.id for tax in line2.taxes_id]
						values = {'folio_id': hotelfolio.id,
								  'product_id': line2.product_id.id,
								  'name': line2.product_id.name,
								  'price_unit': line2.price_unit,
								  'product_uom':line2.product_uom.id,
								  'product_uom_qty': duration2,
								  # 'tax_id': [(6, 0, taxes_ids)],
								  'every_day': line2.every_day,
								  }
					sol_rec = hsl_obj.create(values)
			
			for advance_line in reservation.advance_lines:
				advance_line.folio_id = folio.id
			
			tz = pytz.timezone('Asia/Kolkata')
			date_string = datetime.datetime.now(tz)
			format1 = '%I:%M %p'
			my_date = datetime.datetime.strftime(date_string, format1)
			self.checkin_time = my_date
		return True
	
	
	
	
	@api.multi
	def get_warning(self):
		grc_id_no = self.env['hotel.reservation'].search([], order='seq desc', limit=1)
		if not grc_id_no:
			self.seq = 1
		else:
			self.seq = grc_id_no.seq + 1
		
		if not self.reservation_line:
			raise except_orm(_('Error'),_('No Room is selected.'))
		state = ['block','confirm','done']
		for lines in self.reservation_line:
			for rooms in lines.reserved:
				room_id = rooms.name.id
				room = self.env['hotel.room.reservation.line'].search([('room_id','=',room_id),('status','in',state)])
				for line in room:
					if line.check_in <= self.checkin <= line.check_out and line.reservation_id.id != self.id:
						raise except_orm(_('Warning'),_('Sorry..!! The Room Is Blocked Already..'))
					elif line.check_in <= self.checkout <= line.check_out and line.reservation_id.id != self.id:
						raise except_orm(_('Warning'),_('Sorry..!! The Room Is Blocked Already..'))
				
				reservation_line_obj = self.env['hotel.room.reservation.line']
				for reservation in self:
					self._cr.execute("select count(*) from hotel_reservation as hr "
									 "inner join hotel_reservation_line as hrl on \
									 hrl.line_id = hr.id "
									 "inner join hotel_reservation_line_room_rel as \
									 hrlrr on hrlrr.room_id = hrl.id "
									 "where (checkin,checkout) overlaps \
									 ( timestamp %s, timestamp %s ) "
									 "and hr.id <> cast(%s as integer) "
									 "and hr.state = 'confirm' "
									 "and hrlrr.hotel_reservation_line_id in ("
									 "select hrlrr.hotel_reservation_line_id \
									 from hotel_reservation as hr "
									 "inner join hotel_reservation_line as \
									 hrl on hrl.line_id = hr.id "
									 "inner join hotel_reservation_line_room_rel \
									 as hrlrr on hrlrr.room_id = hrl.id "
									 "where hr.id = cast(%s as integer) )",
									 (reservation.checkin, reservation.checkout,
									  str(reservation.id), str(reservation.id)))
					res = self._cr.fetchone()
					roomcount = res and res[0] or 0.0
					if roomcount:
						raise except_orm(_('Warning'), _('You tried to confirm \
							reservation with room those already reserved in this \
							reservation period'))
					else:
						room_reserved = self.env['hotel.room.reservation.line'].search([('room_id','=',room_id),('status','in',state),('reservation_id','=',self.id)])
						# self.write({'state': 'block'})
						if room_reserved:
							for room_reser in room_reserved:
								room_reser.status = 'done'
						
						else:
							for line_id in reservation.reservation_line:
								line_id = line_id.reserved
								for room_id in line_id:
									vals = {
										'room_id': room_id.name.id,
										'check_in': reservation.checkin,
										'check_out': reservation.checkout,
										'state': 'assigned',
										'reservation_id': reservation.id,
									}
									room_id.name.write({'isroom': False, 'status': 'occupied'})
									reservation_line_obj.create(vals)
		self.create_folio()
		rec = self.env['ir.attachment'].search([('res_model','=','hotel.reservation'),('res_name','=',self.reservation_no+'...')])
		if len(rec) == 0:
			return {
				'name': 'Warning Message',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'warning.attachment',
				'view_id': self.env.ref('hrms.view_warning_message_form').id,
				'target': 'new',
				'type': 'ir.actions.act_window',
				'context': {}
			}
		return True
	# raise except_orm(_('Warning'),_('Attachment Must Contain Atleast One File'))
	
	
	@api.multi
	def change_room(self):
		"""
		This method cancel recordset for hotel room reservation line and set to draft
		------------------------------------------------------------------
		@param self: The object pointer
		@return: cancel record set for hotel room reservation line.
		"""
		for line in self:
			if line.state != 'cancel':
				line.cancel_reservation()
		
		
		return True
	
	@api.multi
	def get_menu_item_category(self):
		menu_card_type = self.env['hotel.menucard.type'].search([('id','!=',False)])
		recordset = menu_card_type.sorted(key=lambda r: r.name)
		return recordset
	
	@api.multi
	def get_menu_items(self, category):
		menu_card = self.env['hotel.menucard'].search([('active','=',True),('item_type_id','=',category)])
		recordset = menu_card.sorted(key=lambda r: r.name)
		return recordset



class AddCategory(models.Model):
	_name = 'add.category.line'
	
	line_id = fields.Many2one('hotel.reservation')
	rate = fields.Float('Rate')
	category_id = fields.Many2one('hotel.room.type','Category',required=True)
	avail_rooms = fields.Integer(readonly=True,string='Available Rooms')
	selected_rooms = fields.Integer(required=True)
	tax_ids = fields.Many2many('account.tax','add_category_tax_id_room_rel','category_id','tax_id',string="Tax")
	adult = fields.Float('Adult')
	capacity = fields.Float('Capacity')
	child = fields.Float('Child')
	room_id = fields.Many2one('hotel_reservation.line','Select Room')
	
	
	
	@api.model
	def create(self, vals):
		result = super(AddCategory, self).create(vals)
		if result.selected_rooms == 0:
			raise except_orm(_('Warning.....!'), _('Must Enter Selected Rooms.'))
		vacant_rooms = 0
		assigned = 0
		for lines in result.category_id.reservation_ids:
			if result.line_id.checkin >= lines.check_in and result.line_id.checkin <= lines.check_out:
				if lines.status == 'assigned':
					assigned += lines.nos
		
		result.avail_rooms = result.category_id.room_no - assigned
		result.capacity = result.category_id.capacity
		return result
	
	@api.onchange('category_id')
	def onchange_category_id(self):
		if self.category_id:
			# print 'test=====================1'
			vacant_rooms = 0
			assigned = 0
			for lines in self.category_id.reservation_ids:
				if self.line_id.checkin >= lines.check_in and self.line_id.checkin <= lines.check_out:
					if lines.status == 'assigned':
						assigned += lines.nos
			
			self.tax_ids = [(6, 0, [i.id for i in self.category_id.tax_ids])]
			self.capacity = self.category_id.capacity
			self.rate = self.category_id.rate
			# tax = self.env['tax.mapping'].search([])
			# for val in tax:
			# 	if val.price_from <= self.category_id.rate and val.price_to >= self.category_id.rate:
			# 		self.tax_ids = [(6, 0, [i.id for i in val.tax_id])]
			
			self.avail_rooms = self.category_id.room_no - assigned
	
	
	@api.onchange('rate')
	def onchange_rate(self):
		if self.rate:
			# print 'test=====================2'
			tax = self.env['tax.mapping'].search([])
			for val in tax:
				
				if val.price_from <= self.rate and val.price_to >= self.rate:
					# print 'test==================================3', val.tax_id
					self.tax_ids = False
					self.tax_ids = [(6, 0, [i.id for i in val.tax_id])]
	
	@api.onchange('selected_rooms')
	def onchange_selected_rooms(self):
		if self.selected_rooms:
			if self.selected_rooms > self.avail_rooms:
				self.selected_rooms = 0
				return {
					'warning': {
						'title': 'Warning',
						'message': "No such category room avaliable in the days."
					}
				}



class WarningAttachment(models.Model):
	_name = 'warning.attachment'
	
	message = fields.Text(default="Attachment Must Contain Atleast One File",readonly=True)
	
	@api.multi
	def warning_ok(self):
		return True


class extra_service_line(models.Model):
	_name = 'extra.service.line'
	_description = 'Extra Service Line'
	
	
	@api.onchange('product_id')
	def onchange_product(self):
		if self.product_id:
			self.price_unit = self.product_id.uom_id.id
			self.price_unit = self.product_id.lst_price
			self.product_uom_qty = 1
			self.product_uom = self.product_id.uom_id.id
			self.taxes_id = self.product_id.taxes_id
	
	@api.multi
	@api.depends('product_id','price_unit','product_uom_qty','taxes_id','complimentary')
	def _compute_subtotal(self):
		for service in self:
			tax_ex = 0
			tax_in = 0
			amt_ex = 0
			amt_in = 0
			for tax_id in service.taxes_id:
				if tax_id.price_include == False:
					tax_ex += service.price_unit * tax_id.amount
					amt_ex += service.price_unit
				else:
					tax_in += service.price_unit - (service.price_unit/(1+tax_id.amount))
					amt_in += service.price_unit - tax_in
			if service.complimentary == True:
				service.price_subtotal = 0.0
			else:
				service.price_subtotal = service.price_unit*service.product_uom_qty
				
				service.tax_amount = (tax_ex+tax_in)*service.product_uom_qty
				service.amt_without_tax = (amt_ex+amt_in)*service.product_uom_qty
	
	
	
	amt_without_tax = fields.Float('Amount withot tax', compute="_compute_subtotal")
	#    _coloums = {
	line_id_extra = fields.Many2one('hotel.reservation', 'Order Reference' )
	#    line_id_extra_folio = fields.Many2one('hotel.folio', 'Order Reference' )
	name = fields.Text('Description')
	product_id = fields.Many2one('product.product', 'Product', domain=[('is_hotel_service','=',True)])
	price_unit = fields.Float('Unit Price')
	price_subtotal = fields.Float(compute='_compute_subtotal', string='Subtotal')
	product_uom_qty = fields.Float('Quantity', digits_compute= dp.get_precision('Product UoS'), required=True, readonly=True, states={'draft': [('readonly', False)]})
	product_uom = fields.Many2one('product.uom', 'Unit of Measure ', )
	product_uos_qty = fields.Float('Quantity (UoS)' ,digits_compute= dp.get_precision('Product UoS'), readonly=True, states={'draft': [('readonly', False)]})
	product_uos = fields.Many2one('product.uom', 'Product UoS')
	every_day = fields.Boolean('Everyday', help="Please Check for the daily service")
	complimentary = fields.Boolean('Complimentary')
	taxes_id = fields.Many2many('account.tax', 'service_taxes_rel',
								'service_id', 'tax_id', 'Taxes',
								domain=[('parent_id','=',False),('type_tax_use','in',['sale','all'])])
	tax_amount = fields.Float(compute='_compute_subtotal', string='Tax Amount')
	state = fields.Selection([
		('draft', 'Draft Quotation'),
		('sent', 'Quotation Sent'),
		('cancel', 'Cancelled'),
		('waiting_date', 'Waiting Schedule'),
		('progress', 'Sales Order'),
		('manual', 'Sale to Invoice'),
		('shipping_except', 'Shipping Exception'),
		('invoice_except', 'Invoice Exception'),
		('done', 'Done'),
	])
	_defaults = {
		'state': 'draft'
	}







class hotel_services(models.Model):
	_inherit = 'hotel.services'
	
	line_id_reservation = fields.Many2one('hotel.reservation')
	company_id = fields.Many2one('res.company', 'Company', required=True)
	
	_defaults = {
		'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
	}




class HotelMenucard(models.Model):
	_inherit = 'hotel.menucard'
	
	item_type_id = fields.Many2one('hotel.menucard.type' , 'Category')
	item_code = fields.Char('Item Code')


class Hotel_Room(models.Model):
	_inherit = 'hotel.room'
	
	@api.onchange('categ_id')
	def onchange_categ(self):
		if self.categ_id:
			self.extra_adult = self.categ_id.extra_adult
			self.extra_child = self.categ_id.extra_child
			self.list_price = self.categ_id.rate
		# self.taxes_id = [i.id for i in self.categ_id.tax_ids]
	
	discount = fields.Float('Advance', size=64, default=0.0)
	company_id = fields.Many2one('res.company', 'Company', required=True)
	extra_adult = fields.Float('Extra Adult Rate')
	extra_child = fields.Float('Extra Children Rate')
	
	
	_defaults = {
		'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
	}
	
	
	
	@api.model
	def create(self,vals):
		uom_obj = self.env['product.uom']
		vals.update({'type':'service','room_status2': True})
		uom_rec = uom_obj.search([('name', 'ilike', 'Hour(s)')], limit=1)
		if uom_rec:
			vals.update({'uom_id': uom_rec.id, 'uom_po_id': uom_rec.id})
		rec = super(Hotel_Room, self).create(vals)
		self.env['hotel.room.new'].create({'name':rec.id})
		if rec.capacity == 0:
			raise except_orm(_('Warning...!'), _('Please Enter Capacity.'))
		return rec

class sale_order(models.Model):
	_inherit = 'sale.order'
	
	advance = fields.Float('Advance', size=64, default=0.0)
	service = fields.Float('Service Charge', size=64, default=0.0)


class invoice_date_line(models.Model):
	_name = 'invoice.date.line'
	_description = 'invoice date line'
	#    _coloums = {
	line_id_date = fields.Many2one('account.invoice', 'Date Wise Entry' )
	date_service = fields.Date('Dates')


class account_invoice_line(models.Model):
	_inherit = 'account.invoice.line'
	
	@api.one
	@api.depends('price_unit','quantity')
	def _compute_amount_amount(self):
		self.amount_amount = self.quantity * self.price_unit
	
	
	@api.one
	@api.depends('cgst','price_subtotal','sgst','igst')
	def _compute_amount_with_tax(self):
		self.amount_with_tax = self.cgst + self.sgst + self.igst + self.price_subtotal
	
	
	@api.one
	@api.depends('price_subtotal')
	def _compute_amount_tax_included(self):
		gst = 0
		igst = 0
		for tax in self.invoice_line_tax_id:
			if tax.tax_based == 'gst':
				gst += tax.amount
			if tax.tax_based == 'igst':
				igst += tax.amount
		gst_total = gst * self.price_subtotal
		self.sgst = self.cgst = gst_total/2
		self.igst = igst * self.price_subtotal
	
	
	# @api.multi
	# def _compute_amount_tax_included(self):
	#     for line in self:
	#         tax = 0
	#         included = False
	#         for lines in line.invoice_line_tax_id:
	#             tax += lines.amount
	#             if lines.price_include == True:
	#                 included = True
	#         line.amount_with_tax = (1 + tax)*line.price_unit*line.quantity
	#         line.sgst = tax*line.price_subtotal/2
	#         line.cgst = tax*line.price_subtotal/2
	#         if included == True:
	#             line.amount_with_tax = line.price_unit*line.quantity
	
	
	
	
	date_service = fields.Date('Date of Service')
	sac_no = fields.Char('SAC')
	sgst = fields.Float(compute='_compute_amount_tax_included', string='SGST')
	cgst = fields.Float(compute='_compute_amount_tax_included', string='CGST')
	igst = fields.Float(string='IGST',compute='_compute_amount_tax_included')
	amount_with_tax = fields.Float(string='Taxable Value',compute='_compute_amount_with_tax')
	every_day = fields.Boolean('Per Day', help="Please Check for the daily service")
	amount_amount = fields.Float('Amount',compute="_compute_amount_amount")
	tax_id = fields.Many2one('account.tax', string='Tax')
	
	_defaults = {
		'date_service': date.today(),
	}

	@api.model
	def create(self, vals):
		if 'invoice_line_tax_id' in vals:
			for tax_id in vals['invoice_line_tax_id'][0][2]:
				tax = self.env['account.tax'].browse(tax_id)
				if tax.tax_based == 'gst' or tax.tax_based == 'igst':
					vals['tax_id'] = tax.id
		return super(account_invoice_line, self).create(vals)

	# @api.multi
	# def write(self, vals):
	#
	# 	if not self.tax_id:
	# 		for tax_id in self.invoice_line_tax_id:
	# 			if tax_id.tax_based == 'gst' or tax_id.tax_based == 'igst':
	# 				vals['tax_id'] = tax_id.id
	# 	return super(account_invoice_line, self).write(vals)


class minus_bill_line(models.Model):
	_name = 'minus.bill.line'
	
	name = fields.Char(string='Description', required=True)
	reference = fields.Char(string='Reference', required=True)
	price_subtotal = fields.Float(string='Amount', digits= dp.get_precision('Account'),
								  store=True)
	line_bill_minus = fields.Many2one('account.invoice', string='Bill Minus')

class account_invoice(models.Model):
	_inherit = 'account.invoice'
	
	
	def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
		res = models.Model.fields_view_get(self, cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
		if view_type == 'form':
			doc = etree.XML(res['arch'])
			for sheet in doc.xpath("//sheet"):
				parent = sheet.getparent()
				index = parent.index(sheet)
				for child in sheet:
					parent.insert(index, child)
					index += 1
				parent.remove(sheet)
			res['arch'] = etree.tostring(doc)
		return res
	
	
	
	@api.multi
	def delete_invoice(self):
		moves = self.env['account.move']
		for inv in self:
			if inv.move_id:
				moves += inv.move_id
			#                 for move in moves:
			#                     self.env['account.voucher'].search([('id','')])
			if inv.payment_ids:
				for move_line in inv.payment_ids:
					voucher = self.env['account.voucher'].search([('move_id','=',move_line.move_id.id)])
					voucher.cancel_voucher()
		#                     if move_line.reconcile_partial_id.line_partial_ids:
		#                         raise except_orm(_('Error!'), _('You cannot cancel an invoice which is partially paid. You need to unreconcile related payment entries first.'))
		
		# First, set the invoices as cancelled and detach the move ids
		self.write({'state': 'cancel', 'move_id': False})
		if moves:
			# second, invalidate the move(s)
			moves.button_cancel()
			# delete the move this invoice was pointing to
			# Note that the corresponding move_lines and move_reconciles
			# will be automatically deleted too
			moves.unlink()
		self._log_event(-1.0, 'Cancel Invoice')
		
		folio = self.env['hotel.folio'].search([('id','=', self.folio_id.id)])
		reservation = self.env['hotel.reservation'].search([('id','=', self.folio_id.reservation_id.id)])
		# resturant = self.env['hotel.restaurant.order'].seatch([('')])
		restaurant = self.env['hotel.restaurant.order'].search([('folio_id','=',self.folio_id.id)])
		print 'test==================1'
		for rest in restaurant:
			rest.action_cancel(True)
			rest.unlink()
		service = self.env['service.invoice'].search([('folio_id','=',self.folio_id.id)])
		for serv in service:
			serv.action_cancel(True)
			serv.unlink()
		print 'test==================2'
		folio.unlink()
		print 'test==================3'
		reservation.cancel_reservation()
		reservation.set_to_draft_reservation()
		reservation.unlink()
		self.unlink()
		
		return True
	
	@api.multi
	def get_id(self):
		list = []
		list.append(self.partner_id.id)
		list.append(self.traval_agent_id.id)
		return list
	
	
	@api.multi
	def invoice_validate_new(self):
		self.state = 'open'
		# self.action_number()
		self.action_date_assign()
		
		account_invoice_tax = self.env['account.invoice.tax']
		account_move = self.env['account.move']
		
		for inv in self:
			if not inv.journal_id.sequence_id:
				raise except_orm(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
			if not inv.invoice_line:
				raise except_orm(_('No Invoice Lines!'), _('Please create some invoice lines.'))
			if inv.move_id:
				print ' move id=================================='
				continue
			
			ctx = dict(self._context, lang=inv.partner_id.lang)
			
			company_currency = inv.company_id.currency_id
			if not inv.date_invoice:
				# FORWARD-PORT UP TO SAAS-6
				if inv.currency_id != company_currency and inv.tax_line:
					raise except_orm(
						_('Warning!'),
						_('No invoice date!'
						  '\nThe invoice currency is not the same than the company currency.'
						  ' An invoice date is required to determine the exchange rate to apply. Do not forget to update the taxes!'
						  )
					)
				inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
			date_invoice = inv.date_invoice
			
			# create the analytical lines, one move line per invoice line
			iml = inv._get_analytic_lines()
			# check if taxes are all computed
			compute_taxes = account_invoice_tax.compute(inv.with_context(lang=inv.partner_id.lang))
			inv.check_tax_lines(compute_taxes)
			
			# I disabled the check_total feature
			if self.env.user.has_group('account.group_supplier_inv_check_total'):
				if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding / 2.0):
					raise except_orm(_('Bad Total!'), _('Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))
			
			if inv.payment_term:
				total_fixed = total_percent = 0
				for line in inv.payment_term.line_ids:
					if line.value == 'fixed':
						total_fixed += line.value_amount
					if line.value == 'procent':
						total_percent += line.value_amount
				total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
				if (total_fixed + total_percent) > 100:
					raise except_orm(_('Error!'), _("Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))
			
			# Force recomputation of tax_amount, since the rate potentially changed between creation
			# and validation of the invoice
			inv._recompute_tax_amount()
			# one move line per tax line
			iml += account_invoice_tax.move_line_get(inv.id)
			
			if inv.type in ('in_invoice', 'in_refund'):
				ref = inv.reference
			else:
				ref = inv.number
			
			diff_currency = inv.currency_id != company_currency
			# create one move line for the total and possibly adjust the other lines amount
			total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, ref, iml)
			
			name = inv.supplier_invoice_number or inv.name or '/'
			totlines = []
			if inv.payment_term:
				totlines = inv.with_context(ctx).payment_term.compute(total, date_invoice)[0]
			if totlines:
				res_amount_currency = total_currency
				ctx['date'] = date_invoice
				for i, t in enumerate(totlines):
					if inv.currency_id != company_currency:
						amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
					else:
						amount_currency = False
					
					# last line: add the diff
					res_amount_currency -= amount_currency or 0
					if i + 1 == len(totlines):
						amount_currency += res_amount_currency
					
					iml.append({
						'type': 'dest',
						'name': name,
						'price': t[1],
						'account_id': inv.account_id.id,
						'date_maturity': t[0],
						'amount_currency': diff_currency and amount_currency,
						'currency_id': diff_currency and inv.currency_id.id,
						'ref': ref,
					})
			else:
				iml.append({
					'type': 'dest',
					'name': name,
					'price': total,
					'account_id': inv.account_id.id,
					'date_maturity': inv.date_due,
					'amount_currency': diff_currency and total_currency,
					'currency_id': diff_currency and inv.currency_id.id,
					'ref': ref
				})
			
			date = date_invoice
			
			part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
			agent_account = inv.traval_agent_id.property_account_receivable.id or inv.agent_id.property_account_receivable.id
			if not agent_account:
				raise osv.except_osv(('Error'), ('No Travel agencey/Travel agency account found'));
			# newcode
			line = [(0,0,{
				'account_id': inv.journal_id.default_debit_account_id.id,
				'name': inv.number2,
				'debit': inv.amount_total,
				'credit': 0,
				# 'move_id': move_id.id,
				'invoice_id':inv.id,
			}),(0,0,{
				'account_id': inv.traval_agent_id.property_account_receivable.id or inv.agent_id.property_account_receivable.id,
				'name': inv.number2,
				'debit': 0,
				'credit': inv.amount_total,
				# 'move_id': move_id.id,
				'invoice_id': inv.id,
				'partner_id': inv.partner_id.id,
			})]
			
			
			
			journal = inv.journal_id.with_context(ctx)
			if journal.centralisation:
				raise except_orm(_('User Error!'),
								 _('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))
			
			# line = inv.finalize_invoice_move_lines(line)
			# print 'line===================',line
			# print 'ashvjm',hjfvj
			
			move_vals = {
				'ref': inv.reference or inv.name,
				'line_id': line,
				'journal_id': journal.id,
				'date': inv.date_invoice,
				'narration': inv.comment,
				'company_id': inv.company_id.id,
			}
			ctx['company_id'] = inv.company_id.id
			period = inv.period_id
			if not period:
				period = period.with_context(ctx).find(date_invoice)[:1]
			if period:
				move_vals['period_id'] = period.id
				for i in line:
					i[2]['period_id'] = period.id
			
			ctx['invoice'] = inv
			ctx_nolang = ctx.copy()
			ctx_nolang.pop('lang', None)
			move = account_move.with_context(ctx_nolang).create(move_vals)
			
			# make the invoice point to that move
			vals = {
				'move_id': move.id,
				'period_id': period.id,
				'move_name': move.name,
			}
			inv.with_context(ctx).write(vals)
			# Pass invoice in context in method post: used if you want to get the same
			# account move reference when creating the same invoice after a cancelled one:
			move.post()
		self._log_event()
		return True
	
	
	
	
	@api.multi
	def _get_analytic_lines(self):
		account = False
		""" Return a list of dict for creating analytic lines for self[0] """
		company_currency = self.company_id.currency_id
		sign = 1 if self.type in ('out_invoice', 'in_refund') else -1
		
		iml = self.env['account.invoice.line'].move_line_get(self.id)
		# print "imlmain============================", iml
		for il in iml:
			if il['account_analytic_id']:
				if self.type in ('in_invoice', 'in_refund'):
					ref = self.reference
				else:
					ref = self.number
				if not self.journal_id.analytic_journal_id:
					raise except_orm(_('No Analytic Journal!'),
									 _("You have to define an analytic journal on the '%s' journal!") % (self.journal_id.name,))
				currency = self.currency_id.with_context(date=self.date_invoice)
				il['analytic_lines'] = [(0,0, {
					'name': il['name'],
					'date': self.date_invoice,
					'account_id': il['account_analytic_id'],
					'unit_amount': il['quantity'],
					'amount': currency.compute(il['price'], company_currency) * sign,
					'product_id': il['product_id'],
					'product_uom_id': il['uos_id'],
					'general_account_id': il['account_id'],
					'journal_id': self.journal_id.analytic_journal_id.id,
					'ref': ref,
				})]
				print "il['product_id'] ===========", il['product_id']
		return iml
	
	
	@api.one
	@api.depends(
		'move_id.line_id.reconcile_id.line_id',
		'move_id.line_id.reconcile_partial_id.line_partial_ids',
	)
	def _compute_payments(self):
		self.ensure_one()
		move_lines = self.env['account.move.line'].search([('invoice_id','=', self.id)])
		if self.reservation_id.id != False:
			move_lines = self.env['account.move.line'].search([('reserv_id','=', self.reservation_id.id)])
			move_lines |= move_lines
		self.payment_ids = move_lines
		self._paid_amount()
		
		move_lines = self.env['account.move.line'].search(['|',('reserv_id','=', self.reservation_id.id),('invoice_id','=', self.id)])
		for move_line_id in move_lines:
			if move_line_id.reserv_id:
				self.payment_ids = self.payment_ids +  move_line_id
	
	@api.multi
	@api.depends('invoice_line')
	def get_tax_amount(self):
		for records in self:
			cgst = 0
			igst = 0
			sgst = 0
			for lines in records.invoice_line:
				cgst += lines.cgst
				sgst += lines.sgst
				igst += lines.igst
			records.cgst = cgst
			records.sgst = sgst
			records.igst = igst
	
	
	@api.multi
	@api.depends('bill_minus','amount_total')
	def _compute_after_reduction(self):
		for lines in self:
			for line in lines.bill_minus:
				lines.amount_after_reduction = lines.amount_total - line.price_subtotal
	
	@api.one
	@api.depends('invoice_line.price_subtotal', 'tax_line.amount', 'discount','round_off')
	def _compute_amount(self):
		self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line)
		self.amount_tax = sum(line.amount for line in self.tax_line)
		self.amount_total = self.amount_untaxed + self.amount_tax + self.service - self.discount + self.round_off
	
	@api.multi
	@api.depends('amount_total','payment_total')
	def _compute_residual(self):
		self.residual = 0.0
		self.residual = self.amount_total - self.payment_total
	
	@api.multi
	@api.depends('seq')
	def compute_no(self):
		for rec in self:
			if rec.type == 'out_invoice':
				rec.number2 = 'A/'+str(rec.seq)
	
	@api.model
	def create(self,vals):
			previous_invoice_number = self.env['account.invoice'].search([], order='seq desc', limit=1).number2.split('/')
			number = self.env['ir.sequence'].get('account.invoice')
			res = self.env['account.invoice'].search([], order='seq desc', limit=1)
			if not res:
				vals['number2'] = number
				vals['seq'] = 1
			else:
				last_index = int(res.number2.split('/')[2])+1
				index = number.split('/')
				vals['number2'] = index[0] + "/" + index[1] + "/" + str(last_index)
				vals['seq'] = res.seq + 1
			res = super(account_invoice, self).create(vals)
			for rec in res.invoice_line:
				for tax in rec.invoice_line_tax_id:
					if tax.tax_based == 'gst' or tax.tax_based == 'igst':
						res.tax_id = tax
			return res
	
	
	payment_ids = fields.One2many('account.move.line', 'invoice_id', string='Payments')
	advance = fields.Float('Advance', size=64, default=0.0)
	service = fields.Float('Service Charge', size=64, default=0.0)
	date_line = fields.One2many('invoice.date.line', 'line_id_date',
								'Extras',
								help='Extras')
	checkin_date = fields.Date('Check in Date')
	checkout_date = fields.Date('Check out Date')
	balance = fields.Float('Balance', size=64, default=0.0)
	bill_no = fields.Char('Bill No', size=64)
	folio_id = fields.Many2one('hotel.folio', string='Folio No')
	reservation_id = fields.Many2one('hotel.reservation', related='folio_id.reservation_id', string='Reservation No')
	is_reduce = fields.Boolean('Reduced', readonly="True")
	bill_minus = fields.One2many('minus.bill.line', 'line_bill_minus', 'Bill Minus')
	amount_after_reduction = fields.Float(compute='_compute_after_reduction', store=True, string='Amount After Reduction')
	room_no_list = fields.Char('Rooms')
	customer_id = fields.Many2one('res.partner', 'Customer2')
	traval_agent_id = fields.Many2one(related='folio_id.reservation_id.partner_order_id', store=True, string='Travel Agency')
	agent_id =fields.Many2one('res.partner',string="Agent from KOT")
	# from_kot = fields.Boolean(string="From KOT")
	discount = fields.Float('Discount')
	invoice_report = fields.Selection([
		('all','All'),
		('separate','Separate')
	], string="Report Format", default="all")
	
	cgst = fields.Float(compute="get_tax_amount",string="CGST")
	sgst = fields.Float(compute="get_tax_amount",string="SGST")
	igst = fields.Float(compute="get_tax_amount",string="IGST")
	residual = fields.Float(string='Balance', digits=dp.get_precision('Account'),
							compute='_compute_residual', store=True,
							help="Remaining amount due.")
	round_off = fields.Float('Round Off Amount')
	amount_untaxed = fields.Float(string='Subtotal', digits=dp.get_precision('Account'),
								  store=True, readonly=True, compute='_compute_amount', track_visibility='always')
	amount_tax = fields.Float(string='Tax', digits=dp.get_precision('Account'),
							  store=True, readonly=True, compute='_compute_amount')
	amount_total = fields.Float(string='Total', digits=dp.get_precision('Account'),
								store=True, readonly=True, compute='_compute_amount')
	purchase_bill_no = fields.Char('Bill No.')
	grc_no = fields.Char('GRC No:')
	number2 = fields.Char(string="Invoice No.")
	seq = fields.Integer('Sequence')
	_defaults = {
		'checkin_date': date.today(),
		'checkout_date': date.today()
	}
	b2b = fields.Boolean(string='BTOB')
	b2c = fields.Boolean(string='BTOC', default=True)
	inter_state = fields.Boolean(string='Interstate')
	local = fields.Boolean(string='kerala',default=True)

	@api.onchange('b2c')
	def b2c_boolean(self):
		if self.b2c:
			self.b2b = False
			self.inter_state = False
			self.local = False

	@api.onchange('b2b')
	def b2b_boolean(self):
		if self.b2b:
			self.b2c = False
			self.inter_state = False
			self.local = False

	@api.onchange('inter_state')
	def inter_state_boolean(self):
		if self.inter_state:
			self.local = False

	@api.onchange('local')
	def local_boolean(self):
		if self.local:
			self.inter_state = False

	@api.multi
	def invoice_print(self):
		view_ref = self.env['ir.model.data'].get_object_reference('hrms', 'hotel_invoice_wizard_selection')
		view_id = view_ref[1] if view_ref else False
		res = {
			'type': 'ir.actions.act_window',
			'name': _('Report Format'),
			'res_model': 'wizard.selection',
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': view_id,
			'target': 'new',
			'context': {'default_name':self.id}
		}
		
		return res
	
	
	@api.multi
	def date_ranches(self):
		self.ensure_one()
		recordset = []
		date_format = "%Y-%m-%d"
		if self.checkin_date and self.checkout_date:
			start_date = self.checkin_date
			end_date = self.checkout_date
			start_date2 = datetime.datetime.strptime(self.checkin_date, date_format)
			end_date2 = datetime.datetime.strptime(self.checkout_date, date_format)
			diff = (end_date2 - start_date2).days
			recordset = [(start_date2 + datetime.timedelta(days=x)).strftime("%d-%m-%Y") for x in range(0, diff+1)]
			return recordset
		else:
			recordset = [(datetime.datetime.strptime(self.date_invoice, date_format)).strftime("%d-%m-%Y")]
		return recordset
	
	@api.multi
	def get_invoice_lines(self,date):
		date_format = "%d-%m-%Y"
		date_format2 = "%Y-%m-%d"
		self.ensure_one()
		invoice = self.env['account.invoice.line']
		
		invoice_linerecs1 = invoice.search([('invoice_id','=',self.id)])
		printrecs1 = self.env['print.list']
		printrecs2 = self.env['print.list']
		printrecs3 = self.env['print.list']
		printrecs4 = self.env['print.list']
		
		if self.checkout_date:
			end_date2 = (datetime.datetime.strptime(self.checkout_date, date_format2)).strftime("%d-%m-%Y")
			values3 = {}
			if date < end_date2:
				for lines1 in invoice_linerecs1:
					amount = 0.0
					amount_without_tax = 0.0
					cgst = 0.0
					sgst = 0.0
					if lines1.product_id.isroom == True:
						amount = lines1.price_unit
						amount_without_tax = lines1.price_subtotal/lines1.quantity
						cgst = (amount - amount_without_tax)/2
						sgst = (amount - amount_without_tax)/2
						values3 = {'name':lines1.product_id.name,
								   'amount': amount,
								   'amount_without_tax': amount_without_tax,
								   'cgst':cgst,
								   'sgst':sgst }
						if values3 != {}:
							printrecs1 = printrecs1 | self.env['print.list'].create(values3)
					if lines1.name == "Amount for Without Bed" or lines1.name == "Amount for Extra Bed":
						amount = lines1.price_unit
						amount_without_tax = lines1.price_subtotal/lines1.quantity
						cgst = (amount - amount_without_tax)/2
						sgst = (amount - amount_without_tax)/2
						values3 = {'name':lines1.name,
								   'amount': amount,
								   'amount_without_tax': amount_without_tax,
								   'cgst':cgst,
								   'sgst':sgst }
						if values3 != {}:
							printrecs1 = printrecs1 | self.env['print.list'].create(values3)
		
		invoice_linerecs = invoice.search([('invoice_id','=',self.id),('date_service','=',datetime.datetime.strptime(date,date_format))])
		amount2 = 0.0
		amount_without_tax2 = 0.0
		cgst2 = 0.0
		sgst2 = 0.0
		amount3 = 0.0
		amount_without_tax3 = 0.0
		cgst3 = 0.0
		sgst3 = 0.0
		values1 = {}
		values2 = {}
		values4 = {}
		
		for lines in invoice_linerecs:
			if lines.product_id.ismenucard == True:
				amount2 += lines.price_unit*lines.quantity
				amount_without_tax2 += lines.price_subtotal
				cgst2 += (amount2 - amount_without_tax2)/2
				sgst2 += (amount2 - amount_without_tax2)/2
				values1 = {'name':'Restaurant Bill',
						   'amount': amount2,
						   'amount_without_tax': amount_without_tax2,
						   'cgst':cgst2,
						   'sgst':sgst2 }
			if lines.product_id.is_laundry == True:
				amount3 += lines.price_unit*lines.quantity
				amount_without_tax3 += lines.price_subtotal
				cgst3 += (amount3 - amount_without_tax3)/2
				sgst3 += (amount3 - amount_without_tax3)/2
				values2 = {'name':'Laundry',
						   'amount': amount3,
						   'amount_without_tax': amount_without_tax3,
						   'cgst':cgst3,
						   'sgst':sgst3}
			if lines.product_id.type == 'service' and lines.product_id.is_laundry == False and lines.product_id.isroom != True:
				amount4 = lines.price_unit*lines.quantity
				amount_without_tax4 = lines.price_subtotal
				cgst4 = (amount4 - amount_without_tax4)/2
				sgst4 = (amount4 - amount_without_tax4)/2
				values4 = {'name':lines.product_id.name,
						   'amount': amount4,
						   'amount_without_tax': amount_without_tax4,
						   'cgst':cgst4,
						   'sgst':sgst4 }
				if values4 != {}:
					printrecs4 = self.env['print.list'].create(values4)
		if values1 != {}:
			printrecs2 = self.env['print.list'].create(values1)
		if values2 != {}:
			printrecs3 = self.env['print.list'].create(values2)
		printrecs = printrecs1 | printrecs2 | printrecs3 | printrecs4
		return printrecs
	
	
	
	
	@api.multi
	def _convert_nn(self, val):
		"""convert a value < 100 to English.
		"""
		if val < 20:
			return to_19[val]
		for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens)):
			if dval + 10 > val:
				if val % 10:
					return dcap + '-' + to_19[val % 10]
				return dcap
	@api.multi
	def _convert_nnn(self, val):
		"""
			convert a value < 1000 to english, special cased because it is the level that kicks
			off the < 100 special case.  The rest are more general.  This also allows you to
			get strings in the form of 'forty-five hundred' if called directly.
		"""
		word = ''
		(mod, rem) = (val % 100, val // 100)
		if rem > 0:
			word = to_19[rem] + ' Hundred'
			if mod > 0:
				word += ' '
		if mod > 0:
			word += self._convert_nn(mod)
		return word
	
	@api.multi
	def english_number(self, val):
		if val < 100:
			return self._convert_nn(val)
		if val < 1000:
			return self._convert_nnn(val)
		for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom))):
			if dval > val:
				mod = 1000 ** didx
				l = val // mod
				r = val - (l * mod)
				ret = self._convert_nnn(l) + ' ' + denom[didx]
				if r > 0:
					ret = ret + ', ' + self.english_number(r)
				return ret
	
	@api.multi
	def amount_to_text(self, number, currency):
		number = '%.2f' % number
		units_name = currency
		list = str(number).split('.')
		start_word = self.english_number(int(list[0]))
		end_word = self.english_number(int(list[1]))
		cents_number = int(list[1])
		cents_name = (cents_number > 1) and 'Paise' or 'Paise'
		
		return ' '.join(filter(None, [start_word, units_name, (start_word or units_name) and (end_word or cents_name) and 'and', end_word, cents_name]))
	
	
	@api.multi
	def get_restaurant_bill(self):
		rec = self.env['hotel.restaurant.order'].search([('folio_id','=',self.folio_id.id),('state','=','credited')])
		return rec
	
	@api.multi
	def get_service_bill(self):
		rec = self.env['service.invoice'].search([('folio_id','=',self.folio_id.id),('state','=','credited')])
		return rec
	
	@api.multi
	def get_advance_lines(self):
		rec = self.env['service.invoice'].search([('folio_id','=',self.folio_id.id),('state','=','credited')])
		return rec
	
	@api.multi
	def get_payment_mode(self):
		mode = ""
		for lines in self.payment_ids:
			if lines.journal_id.name not in mode:
				mode = mode+" "+lines.journal_id.name
		return mode
	
	@api.multi
	def action_invoice_sent(self):
		""" Open a window to compose an email, with the edi invoice template
			message loaded by default
		"""
		assert len(self) == 1, 'This option should only be used for a single id at a time.'
		template = self.env.ref('hrms.email_template_edi_invoice5', False)
		compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
		ctx = dict(
			default_model='account.invoice',
			default_res_id=self.id,
			default_use_template=bool(template),
			default_template_id=template.id,
			default_composition_mode='comment',
			mark_invoice_as_sent=True,
		)
		return {
			'name': _('Compose Email'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'views': [(compose_form.id, 'form')],
			'view_id': compose_form.id,
			'target': 'new',
			'context': ctx,
		}
	
	
	@api.multi
	def invoice_pay_customer(self):
		#         if not ids: return []
		dummy, view_id = self.env['ir.model.data'].get_object_reference('account_voucher', 'view_vendor_receipt_dialog_form')
		
		return {
			'name':_("Pay Invoice"),
			'view_mode': 'form',
			'view_id': view_id,
			'view_type': 'form',
			'res_model': 'account.voucher',
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'new',
			'domain': '[]',
			'context': {
				'payment_expected_currency': self.currency_id.id,
				'partner_id': self.env['res.partner']._find_accounting_partner(self.partner_id).id,
				'default_amount': self.type in ('out_refund', 'in_refund') and -self.residual or self.residual,
				'default_reference': self.name,
				'close_after_process': True,
				'invoice_type': self.type,
				'invoice_id': self.id,
				'default_invoice_id': self.id,
				'default_type': self.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
				'type': self.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
			}
		}
	
	@api.multi
	def get_tax_amounts(self):
		taxes_ids = []
		for line in self.invoice_line:
			for tax in line.invoice_line_tax_id:
				if tax.id not in taxes_ids:
					taxes_ids.append(tax.id)
		list = []
		for tax in taxes_ids:
			# sgst += lines.sgst
			# cgst += lines.cgst
			sgst = 0.0
			cgst = 0.0
			lines = self.env['account.invoice.line'].search([('invoice_id','=',self.id),('invoice_line_tax_id','in',tax)])
			for line in lines:
				sgst += line.sgst
				cgst += line.cgst
			list.append({'name': 'SGST Collection' + ' ' + '@' + str(int((self.env['account.tax'].search([('id','=',tax)]).amount*100)/2)) +' '+ '%', 'amount': sgst})
			list.append({'name': 'CGST Collection' + ' ' + '@' + str(int((self.env['account.tax'].search([('id','=',tax)]).amount*100)/2)) +' '+ '%', 'amount': cgst})
		return list
	
	@api.multi
	def get_separate_tax_amounts(self,page_no):
		print 'page_no==================-----------------------------------', page_no
		taxes_ids = []
		for line in self.invoice_line:
			if page_no == 1:
				if line.product_id.room_status2 == True:
					for tax in line.invoice_line_tax_id:
						if tax.id not in taxes_ids:
							taxes_ids.append(tax.id)
			elif page_no == 2:
				if line.product_id.ismenucard == True:
					for tax in line.invoice_line_tax_id:
						if tax.id not in taxes_ids:
							taxes_ids.append(tax.id)
			else:
				if line.product_id.is_hotel_service == True:
					for tax in line.invoice_line_tax_id:
						if tax.id not in taxes_ids:
							taxes_ids.append(tax.id)
		list = []
		for tax in taxes_ids:
			# sgst += lines.sgst
			# cgst += lines.cgst
			sgst = 0.0
			cgst = 0.0
			lines = self.env['account.invoice.line'].search([('invoice_id','=',self.id),('invoice_line_tax_id','in',tax)])
			for line in lines:
				sgst += line.sgst
				cgst += line.cgst
			list.append({'name': 'SGST Collection' + ' ' + '@' + str(float((self.env['account.tax'].search([('id','=',tax)]).amount*100)/2)) +' '+ '%', 'amount': sgst})
			list.append({'name': 'CGST Collection' + ' ' + '@' + str(float((self.env['account.tax'].search([('id','=',tax)]).amount*100)/2)) +' '+ '%', 'amount': cgst})
		return list
	
	@api.multi
	def get_advances(self):
		taxes_ids = []
		advance = 0
		for line in self.folio_id.advance_lines:
			advance += line.amt_without_tax
			if line.taxes_id.id not in taxes_ids:
				taxes_ids.append(line.taxes_id.id)
		list = []
		list.append({'name': 'Booking Advance', 'amount': advance})
		for tax in taxes_ids:
			sgst = 0.0
			cgst = 0.0
			lines = self.env['reservation.advance'].search([('folio_id','=',self.folio_id.id),('taxes_id','=',tax)])
			for line in lines:
				sgst += line.tax_amount/2
				cgst += line.tax_amount/2
			list.append({'name': 'SGST Collection' + ' ' + '@' + str(int((self.env['account.tax'].search([('id','=',tax)]).amount*100)/2)) +' '+ '%', 'amount': sgst})
			list.append({'name': 'CGST Collection' + ' ' + '@' + str(int((self.env['account.tax'].search([('id','=',tax)]).amount*100)/2)) +' '+ '%', 'amount': cgst})
		return list
	
	
	@api.multi
	def get_date(self):
		date_list = []
		d1 = datetime.datetime.strptime(self.checkin_date, '%Y-%m-%d')
		d2 = datetime.datetime.strptime(self.checkout_date, '%Y-%m-%d')
		dates_btwn = d1
		while dates_btwn <= d2:
			datee = dates_btwn.date()
			date_list.append({
				'date': datee,
			})
			dates_btwn = dates_btwn + timedelta(days=1)
		return date_list
	
	@api.multi
	def get_tariff(self):
		for line in self:
			tariff = 0.0
			for lines in self.invoice_line:
				if lines.product_id.room_status2 == True:
					tariff += lines.price_subtotal
		return tariff
	
	@api.multi
	def get_payment_mode(self):
		for line in self:
			modes = ''
			vouchers = self.env['account.voucher'].search([('invoice_id','=',line.id)])
			temp = 0
			for lines in vouchers:
				if temp == 0:
					modes += lines.journal_id.name
					temp = 1
				else:
					modes += ',' + lines.journal_id.name
		return modes
	
	
	@api.multi
	def get_print_invoice_details(self,date,page_no=0):
		
		list = []
		room_ids = []
		menu_ids = []
		service_ids = []
		room_taxes_ids = []
		menu_taxes_ids = []
		service_taxes_ids = []
		room_rate = 0
		service_rate = 0
		rest_rate = 0
		
		d1 = datetime.datetime.strptime(self.checkin_date, '%Y-%m-%d')
		d2 = datetime.datetime.strptime(self.checkout_date, '%Y-%m-%d')
		count = abs((d2 - d1).days)
		
		for line in self.invoice_line:
			if line.product_id.room_status2 == True:
				room_ids.append(line.id)
			if line.product_id.ismenucard == True:
				menu_ids.append(line.id)
			if line.product_id.is_hotel_service == True:
				service_ids.append(line.id)
		if page_no == 1 or page_no == 0:
			invoice_lines1 = self.env['account.invoice.line'].search([('id','in',room_ids),('invoice_id','=', self.id)])
			
			if date != datetime.datetime.strptime(self.checkout_date, '%Y-%m-%d').date():
				
				for line in invoice_lines1:
					room_rate += line.price_subtotal/count
				list.append({'name':'Room Rent','amt':room_rate, 'qty':0, 'rate':0})
				
				sgst = 0.0
				cgst = 0.0
				for line in invoice_lines1:
					# for tax in line.invoice_line_tax_id:
					#     if tax.id not in room_taxes_ids:
					#         room_taxes_ids.append(tax.id)
					# for tax in room_taxes_ids:
					# lines = self.env['account.invoice.line'].search([('invoice_id','=',self.id),('invoice_line_tax_id','in',tax)])
					# for line in lines:
					sgst += line.sgst
					cgst += line.cgst
				# list.append({'name': 'Room SGST Collection' + ' ' + '@' + str(int((self.env['account.tax'].search([('id','=',tax)]).amount*100)/2)) +' '+ '%', 'amt': sgst/count})
				list.append({'name': 'Room SGST Collection' + ' ' + '@' + str((line.invoice_line_tax_id.amount*100)/2) +' '+ '%', 'amt': sgst/count, 'qty':0, 'rate':0})
				# list.append({'name': 'Room CGST Collection' + ' ' + '@' + str(int((self.env['account.tax'].search([('id','=',tax)]).amount*100)/2)) +' '+ '%', 'amt': cgst/count})
				list.append({'name': 'Room CGST Collection' + ' ' + '@' + str((line.invoice_line_tax_id.amount*100)/2) +' '+ '%', 'amt': cgst/count, 'qty':0, 'rate':0})
		
		
		if page_no == 2 or page_no == 0:
			invoice_lines2 = self.env['account.invoice.line'].search([('id','in',menu_ids),('invoice_id','=', self.id),('date_service','=', date)])
			if len(invoice_lines2) > 0:
				for line in invoice_lines2:
					if date == datetime.datetime.strptime(line.date_service, '%Y-%m-%d').date():
						rest_rate += line.price_subtotal
				list.append({'name':'Restaurant Bill','amt':rest_rate, 'qty':0, 'rate':0})
				
				sgst = 0.0
				cgst = 0.0
				for line in invoice_lines2:
					sgst += line.sgst
					cgst += line.cgst
				# list.append({'name': 'Restaurant SGST Collection' + ' ' + '@' + str((self.env['account.tax'].search([('id','=',tax)]).amount*100)/2) +' '+ '%', 'amt': sgst/count})
				list.append({'name': 'Restaurant SGST Collection' + ' ' + '@' + str((line.invoice_line_tax_id.amount*100)/2) +' '+ '%', 'amt': sgst, 'qty':0, 'rate':0})
				# list.append({'name': 'Restaurant CGST Collection' + ' ' + '@' + str((self.env['account.tax'].search([('id','=',tax)]).amount*100)/2) +' '+ '%', 'amt': cgst/count})
				list.append({'name': 'Restaurant CGST Collection' + ' ' + '@' + str((line.invoice_line_tax_id.amount*100)/2) +' '+ '%', 'amt': cgst, 'qty':0, 'rate':0})
		
		
		if page_no == 3 or page_no == 0:
			sgst = 0.0
			cgst = 0.0
			
			invoice_lines4 = self.env['account.invoice.line'].search([('id','in',service_ids),('invoice_id','=', self.id)])
			
			if date != datetime.datetime.strptime(self.checkout_date, '%Y-%m-%d').date():
				
				for line in invoice_lines4:
					if line.every_day == True:
						list.append({'name': line.product_id.name,'amt':line.price_subtotal/count, 'qty':0, 'rate':0})
						sgst += line.sgst/count
						cgst += line.cgst/count
					# for tax in line.invoice_line_tax_id:
					#     if tax.id not in room_taxes_ids:
					#         room_taxes_ids.append(tax.id)
					# for tax in room_taxes_ids:
					#     lines = self.env['account.invoice.line'].search([('invoice_id','=',self.id),('invoice_line_tax_id','in',tax)])
					#     for line in lines:
			
			invoice_lines3 = self.env['account.invoice.line'].search([('id','in',service_ids),('invoice_id','=', self.id),('date_service','=', date)])
			if len(invoice_lines3) > 0:
				
				for line in invoice_lines3:
					if line.every_day != True:
						sgst += line.sgst
						cgst += line.cgst
						list.append({'name':line.product_id.name,'amt':line.price_subtotal, 'qty':line.quantity, 'rate': line.price_subtotal/line.quantity})
			# list.append({'name': 'Restaurant SGST Collection' + ' ' + '@' + str((self.env['account.tax'].search([('id','=',tax)]).amount*100)/2) +' '+ '%', 'amt': sgst/count})
			if sgst != 0.0:
				list.append({'name': 'SGST Collection' + ' ' + '@' + str((line.invoice_line_tax_id.amount*100)/2) +' '+ '%', 'amt': sgst, 'qty':0, 'rate':0})
			# list.append({'name': 'Restaurant CGST Collection' + ' ' + '@' + str((self.env['account.tax'].search([('id','=',tax)]).amount*100)/2) +' '+ '%', 'amt': cgst/count})
			if cgst != 0.0:
				list.append({'name': 'CGST Collection' + ' ' + '@' + str((line.invoice_line_tax_id.amount*100)/2) +' '+ '%', 'amt': cgst, 'qty':0, 'rate':0})
		
		
		return list
	
	@api.multi
	def unlink(self):
		for invoice in self:
			
			up = self.env['account.invoice'].search([('seq','>',invoice.seq)], order='seq desc')
			if up:
				for line in up:
					line.seq -= 1
			invoice.internal_number = False
			if invoice.state not in ('draft', 'cancel'):
				pass
			# raise Warning(_('You cannot delete an invoice which is not draft or cancelled. You should refund it instead.'))
			
			elif invoice.internal_number:
				pass
			# raise Warning(_('You cannot delete an invoice after it has been validated (and received a number).  You can set it back to "Draft" state and modify its content, then re-confirm it.'))
		return super(account_invoice, self).unlink()
	
	@api.multi
	def write(self, vals):
		if vals.get('grc_no'):
			if self.folio_id:
				self.folio_id.grc_no = vals.get('grc_no')
		return super(account_invoice, self).write(vals)



class AccountTax(models.Model):
	_inherit = 'account.tax'
	
	
	@api.multi
	@api.depends('tax_type')
	def compute_tax_amount(self):
		for rec in self:
			if rec.tax_type == '1':
				rec.amount = 0.01
			if rec.tax_type == '2':
				rec.amount = 0.02
			if rec.tax_type == '5':
				rec.amount = 0.05
			if rec.tax_type == '12':
				rec.amount = 0.12
			if rec.tax_type == '18':
				rec.amount = 0.18
			if rec.tax_type == '28':
				rec.amount = 0.28
	
	
	tax_based = fields.Selection([('gst','GST Based'),('igst','IGST Based'),('other','Other')],string="Tax Based On")
	
	tax_type = fields.Selection([('1','1 %'),
								 ('2','2 %'),
								 ('5','5 %'),
								 ('12','12 %'),
								 ('18','18 %'),
								 ('28','28 %')], 'Tax Type')
	
	
	amount = fields.Float(compute='compute_tax_amount', string='Amount', store=True, readonly=True)



class WizardSelection(models.Model):
	_name = 'wizard.selection'
	
	name = fields.Many2one('account.invoice')
	category_id = fields.Selection([('room_bill','Room Bill'),('food_bill','Food Bill'),('all_bill','All')],string="Report Format",required=True)
	
	@api.multi
	def get_food_bill(self,folio_id):
		if folio_id:
			records = self.env['hotel.restaurant.order'].search([('folio_id','=',folio_id.id)], order='o_date_new')
			# for record in records
			if records:
				list = []
				for rec in records:
					
					date = datetime.datetime.strptime(rec.o_date_new,'%Y-%m-%d %H:%M:%S')
					
					
					
					dict = {}
					food_time = str(rec.food_time)+str(" : ") + str(date.date())
					dict['foodtime'] = food_time
					list.append(dict)
					sl_no = 1
					for line in rec.order_list:
						dict = {}
						# print "recordset=====================", rec.order_list,sl_no
						dict['sl_no'] = sl_no
						dict['foodtime'] = False
						dict['name'] = line.name.name
						dict['uom'] = line.name.product_id.uom_id.name
						dict['qty'] = line.item_qty
						dict['item_rate'] = line.item_rate
						dict['amount'] = line.amount
						dict['discount'] = line.discount
						dict['taxable_value'] = line.price_subtotal
						dict['cgst'] = line.cgst
						dict['sgst'] = line.sgst
						dict['igst'] = line.igst
						dict['total_amount'] = line.total_amount
						sl_no += 1
						# print "dict====================", dict
						list.append(dict)
				# print 'liest===========================', list
				return list
			else:
				raise osv.except_osv(_('Error'),_('There is no restaurant bills related to this invoice'))
	
	
	
	
	
	
	@api.multi
	def get_bank_name(self,bank, flag):
		if bank:
			first_rec = bank.search([],limit=1)
			if flag == 0:
				return first_rec.bank_name
			if flag == 1:
				return first_rec.bank.street
			if flag == 2:
				return first_rec.acc_number
			if flag == 3:
				return first_rec.bank_bic
	
	@api.multi
	def get_room_nos(self):
		for line in self.name.invoice_line:
			room_no = ''
			if line.product_id.room_status2 == True:
				room_no += ' ' + line.product_id.name
			return room_no
	
	
	
	
	@api.multi
	def print_report(self):
		# print 'self==================', self._ids
		datas = {
			'ids': self._ids,
			'model': self._name,
			'form': self.read(),
			'context':self._context,
		}
		
		if self.category_id == 'room_bill':
			return{
				'name' : 'Print',
				'type' : 'ir.actions.report.xml',
				'report_name' : 'hrms.report_room_bill_print22',
				'datas': datas,
				'report_type': 'qweb-pdf'
			}
		if self.category_id == 'food_bill':
			return{
				'name' : 'Print',
				'type' : 'ir.actions.report.xml',
				'report_name' : 'hrms.report_food_bill_print',
				'datas': datas,
				'report_type': 'qweb-pdf'
			}
		
		
		if self.category_id == 'all_bill':
			return{
				'name' : 'Print',
				'type' : 'ir.actions.report.xml',
				'report_name' : 'hrms.report_all_bill_print',
				'datas': datas,
				'report_type': 'qweb-pdf'
			}
	
	@api.multi
	def view_report(self):
		datas = {
			'ids': self._ids,
			'model': self._name,
			'form': self.read(),
			'context':self._context,
		}
		
		if self.category_id == 'room_bill':
			return{
				'name' : 'Print',
				'type' : 'ir.actions.report.xml',
				'report_name' : 'hrms.report_room_bill_print22',
				'datas': datas,
				'report_type': 'qweb-html'
			}
		
		if self.category_id == 'food_bill':
			return{
				'name' : 'Print',
				'type' : 'ir.actions.report.xml',
				'report_name' : 'hrms.report_food_bill_print',
				'datas': datas,
				'report_type': 'qweb-html'
			}
		
		if self.category_id == 'all_bill':
			return{
				'name' : 'Print',
				'type' : 'ir.actions.report.xml',
				'report_name' : 'hrms.report_all_bill_print',
				'datas': datas,
				'report_type': 'qweb-html'
			}
	
	
	
	@api.multi
	def get_resturant_bills(self):
		records = self.env['hotel.restaurant.order'].search([('folio_id','=',self.name.folio_id.id)], order='o_date_new')
		# print 'invoice==================', self.name,records,asd
		return records

class print_list(models.Model):
	_name = "print.list"
	
	name = fields.Char('Description')
	rate = fields.Float('Rate')
	cgst = fields.Float('CGST')
	sgst = fields.Float('SGST')
	amount_without_tax = fields.Float('Amount Without Tax')
	amount = fields.Float('Amount')
#     line_id = fields



class HotelRestaurantOrder(models.Model):
	_inherit = 'hotel.restaurant.order'
	_order = "o_date desc, id desc"
	
	
	agent_id = fields.Many2one('res.partner', string='Agency')
	kot_number = fields.Char(string="Kitchen Order Ticket Number")
	
	
	@api.multi
	@api.onchange('room_no')
	def _from_room_no(self):
		DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
		for record in self:
			if not record.room_no:
				room_ids = []
				reservations = self.env['hotel.room.reservation.line'].search([('status','=','done')])
				room_ids = [reserve.room_id.product_id.id for reserve in reservations]
				return {
					'domain': {
						'room_no':[('id','=', room_ids)]
					}
				}
			if record.room_no:
				record.cname=False
				record.folio_id = False
				reserve_id = False
				room =self.env['hotel.room'].search([('product_id','=',record.room_no.id)])
				if room:
					for val in room.room_reservation_line_ids:
						if val.status == 'done':
							date_field1 = datetime.datetime.strptime(val.check_in, "%Y-%m-%d")
							date_field2 = datetime.datetime.strptime(val.check_out, "%Y-%m-%d")
							check_in = date_field1.strftime("%Y-%m-%d")
							check_out = date_field2.strftime("%Y-%m-%d")
							# if self.o_date ==
							if self.o_date >= check_in and self.o_date <= check_out:
								reserve_id = val.reservation_id
					if reserve_id:
						record.folio_id = reserve_id.folio_id.id
						record.cname= reserve_id.folio_id.partner_id.id
					else:
						raise except_orm(_('Error'),_('There is no any guest in this specified room for this specified date'))
					
	
	
	
	@api.onchange('folio_id')
	def get_folio_id(self):
		'''
		When you change folio_id, based on that it will update
		the cname and room_number as well
		---------------------------------------------------------
		@param self: object pointer
		'''
		for rec in self:
			self.cname = False
			# self.room_no = False
			if rec.folio_id:
				self.cname = rec.folio_id.partner_id.id
				# self.ml_plan = rec.folio_id.reservation_id.ml_plan
				# if rec.folio_id.room_lines:
				# 	# self.room_no = rec.folio_id.room_lines[0].product_id.id
	            #             return {'domain': {'room_no': [('id', '=', rec.folio_id.room_lines[0].product_id.id)]}}
				#
	@api.multi
	@api.depends('discount_percent')
	def _compute_kot_discount(self):
		for record in self:
			record.discount_amt = (record.subtotal*record.discount_percent)/100
	
	@api.one
	@api.depends('order_list','cgst','sgst','igst')
	def _compute_amount(self):
		
		for line in self:
			print "aaaaaaaaaaaaaaaaaaa"
			subtotal = 0
			combo_subtotal = 0
			print "line.sgst"
			for lines in line.order_list:
				if lines.complimentary == False:
					subtotal += lines.price_subtotal
				else:
					combo_subtotal += lines.price_subtotal
			
			# line.amount_subtotal = sum(line2.price_subtotal for line2
			#                            in line.order_list)
			# tax = 0
			# included = False
			# for lines in line.taxes_id:
			#     tax += lines.amount
			#     if lines.price_include == True:
			#         included = True
			# if included == True and line.amount_subtotal:
			#     line.subtotal = line.amount_subtotal
			#     line.amount_subtotal = line.subtotal/(1+tax)
			# amount_tax = line.amount_subtotal*(tax)
			# line.amount_tax = float(str(round(amount_tax, 2)))
			# line.cgst = line.amount_tax/2
			# line.sgst = line.amount_tax/2
			# if included != True:
			#     line.subtotal = round(line.amount_subtotal + line.amount_tax + line.serv)
			line.subtotal = subtotal
			line.combo_subtotal = combo_subtotal
			line.combo_total = round(combo_subtotal + line.combo_cgst + line.combo_sgst + line.combo_igst)
			line.amount_total = round(subtotal + line.cgst + line.sgst + line.igst)
		# if line.amount_total != 0:
		#     line.coinage = line.amount_total + line.discount_amt - line.subtotal
	@api.multi
	@api.depends('amount_subtotal','serv','amount_tax','taxes_id')
	def _total(self):
		'''
		amount_total will display on change of amount_subtotal
		-------------------------------------------------------
		@param self: object pointer
		'''
		for line in self:
			included = False
			for lines in line.taxes_id:
				if lines.price_include == True:
					included = True
			if included != True:
				# print 'test=========================='
				line.amount_total = round(line.amount_subtotal + line.amount_tax + line.serv)
	#             line.serv = line.amount_subtotal*(line.serv/100)
	
	#         restaurant_line_tax_id = fields.Many2many('account.tax',
	#                                                   'restaurant_line_tax', 'restaurant_line_id', 'tax_id',
	#                                                   string='Taxes', domain=[('parent_id', '=', False), '|', ('active', '=', False), ('active', '=', True)])
	#         price_subtotal = fields.Float(string='Amount without Tax', digits= dp.get_precision('Account'),
	#                                       store=True, readonly=True, compute='_compute_price')
	
	
	READONLY_STATES = {
		'cancel': [('readonly', True)],
		'payed': [('readonly', True)],
		'credited': [('readonly', True)],
		'nc': [('readonly', True)],
	}
	
	@api.multi
	def _get_tax_line(self):
		for lines in self:
			cgst = sgst = igst = combo_cgst = combo_sgst = combo_igst = 0
			for vals in lines.order_list:
				if vals.complimentary == False:
					cgst += vals.cgst
					sgst += vals.sgst
					igst += vals.igst
				else:
					combo_cgst += vals.cgst
					combo_sgst += vals.sgst
					combo_igst += vals.igst
			lines.cgst = cgst
			lines.sgst = sgst
			lines.igst = igst
			lines.combo_cgst = combo_cgst
			lines.combo_sgst = combo_sgst
			lines.combo_igst = combo_igst
	
	@api.multi
	@api.depends('seq')
	def comute_name(self):
		for rec in self:
			# rec.order_no = 'OR/'+str(rec.seq)
			rec.bill_no = 'B/'+str(rec.seq)
	
	
	
	amount_tax = fields.Float(string='Tax', compute='_compute_amount', store=True,)
	# cgst = fields.Float(string='CGST', readonly=True, compute='_compute_amount')
	# sgst = fields.Float(string='SGST', readonly=True, compute='_compute_amount')
	coinage = fields.Float(string='Coinage', readonly=True, compute='_compute_amount', store=True)
	amount_total = fields.Float(compute='_compute_amount', method=True, store=True,
								digits= dp.get_precision('Account'), string='Total')
	amount_subtotal = fields.Float(compute='_compute_amount', method=True, store=True,
								   string='Subtotal')
	subtotal = fields.Float(compute='_compute_amount', method=True, store=True,
							string='Subtotal')
	account_id = fields.Many2one('account.account', 'Account')
	journal_id = fields.Many2one('account.journal', 'Journal')
	serv = fields.Float('Service Charge', size=64, default=0.0)
	tax = fields.Float('Tax (%) ', default=12)

	sl_no = fields.Char('Sl No', size=64)
	ml_plan = fields.Selection([('Breakfast', 'Breakfast'),
								('Lunch', 'Lunch'),
								('Dinner', 'Dinner')], 'Meal Plan')
	state = fields.Selection([('draft', 'Draft'), ('order', 'Order Created'),
							  ('done', 'Done'), ('cancel', 'Cancelled'),
							  ('payed', 'Paid'),('credited', 'Credited'),
							  ('nc', 'Non Chargable')],
							 'State', select=True, required=True,
							 readonly=True, default=lambda * a: 'draft')
	o_date = fields.Date('Order Date', required=True,
						 default=(lambda *a:
								  time.strftime
								  (DEFAULT_SERVER_DATETIME_FORMAT)))
	
	discount_percent = fields.Float('Discount%')
	o_date_new = fields.Datetime('Order Date', required=True,
								 default=(lambda *a:
										  time.strftime
										  (DEFAULT_SERVER_DATETIME_FORMAT)), states=READONLY_STATES)
	cgst = fields.Float('CGST',compute="_get_tax_line")
	sgst = fields.Float('SGST',compute="_get_tax_line")
	igst = fields.Float('IGST',compute="_get_tax_line")
	
	# o_date_new1 = fields.Datetime('Order Date', required=True,
	#                      default=(lambda *a:
	#                               time.strftime
	#                               (DEFAULT_SERVER_DATETIME_FORMAT)), compute='_get_correct_time')
	discount_amt = fields.Float('Discount Amount', compute='_compute_kot_discount')
	remarks = fields.Text('Remarks')
	food_time = fields.Selection([('Morning','Morning'),('Lunch','Lunch'),('Dinner','Dinner'),('Other','Other')],string="Food Time", states=READONLY_STATES)
	company_id = fields.Many2one('res.company', 'Company')
	tax_id_type = fields.Many2one('account.tax','Tax')
	tax_id = fields.Many2one('account.tax',"Tax")
	seq = fields.Integer('Sequence')
	order_no = fields.Char( string='Order Number')
	bill_no = fields.Char(compute='comute_name', string='Bill No')
	
	combo_subtotal = fields.Float(compute='_compute_amount', method=True, store=True,
								  string='Combo Subtotal')
	combo_cgst = fields.Float('Combo CGST',compute="_get_tax_line")
	combo_sgst = fields.Float('Combo SGST',compute="_get_tax_line")
	combo_igst = fields.Float('Combo IGST',compute="_get_tax_line")
	combo_total = fields.Float(compute='_compute_amount', method=True, store=True,
							   digits= dp.get_precision('Account'), string='Combo Total')
	
	_defaults = {
		'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'account.account', context=c),
	}
	
	@api.multi
	def _get_correct_time(self):
		for record in self:
			DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
			date_field1 = datetime.datetime.strptime(record.o_date_new, DATETIME_FORMAT)
			
			# date_field2 = datetime.strptime(record.o_date_new1, DATETIME_FORMAT)
			date_field2 = date_field1 + timedelta(hours=5,minutes=30)
	
	@api.onchange('o_date_new')
	def onchange_date_order(self):
		self.o_date = dateutil.parser.parse(self.o_date_new).date()
	
	@api.model
	def default_get(self, default_fields):
		vals = super(HotelRestaurantOrder, self).default_get(default_fields)
		taxes_ids=[]
		taxes_ids = [self.env.user.company_id.restaurant_tax_id.id]
		vals['tax_id'] = self.env.user.company_id.restaurant_tax_id.id

		return vals
	# @api.model
	# def create(self, vals):
	# 	# vals['bill_no'
	# 	#  ] = self.pool['ir.sequence'].get(cr, uid, 'hotel.restaurant.order.bill')
	# 	# vals['sl_no'] = self.pool['ir.sequence'].get(cr, uid, 'hotel.restaurant.order.bill.slno')
	# 	order = self.env['hotel.restaurant.order'].search([], order='seq desc', limit=1)
	# 	# print 'order======================', order.seq, asd
	# 	if not order:
	# 		vals['seq'] = 1
	# 	else:
	# 		vals['seq'] = order.seq + 1
	# 	result = super(HotelRestaurantOrder, self).create(vals)
	# 	# print 'resut==============', result
	# 	# object = self.pool.get('hotel.restaurant.order').browse()
	# 	result.generate_kot()
	# 	result.done_order_kot()
	# 	return result
	
	@api.multi
	def unlink(self):
		for rec in self:
			up = self.env['hotel.restaurant.order'].search([('seq','>',rec.seq)], order='seq desc')
			if up:
				for line in up:
					line.seq -= 1
		result = super(HotelRestaurantOrder, self).unlink()
	
	
	@api.multi
	def done_order_kot(self):
		"""
		This method is used to change the state
		to Done of the hotel restaurant order
		----------------------------------------
		@param self: object pointer
		"""
		self.write({'state': 'done'})
		return True
	
	@api.multi
	def markas_non_chargable(self):
		for line in self:
			self.write({'state': 'nc'})
			return True
	
	@api.multi
	def done_payed(self):
		
		
		invoice_line_obj = self.env['account.invoice.line']
		invoice_no = 0
		invoice_obj = self.env['account.invoice']
		so_line_obj = self.env['sale.order.line']
		
		
		account_account_obj = self.env['account.account']
		account_journal_obj = self.env['account.journal']
		account_move_line_obj = self.env['account.move.line']
		# print '===================================o',self.agent_id.id
		# print 'dhbv',asdk
		
		
		for order_obj in self:
			amount_total=order_obj.amount_subtotal+order_obj.serv
			values2 = {   'reference': order_obj.order_no,
						  'internal_number': order_obj.bill_no,
						  'customer_id': order_obj.cname.id,
						  'partner_id': order_obj.cname.id,
						  'agent_id': order_obj.agent_id.id,
						  'origin': order_obj.order_no,
						  'service': order_obj.serv,
						  # 'from_kot':True,
						  'account_id': order_obj.cname.property_account_receivable.id,
						  'date_invoice': date.today().strftime('%Y-%m-%d'),
						  'date_due': date.today().strftime('%Y-%m-%d'),
						  }
			# print 'values2=============================',values2
			acc_id=invoice_obj.create(values2)
			print '==============================',acc_id
			invoice_no = acc_id.id
			sub_total=0.0
			price_total = 0
			included = False
			tax1 = 0
			for lines in order_obj.tax_id:
				tax1 += lines.amount
				if lines.price_include == True:
					included = True
			if included == True:
				price_total = order_obj.amount_total
			if included == False:
				price_total = (order_obj.amount_total)/(1+tax1)
			
			product_id = self.env['product.product'].search([('name','=','Restaurant Bill')])
			if len(product_id) < 1:
				product_id = self.env['product.product'].create({'name':'Restaurant Bill','ismenucard':True})
			if len(product_id) >= 1:
				product_id = self.env['product.product'].search([('name','=','Restaurant Bill')])[0]
				product_id.write({'ismenucard':True})
			
			taxes_ids = []
			taxes_ids = [tax.id for tax in order_obj.tax_id]
			values1 = {   'origin': order_obj.order_no,
						  'partner_id': order_obj.cname.id,
						  'name': order_obj.bill_no,
						  'product_id': product_id.id,
						  'account_id': self.env['ir.property'].get('property_account_income_categ', 'product.category').id,
						  'quantity': 1,
						  'price_unit': price_total,
						  'price_subtotal': price_total,
						  'invoice_id': acc_id.id,
						  'date_service':order_obj.o_date,
						  'invoice_line_tax_id': [(6, 0, taxes_ids)],
						  #                                     'invoice_line_tax_id': [(6, 0, order_obj.restaurant_line_tax_id.id)]
						  }
			sub_total = price_total
			sol_rec = invoice_line_obj.create(values1)
			
			# amount_total = order_obj.amount_subtotal + order_obj.serv
			amount_total = order_obj.amount_total
			
			balance = amount_total
			
			invoice_obj2 = self.env['account.invoice'].browse(acc_id.id)
			invoice_obj2.write({ 'residual': balance,'amount_total': amount_total,'number': order_obj.bill_no,'amount_tax': order_obj.serv})
			
			if self.agent_id:
				
				order_obj.ensure_one()
				# Search for record belonging to the current staff
				record =  self.env['account.invoice'].search([('id','=',invoice_obj2.id)])
				
				context = self._context.copy()
				#context['default_name'] = self.id
				if record:
					res_id = record[0].id
				else:
					res_id = False
				# Return action to open the form view
				view_id = self.env['ir.model.data'].get_object_reference('hrms', 'inherite_invoice_form1')
				return {
					'name':'Invoice',
					'view_type': 'form',
					'view_mode':'form',
					'view_id':False,
					'views' : [(view_id[1] or False, 'form')],
					'res_model':'account.invoice',
					'type':'ir.actions.act_window',
					'res_id':res_id,
					'context':context,
				}
			
			
			invoice_obj2.action_date_assign()
			invoice_obj2.action_move_create()
			invoice_obj2.action_number()
			invoice_obj2.invoice_validate()
		
		move_lines=account_move_line_obj.search([('name','=',order_obj.order_no)])
		
		self.write({'state': 'payed'})
		wizard = self.env['account.invoice'].search([('id','=',invoice_no)])
		if wizard:
			return wizard.invoice_pay_customer()
	# return {
	#     'name': _('Register Payment'),
	#     'view_type': 'form',
	#     'view_mode': 'form',
	#     'res_model': 'account.voucher',
	#     'res_id': PosOrder.ids[0],
	#     'view_id': False,
	#     'context': self.env.context,
	#     'type': 'ir.actions.act_window',
	#     'target': 'current',
	# }
	
	@api.multi
	def done_credited(self):
		"""
		This method is used to change the state
		to Credited of the hotel restaurant order
		----------------------------------------
		@param self: object pointer
		"""
		hotel_folio_obj = self.env['hotel.folio']
		hsl_obj = self.env['hotel.service.line']
		so_line_obj = self.env['sale.order.line']
		
		
		for order_obj in self:
			hotelfolio = order_obj.folio_id.order_id.id
			folio_obj=order_obj.folio_id
			sub_total=folio_obj.grand_total
			last_total=folio_obj.last_total
			service_charge=folio_obj.service_charge
			if order_obj.folio_id:
				price_total = 0
				included = False
				tax1 = 0
				for lines in order_obj.tax_id:
					tax1 += lines.amount
					if lines.price_include == True:
						included = True
				if included == True:
					price_total = order_obj.amount_total
				if included == False:
					price_total = (order_obj.amount_total)/(1+tax1)
				
				product_id = self.env['product.product'].search([('name','=','Restaurant Bill')])
				if len(product_id) < 1:
					product_id = self.env['product.product'].create({'name':'Restaurant Bill','ismenucard':True})
				if len(product_id) >= 1:
					product_id = self.env['product.product'].search([('name','=','Restaurant Bill')])[0]
					product_id.write({'ismenucard':True})
				
				taxes_ids = []
				taxes_ids = [tax.id for tax in order_obj.tax_id]
				values = {'order_id': hotelfolio,
						  'name': order_obj.bill_no,
						  'product_id': product_id.id,
						  'product_uom_qty': 1,
						  'price_unit': price_total,
						  'price_sub_total': price_total,
						  'tax_id': [(6, 0, taxes_ids)],
						  }
				
				sub_total = price_total
				last_total = price_total
				
				sol_rec = so_line_obj.create(values)
				hsl_obj.create({'folio_id': order_obj.folio_id.id,
								'service_line_id': sol_rec.id,
								'date_order':order_obj.o_date})
				
				
				if order_obj.combo_total > 0:
					product_id = self.env['product.product'].search([('name','=','Combo Meal')])
					if not product_id:
						product_id = self.env['product.product'].create({'name':'Combo Meal','ismenucard':True})
					taxes_ids = []
					taxes_ids = [tax.id for tax in order_obj.tax_id]
					values = {'order_id': hotelfolio,
							  'name': order_obj.bill_no,
							  'product_id': product_id.id,
							  'product_uom_qty': 1,
							  'price_unit': order_obj.combo_total,
							  'price_sub_total': order_obj.combo_total,
							  'tax_id': [(6, 0, taxes_ids)],
							  }
					sol_line = so_line_obj.create(values)
					hsl_obj.create({'folio_id': order_obj.folio_id.id,
									'service_line_id': sol_line.id,
									'date_order':order_obj.o_date})
				
				hf_rec = hotel_folio_obj.browse(order_obj.folio_id.id)
				hf_rec.write({'hotel_restaurant_order_ids':
								  [(4, order_obj.id)]})
			
			
			service_charge += order_obj.serv
			last_total+= service_charge
			last_total+= order_obj.amount_tax
			amount_tax = order_obj.amount_tax
			self.write({'state': 'credited'})
		
		folio_obj.write({'service_charge': service_charge,'bill_no': self.bill_no})
		return True
	
	@api.multi
	def generate_kot(self):
		"""
		This method create new record for hotel restaurant order list.
		@param self: The object pointer
		@return: new record set for hotel restaurant order list.
		"""
		res = []
		order_tickets_obj = self.env['hotel.restaurant.kitchen.order.tickets']
		restaurant_order_list_obj = self.env['hotel.restaurant.order.list']
		for order in self:
			if len(order.order_list.ids) == 0:
				raise except_orm(_('No Order Given'),
								 _('Please Give an Order'))
			#                 if len(order.table_no.ids) == 0:
			#                     raise except_orm(_('No Table Assigned '),
			#                                      _('Please Assign a Table'))
			table_ids = [x.id for x in order.table_no]
			kot_data = order_tickets_obj.create({
				'orderno': order.order_no,
				'kot_date': order.o_date,
				'room_no': order.room_no.name,
				'w_name': order.waiter_name.name,
				'tableno': [(6, 0, table_ids)],
			})
			self.kitchen_id = kot_data.id
			for order_line in order.order_list:
				o_line = {'kot_order_list': kot_data.id,
						  'name': order_line.name.id,
						  'item_qty': order_line.item_qty,
						  'item_rate': order_line.item_rate
						  }
				restaurant_order_list_obj.create(o_line)
				res.append(order_line.id)
			self.rest_item_id = [(6, 0, res)]
			self.write({'state': 'order'})
		return True
	
	
	@api.multi
	def action_cancel(self,final=False):
		if self.state == 'payed':
			invoice_record = self.env['account.invoice'].search([('reference','=',self.order_no)])
			invoice_record.state = 'draft'
			invoice_record.internal_number = ''
			invoice_record.unlink()
		print 'final===================', final
		if self.state == 'credited':
			folio_record = self.env['hotel.folio'].search([('id','=',self.folio_id.id)])
			if final == False:
				if folio_record.state == 'manual' or folio_record.state == 'progress':
					raise except_orm(_('Warning'),_('The Guest related to this bill is already Checked Out'))
			for lines in folio_record.service_lines:
				if lines.name == self.bill_no:
					lines.state = 'draft'
					lines.unlink()
		
		self.write({'state': 'cancel'})
		return True



class RemindersWizard(models.Model):
	_name = 'reservation.reminder.wizard'
	
	
	date_from = fields.Date('Date From',required=True)
	date_to = fields.Date('Date To',required=True)
	reminder = fields.Selection([('dob', 'Birth Date Reminder'),
								 ('wedding', 'Wedding Date Reminder')
								 ], 'Select',required=True)
	
	
	@api.multi
	def action_open_window1(self):
		view_id = self.env.ref('hrms.form_reservation_reminder').id
		context = {'default_reminder': self.reminder,
				   'default_date_from':self.date_from,
				   'default_date_to':self.date_to
				   }
		# self.month_id._get_actual_sale_amt(self.location_id.id)
		# context['location_id'] = self.location_id.id
		return {
			'name':'form_name',
			'view_type':'form',
			'view_mode':'form',
			'views' : [(view_id,'form')],
			'res_model':'reservation.customer.reminder',
			'view_id':view_id,
			'type':'ir.actions.act_window',
			# 'res_id':self.month_id.id,
			'target':'inline',
			# 'default_location_id': self.location_id.id,
			'context':context
		}

class Reminders(models.Model):
	_name = 'reservation.customer.reminder'
	
	dob_one2many = fields.One2many('reservation.customer.reminder.dob','dob_id')
	wedding_one2many = fields.One2many('reservation.customer.reminder.wedding','wedding_id')
	reminder = fields.Selection([('dob', 'Birth Date Reminder'),
								 ('wedding', 'Wedding Date Reminder')
								 ], string='Select')
	date_from = fields.Date('Date From')
	date_to = fields.Date('Date To')
	
	@api.multi
	def open_report_reminder(self):
		return self.env['report'].get_action(self, 'hrms.report_customer_reminder')
	
	
	@api.onchange('dob_one2many','wedding_one2many','date_from','date_to')
	def onchange_date(self):
		dob_list = []
		wedding_list = []
		list1 = []
		list2 = []
		var_from = datetime.datetime.strptime(self.date_from, "%Y-%m-%d")
		var_to = datetime.datetime.strptime(self.date_to, "%Y-%m-%d")
		dobs = self.env['hotel.reservation'].search([])
		for dob in dobs:
			if dob.dob:
				var_dob = datetime.datetime.strptime(dob.dob, "%Y-%m-%d")
				
				if ((var_from.day >= var_dob.day >= var_to.day) or(var_to.day >= var_dob.day >= var_from.day)):
					if ((var_from.month >= var_dob.month >= var_to.month) or(var_to.month >= var_dob.month >= var_from.month)):
						
						if dob.partner_id in list1:
							pass
						else:
							
							dob_list.append((0, False, {'name':dob.partner_id,
														'dob':dob.dob}))
						list1.append(dob.partner_id)
		
		self.dob_one2many = dob_list
		
		weddings = self.env['hotel.reservation'].search([])
		for wedding in weddings:
			if wedding.wdng_day:
				var_wedding = datetime.datetime.strptime(wedding.wdng_day, "%Y-%m-%d")
				if ((var_from.day >= var_wedding.day >= var_to.day) or(var_to.day >= var_wedding.day >= var_from.day)):
					if ((var_from.month >= var_wedding.month >= var_to.month) or(var_to.month >= var_wedding.month >= var_from.month)):
						if wedding.partner_id in list2:
							pass
						else:
							wedding_list.append((0, False, {'name':wedding.partner_id,
															'wedding':wedding.wdng_day}))
						list2.append(wedding.partner_id)
		self.wedding_one2many = wedding_list


class Reminders1(models.Model):
	_name = 'reservation.customer.reminder.dob'
	
	dob_id = fields.Many2one('reservation.customer.reminder')
	name = fields.Many2one('res.partner', string='Name')
	dob = fields.Date('DOB', related="name.dob")

class Reminders2(models.Model):
	_name = 'reservation.customer.reminder.wedding'
	
	wedding_id = fields.Many2one('reservation.customer.reminder')
	name = fields.Many2one('res.partner', string='Name')
	wdng_day = fields.Date('Wedding Anniversary Date', related="name.wdng_day")


class AvailableRooms(models.Model):
	_name = 'hotel.rooms.available'
	
	date = fields.Date('Date')
	rooms = fields.One2many('hotel.rooms.available.new', 'room_id', compute="_compute_available_rooms")
	
	@api.depends('date')
	def _compute_available_rooms(self):
		
		if self.date:
			list = []
			
			room_types = self.env['product.category'].search([('isroomtype','=', True)])
			for types in room_types:
				# print 'typeeeeeeeeeeeeeeeeeeeeeeeeeeee=================', types.name
				available_rooms = 0
				rooms = self.env['hotel.room'].search([('categ_id','=',types.id)])
				for room in rooms:
					# print 'roomsssssssssssssssssssssssssssssssssssssssssssssssssssssssss', room.name
					vals = False
					for room_id in room.room_reservation_line_ids:
						if room_id.check_in and room_id.check_out:
							# print '=====================================================', room_id.check_in
							checkout2 = room_id.check_out
							end_dt = datetime.datetime.strptime(checkout2, "%Y-%m-%d")
							# mytime = datetime.datetime.strptime(checkout2, "%Y-%m-%d")
							# mytime += timedelta(hours=5)
							# dummy_check_out=mytime.strftime("%Y-%m-%d %H:%M:%S")
							
							checkin2 = room_id.check_in
							str_dt = datetime.datetime.strptime(checkin2, "%Y-%m-%d")
							# mytime = datetime.datetime.strptime(checkin2, "%Y-%m-%d")
							# mytime += timedelta(hours=5)
							# dummy_check_in=mytime.strftime("%Y-%m-%d %H:%M:%S")
							
							# print '111111111111111111========================',dummy_check_in
							# print '22222222222222222222========================',dummy_check_out
							
							# if dummy_check_in <= self.date <= dummy_check_out:
							#     vals = True
							
							
							check_in = str_dt.date()
							check_out = end_dt.date()
							date = self.date
							
							# print 'in==========================', check_in
							# print 'out=========================', check_out
							# dt = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
							# h=dt.hour+5
							# m=dt.minute+1
							# mytime = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
							# mytime -= timedelta(hours=h,minutes=m)
							# dummy_date=mytime.strftime("%Y-%m-%d %H:%M:%S")
							
							if str(check_in) <= self.date < str(check_out):
								
								vals = True
					if vals == False:
						available_rooms += 1
				list.append({'room_type': types.name, 'no_rooms':available_rooms})
			self.rooms = list



class AvailableRooms(models.Model):
	_name = 'hotel.rooms.available.new'
	
	room_id = fields.Many2one('hotel.rooms.available')
	room_type = fields.Char('Type of room')
	no_rooms = fields.Integer(string='No. of available rooms')



class HotelRoom(models.Model):
	_inherit = 'hotel.room'
	
	
	@api.onchange
	def onchange_categ_id(self):
		if self.category_id:
			self.extra_adult =  self.self.category_id.extra_adult
			self.extra_child =  self.self.category_id.extra_child
	
	
	
	room_amenities_new = fields.One2many('hotel.room.amenities.new','new_id')



# @api.onchange('room_amenities_new')
# def onchange_amenities(self, fields):
#     res = super(HotelRoomNew, self).default_get(fields)
#     amenities_list = []
#     amenities = self.env['hotel.room.amenities'].search([])
#     for rec in amenities:
#         new = self.env['hotel.room.amenities.new'].search([('amenities_id','=',rec.id)])
#         if len(new) < 1:
#             amenities_list.append((0, 0, {'amenities_id': rec.name}))
#         else:
#             pass
#     self.room_amenities_new = amenities_list


class HotelRoomAmenitiesNew(models.Model):
	_name = 'hotel.room.amenities.new'
	
	new_id = fields.Many2one('hotel.room')
	amenities_id = fields.Many2one('hotel.room.amenities', 'Name')
	brand = fields.Char('Brand')
	quantity = fields.Integer('Quantity')
	remarks = fields.Text('Remarks')


class HotelRoomAmenities1(models.Model):
	_inherit = 'hotel.room.amenities'
	
	room_id = fields.Many2many('hotel.room', string='Rooms', compute="_compute_rooms", store=True)
	
	@api.multi
	@api.depends('name')
	def _compute_rooms(self):
		for record in self:
			list =[]
			rooms = self.env['hotel.room.amenities.new'].search([('amenities_id','=',record.id)])
			for room_id in rooms:
				list.append((4, room_id.new_id.id))
			record.room_id = list

class mail_compose_message(models.Model):
	_inherit = 'mail.compose.message'
	
	@api.multi
	def send_mail(self):
		context = self._context
		if context.get('default_model') == 'hotel.reservation' and \
				context.get('default_res_id'):
			reservation = self.env['hotel.reservation'].browse(context['default_res_id'])
			reservation.write({'state': 'block'})
		if context.get('default_model') == 'hotel.reservation' and \
					context.get('default_res_id') and context.get('acknowlegdement'):
				reservation = self.env['hotel.reservation'].browse(context['default_res_id'])
				reservation.write({'state': 'confirm'})
			
		return super(mail_compose_message, self).send_mail()
	
	
	
