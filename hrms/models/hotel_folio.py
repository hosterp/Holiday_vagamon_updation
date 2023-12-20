from openerp import fields, models, api
import time
from datetime import datetime, date
import datetime
from openerp.osv import osv
from datetime import timedelta

#from openerp.osv import fields
from openerp import tools
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import dateutil
from openerp.exceptions import except_orm, ValidationError
import pytz
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


to_19 = ( 'Zero',  'One',   'Two',  'Three', 'Four',   'Five',   'Six',
		  'Seven', 'Eight', 'Nine', 'Ten',   'Eleven', 'Twelve', 'Thirteen',
		  'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen' )
tens  = ( 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety')
denom = ( '',
		  'Thousand',     'Million',         'Billion',       'Trillion',       'Quadrillion',
		  'Quintillion',  'Sextillion',      'Septillion',    'Octillion',      'Nonillion',
		  'Decillion',    'Undecillion',     'Duodecillion',  'Tredecillion',   'Quattuordecillion',
		  'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Novemdecillion', 'Vigintillion' )




class EstimatedBill(models.Model):
	_name = 'estimated.bill'


	date = fields.Date('Date',required=True, default=datetime.datetime.now().today())
	name = fields.Many2one('hotel.folio')


	@api.multi
	def get_food_bill(self,folio_id):
		if folio_id:
			records = self.env['hotel.restaurant.order'].search([('state','=','credited'),('folio_id','=',folio_id.id),('o_date_new','<=',self.date)])
			list = []
			if records:
				
				for rec in records:
			
					date = datetime.datetime.strptime(rec.o_date_new,'%Y-%m-%d %H:%M:%S')
			
			 

					dict = {}
					food_time = str(rec.food_time)+str(" : ") + str(date.date())
					dict['foodtime'] = food_time
					list.append(dict)
					sl_no = 1
					for line in rec.order_list:
						dict = {}
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
						list.append(dict)
				
				return list

			else:
				return 1


	@api.multi
	def get_other_bill(self,folio_id):
		if folio_id:
			records = self.env['hotel.service.line'].search([('folio_id','=',folio_id.id),('date_order','<=',self.date),('is_service','=',True)])
			list = []
			# print 'test==================', records, ads
			if records:
				
				sl_no = 1
				for rec in records:
					if rec.product_id.name != 'Restaurant Bill':
						dict = {}
						dict['sl_no'] = sl_no
						dict['name'] = rec.product_id.name
						dict['uom'] = rec.product_uom.name
						dict['qty'] = rec.product_uom_qty
						dict['item_rate'] = rec.price_unit
						dict['amount'] = rec.price_unit*rec.product_uom_qty
						dict['discount'] = rec.discount
						dict['taxable_value'] = rec.price_subtotal
						# dict['cgst'] = rec.cgst
						# dict['sgst'] = rec.sgst
						# dict['igst'] = rec.igst
						dict['total_amount'] = rec.total_with_tax
						sl_no += 1
						list.append(dict)
				
				return list

			else:
				return 1

	@api.multi
	def print_report(self):
		datas = {
		   'ids': self._ids,
		   'model': self._name,
		   'form': self.read(),
		   'context':self._context,
				}
		return{
		   'name' : 'Estimated Bill Print',
		   'type' : 'ir.actions.report.xml',
		   'report_name' : 'hrms.report_estimated_bill',
		   'datas': datas,
		   'report_type': 'qweb-print'
			  }

	@api.multi
	def view_report(self):
		datas = {
		   'ids': self._ids,
		   'model': self._name,
		   'form': self.read(),
		   'context':self._context,
				}
		return{
		   'name' : 'Estimated Bill Print',
		   'type' : 'ir.actions.report.xml',
		   'report_name' : 'hrms.report_estimated_bill',
		   'datas': datas,
		   'report_type': 'qweb-html'
			  }




class hotelServiceLiner(models.Model):
	_inherit = 'hotel.service.line'

	date_order = fields.Date('Order Date')
	every_day = fields.Boolean('Per Day', help="Please Check for the daily service")
	is_service = fields.Boolean('Is Service', default=False)

	_defaults = {
		'date_order': date.today(),
		}


class hotel_folio_inhr(models.Model):
	_inherit = 'hotel.folio'

	@api.multi
	def room_booking_extend_wizard(self):
		
		self.ensure_one()
		formview_id = self.env.ref('hrms.hotel_extend_reservation_form').id

		return {
			'name': 'Extend reservation',
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'hotel.extend.reservation',
			'view_id': formview_id,
			'target': 'new',
			'context': {'default_extended_res_id':self.id,'default_pre_check_in_date':self.checkin_date,'default_pre_check_out_date':self.checkout_date}
			}


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
	def estimated_bill(self):
		view_ref = self.env['ir.model.data'].get_object_reference('hrms', 'hotel_estimated_bill_wizard')
		view_id = view_ref[1] if view_ref else False
		res = {
		   'type': 'ir.actions.act_window',
		   'name': _('Select Date'),
		   'res_model': 'estimated.bill',
		   'view_type': 'form',
		   'view_mode': 'form',
		   'view_id': view_id,
		   'target': 'new',
		   'context': {'default_name':self.id}
	   }

		return res

	@api.multi
	def get_room_bill(self, date=False):
		list = []	
		checkin1 = self.checkin_date
		checkout1 = self.checkout_date
		today = date
		if date == False:
			today = datetime.datetime.now().date()
		date_format = "%Y-%m-%d"
		no_date = 0
		real_date = 0
		checkout = datetime.datetime.strptime(str(today), date_format)
		real_checkout = datetime.datetime.strptime(checkout1, date_format)
		checkin = datetime.datetime.strptime(checkin1, date_format)
		# print 'd=============================', date,checkout, real_checkout,checkin
		no_date = (checkout-checkin).days
		real_date = (real_checkout-checkin).days
		# print 'd=============================', real_date, no_date
		if no_date <1:
			no_date = 1

		for line in self.room_lines:
			dict = {}
			dict['check_in'] = line.checkin_date
			dict['check_out'] = line.checkout_date
			dict['room'] = line.product_id.name
			dict['desc'] = line.name
			dict['days'] = no_date
			dict['rent'] = line.price_unit
			taxes =''
			for i in line.tax_id:
				taxes += ' '+i.name 
			dict['taxes'] = taxes 
			dict['sub_total'] = (line.price_subtotal/real_date)*no_date
			dict['total'] = (line.total_with_tax/real_date)*no_date
			list.append(dict)
		return list





	@api.multi
	def get_extra_bed_bill(self, date=False):
		list = []	
		checkin1 = self.checkin_date
		checkout1 = self.checkout_date
		today = date
		if date == False:
			today = datetime.datetime.now().date()
		date_format = "%Y-%m-%d"
		no_date = 0
		real_date = 0
		checkout = datetime.datetime.strptime(str(today), date_format)
		real_checkout = datetime.datetime.strptime(checkout1, date_format)
		checkin = datetime.datetime.strptime(checkin1, date_format)
		# print 'd=============================', date,checkout, real_checkout,checkin
		no_date = (checkout-checkin).days
		real_date = (real_checkout-checkin).days
		# print 'd=============================', real_date, no_date
		if no_date <1:
			no_date = 1

		for line in self.extrabed_lines:
			dict = {}
			dict['check_in'] = line.checkin_date
			dict['check_out'] = line.checkout_date
			dict['room'] = line.product_id.name
			dict['desc'] = line.name
			dict['days'] = (line.product_uom_qty/real_date)*no_date
			dict['rent'] = line.price_unit
			taxes =''
			for i in line.tax_id:
				taxes += ' '+i.name 
			dict['taxes'] = taxes 
			dict['sub_total'] = (line.price_subtotal/real_date)*no_date
			dict['total'] = (line.total_with_tax/real_date)*no_date
			list.append(dict)
		if len(list):
			return list
		else:
			return 1


	@api.multi
	def get_room_advance(self, date=False):
		if date:
			advance = 0
			for lines in self.advance_lines:
				if lines.date <= date:
					advance += lines.amount
			return advance
		else:
			return 0
	
		


	@api.multi
	def done_reserve(self):
		self.state = 'done'

	@api.multi
	@api.depends('checkout_date')
	def _get_date_session(self):
		for record in self:
			if record.checkout_date:
				record.date_folio3 = dateutil.parser.parse(record.checkout_date).date()+timedelta(days=1)

	@api.multi
	@api.depends('room_lines')
	def _find_room_nos(self):
		self.room_no_list = ' '
		for line in self:
			for lines in line.room_lines:
				for lines2 in lines.order_line_id:
					for lines3 in lines2.product_id:
						line.room_no_list = lines3.name + ','  + line.room_no_list

	@api.multi
	@api.depends('service_lines')
	def _compute_rb_total(self):
		rb_total=0.0
		for line in self:
			for lines in line.service_lines:
				if lines.product_id.name == 'Restaurant Bill':
					line.rb_total += lines.total_with_tax
	@api.multi
	@api.depends('service_lines')
	def _compute_laundry_total(self):
		ldry_total=0.0
		for line in self:
			for lines in line.service_lines:
				if lines.product_id.is_laundry == True:
					line.ldry_total += lines.total_with_tax

	@api.multi
	@api.depends('service_charge','payment_received','advance','grand_total','discount')
	def _compute_last_total(self):
		for line in self:
			line.last_total = round(line.grand_total+line.tax_amount+line.service_charge-line.advance-line.payment_received-line.discount,1)
			# print 'tst=======================', line.last_total
	@api.multi
	@api.depends('hotel_restaurant_order_ids')
	def _compute_total_service_charge(self):
		ldry_total=0.0
		for line in self:
			line.service_charge = 0.0
			for lines in line.hotel_restaurant_order_ids:
				line.service_charge += lines.serv

	@api.multi
	@api.depends('room_lines','service_lines')
	def _compute_total_amount_tax(self):
		for line in self:
			tax_amount = 0.0
			for lines in line.room_lines:
				tax_amount += lines.tax_amount
			for lines2 in line.service_lines:
				tax_amount += lines2.tax_amount
			for lines3 in line.extrabed_lines:
				tax_amount += lines3.tax_amount
			line.tax_amount = tax_amount

	@api.multi
	@api.depends('service_lines','room_lines')
	def _compute_grand_total(self):
		ldry_total=0.0
		for line in self:
			grand_total1 = 0.0
			grand_total2 = 0.0
			line.grand_total = 0.0
			for lines in line.service_lines:
				grand_total1 += lines.price_subtotal
			for lines2 in line.room_lines:
				grand_total2 += lines2.price_subtotal
			for lines3 in line.extrabed_lines:
				grand_total2 += lines3.price_subtotal
			line.grand_total = grand_total1+grand_total2


			
	@api.onchange('checkout_date', 'checkin_date')
	def onchange_dates(self):
		'''
		This mathod gives the duration between check in and checkout
		if customer will leave only for some hour it would be considers
		as a whole day.If customer will check in checkout for more or equal
		hours, which configured in company as additional hours than it would
		be consider as full days
		--------------------------------------------------------------------
		@param self: object pointer
		@return: Duration and checkout_date
		'''
		company_obj = self.env['res.company']
		configured_addition_hours = 0
		company_ids = company_obj.search([])
		if company_ids.ids:
			configured_addition_hours = company_ids[0].additional_hours
		myduration = 0
		chckin = self.checkin_date
		chckout = self.checkout_date
		if chckin and chckout:
			server_dt = DEFAULT_SERVER_DATE_FORMAT
			chkin_dt = datetime.datetime.strptime(chckin, server_dt)
			chkout_dt = datetime.datetime.strptime(chckout, server_dt)
			dur = chkout_dt - chkin_dt
			sec_dur = dur.seconds
			if (not dur.days and not sec_dur) or (dur.days and not sec_dur):
				myduration = dur.days
			else:
				myduration = dur.days + 1
			if configured_addition_hours > 0:
				additional_hours = abs((dur.seconds / 60) / 60)
				if additional_hours >= configured_addition_hours:
					myduration += 1
		self.duration = myduration

	@api.depends('advance_lines')
	def _compute_advance(self):
		for line in self:
			line.advance = 0
			for lines in line.advance_lines:
				line.advance += lines.total_amount

	@api.multi
	@api.depends('seq')
	def compute_name(self):
		for rec in self:
			rec.name = 'F/'+str(rec.seq)
			# print '=============================',self.travel_agency


	payment = fields.Many2one('account.journal',string="Payment Methode")
	date_folio3 = fields.Date('Date Folio',compute="_get_date_session",store=True)
	advance = fields.Float(compute='_compute_advance', string='Advance', store=True)
	grand_total = fields.Float(compute='_compute_grand_total',  string='Sub Total')
	last_total = fields.Float(compute='_compute_last_total',  string='Total')
	service_charge = fields.Float(compute='_compute_total_service_charge', string='Total')
	tax_amount = fields.Float(compute='_compute_total_amount_tax', string='Amount Tax')
	bill_no = fields.Char('Bill No Restaurant')
	checkout_dummy = fields.Datetime('Dummy-Date-Departure')
	extra_amount_bed = fields.Float('Extra Bed', default=0.0)
	extra_amount_withoutbed = fields.Float('Without Bed', default=0.0)
	payment_received = fields.Float('Payment Received', size=64, default=0.0)
	rb_total = fields.Float(compute='_compute_rb_total',  string='RB Total')
	ldry_total = fields.Float(compute='_compute_laundry_total', string='Laundry Total')
	room_no_list = fields.Char('Rooms')
	discount = fields.Float('Discount')
	checkout_time =fields.Char('Check Out Time')

	company_id = fields.Many2one('res.company', 'Company', required=True)
	advance_lines = fields.One2many('reservation.advance', 'folio_id', 'Advance Payments')
	is_agency = fields.Boolean('Is Agency', default=False)
	checkin_date = fields.Date('Check In', required=True, readonly=True,
								   states={'draft': [('readonly', False)]})
	checkout_date = fields.Date('Check Out', required=True, readonly=True,
									states={'draft': [('readonly', False)]})
	partner_order_id = fields.Many2one('res.partner', 'Traveling Agent',readonly=True)
	travel_agency = fields.Many2one('res.partner','Travel agency')
	grc_no = fields.Char('GRC No:')
	seq = fields.Integer('Sequence')
	name = fields.Char(compute='compute_name', string='Folio No')
	extrabed_lines = fields.One2many('hotel.folio.line', 'folio_id2',
                                 states={'draft': [('readonly', False)],
                                         'sent': [('readonly', False)]},
                                 help="Extra Bed Lines.")

	_defaults = {
		'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
		}


	#credit2 = fields.Float(compute='_compute_credit', store=True, string='Credit')
	#extra_line2 = fields.One2many('extra.service.line', 'line_id_extra_folio',
	#                                   'Extras',
	#                                   help='Extras')
	# @api.multi
 #    @api.depends('date_order')
 #    def _get_date_session(self):
 #        for record in self:
 #            if record.date_order:
 #                record.date_folio = dateutil.parser.parse(record.date_order).date()



	@api.constrains('checkin_date', 'checkout_date')
	def check_dates(self):
		'''
		This method is used to validate the checkin_date and checkout_date.
		-------------------------------------------------------------------
		@param self: object pointer
		@return: raise warning depending on the validation
		'''
		if self.checkin_date and self.checkout_date:
			if self.checkin_date > self.checkout_date:
				raise ValidationError(_('Check in Date Should be \
				less than the Check Out Date!'))
		# print 'test-=======================2',self.checkin_date,self.checkout_date
		#if self.date_order and self.checkin_date:
		#    if self.checkin_date <= self.date_order:
		#        raise ValidationError(_('Check in date should be \
		#        greater than the current date.'))


	@api.multi
	def action_invoice_create(self, grouped=False, states=None):
		'''
		@param self: object pointer
		'''
		date_format = "%Y-%m-%d %H:%M:%S"

		if states is None:
			states = ['confirmed', 'done']
		order_ids = [folio.order_id.id for folio in self]
		room_lst = []
		sale_obj = self.env['sale.order'].browse(order_ids)
		inv_ids0 = set(inv.id for sale in self.env['sale.order'].browse(order_ids) for inv in sale.invoice_ids)
		sale_obj.signal_workflow('manual_invoice')
		inv_ids1 = set(inv.id for sale in self.env['sale.order'].browse(order_ids) for inv in sale.invoice_ids)
		new_inv_ids = list(inv_ids1 - inv_ids0)
		invoice_id1=new_inv_ids and new_inv_ids[0]
		invoice_obj = self.env['account.invoice'].browse(invoice_id1)
		advance=self.advance+self.payment_received
		service=self.service_charge
		balance=self.last_total
		checkin_date= self.checkin_date
		checkout_date= self.checkout_date
		bill_no=self.bill_no
		folio_id=self.id
		amount_total=self.grand_total
		room_no_list=self.room_no_list
		customer_id=self.partner_id.id
		discount = self.discount
		grc_no = self.grc_no
		print "jhdsfjiknsdijofjkdshfjh=-=-=-=-=-=-",self.travel_agency

		invoice_obj.write({'folio_id': folio_id,'traval_agent_id':self.travel_agency.id,'account_id':self.travel_agency.property_account_receivable.id,'advance': advance, 'discount':discount,'service': service, 'balance': balance, 'checkin_date': checkin_date, 'checkout_date': checkout_date, 'bill_no': bill_no,'room_no_list': room_no_list, 'customer_id': customer_id})
		line_ids = []

		line_ids = [line.id for line in invoice_obj.invoice_line]
		for serviceline in self.service_lines:
			value = {}
			invoice_line = self.env['account.invoice.line'].search([('id','in',line_ids),('product_id','=',serviceline.product_id.id),('price_subtotal','=',serviceline.price_subtotal)])[0]
			value = {'date_service':serviceline.date_order, 'every_day':serviceline.every_day}
			if serviceline.product_id.name == 'Restaurant Bill' and self.company_id.restaurant_income_account.id != False:
				value['account_id']  = self.company_id.restaurant_income_account.id != False
			# print 'aaaaaaaaaaaaaaaaaaaaaaaaa', value, asdasd
			invoice_line.write(value)

		if new_inv_ids:
			for line in self:
				values = {'invoiced': True,
						  'state': 'progress' if grouped else 'progress',
						  'hotel_invoice_id': new_inv_ids and new_inv_ids[0]
						  }
				line.write(values)

				for rec in line.room_lines:
					room_lst.append(rec.product_id)
				for room in room_lst:
					room_obj = self.env['hotel.room'
										].search([('name', '=', room.name)])
					room_obj.write({'isroom': True})
			return new_inv_ids and new_inv_ids[0]
		return True

	@api.multi
	def action_wait(self):
		# rec = self.env['ir.attachment'].search([('res_model','=','hotel.reservation'),('res_name','=',self.reservation_id.reservation_no+'...')])
		# print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrr",len(rec)
		# if len(rec)==0:
			# raise except_orm(_('Warning'),_('Attachment Must Contain Atleast One File'))
		# else:
		sale_order_obj = self.env['sale.order']
		for o in self:
			sale_obj = sale_order_obj.browse([o.order_id.id])
			sale_obj.signal_workflow('order_confirm')

		self.reservation_id.state = 'checkout'
		invoice = self.action_invoice_create()
		invoice_obj = self.env['account.invoice'].search([('id','=',invoice)])
		for lines in self.env['account.move.line'].search([('reserv_id','=',self.reservation_id.id),('debit','=',0.0)]):
			lines.invoice_id = invoice_obj.id
		invoice_obj.action_date_assign()
		
		tz = pytz.timezone('Asia/Kolkata')
		date_string = datetime.datetime.now(tz)
		format1 = '%I:%M %p'
		my_date = datetime.datetime.strftime(date_string, format1)
		self.checkout_time = my_date
		rec = self.env['room.type.reservation'].search([('reservation_id','=',self.reservation_id.id)])
		if rec:
			for r_line in rec:
				r_line.write({'state':'unassigned','status':'unassigned'})
		# print "test========================================"
		# invoice_obj.action_move_create()
		# invoice_obj.action_number()
		# invoice_obj.invoice_validate()
		# invoice_obj.compute_residual()


	@api.multi
	def action_view_invoice(self):
		self.ensure_one()
		# Search for record belonging to the current staff
		record =  self.env['account.invoice'].search([('folio_id','=',self.id)])

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



	@api.model
	def create(self, vals, check=True):
		"""
		Overrides orm create method.
		@param self: The object pointer
		@param vals: dictionary of fields value.
		@return: new record set for hotel folio.
		"""
		if not 'service_lines' and 'folio_id' in vals:
			tmp_room_lines = vals.get('room_lines', [])
			vals['order_policy'] = vals.get('hotel_policy', 'manual')
			vals.update({'room_lines': []})
			folio_id = super(hotel_folio_inhr, self).create(vals)
			for line in (tmp_room_lines):
				line[2].update({'folio_id': folio_id})
			vals.update({'room_lines': tmp_room_lines})
			folio_id.write(vals)
		else:
			if not vals:
				vals = {}
			folio = self.env['hotel.folio'].search([], order='seq desc', limit=1)
			# print 'folio======================', folio.seq, asd
			if not folio:
				vals['seq'] = 1
			else:
				vals['seq'] = folio.seq + 1 
			# vals['name'] = self.env['ir.sequence'].get('hotel.folio')
			folio_id = super(hotel_folio_inhr, self).create(vals)
		return folio_id



	@api.multi
	def write(self,vals):
		if vals.get('grc_no'):
			self.reservation_id.grc_no = vals.get('grc_no')
		return super(hotel_folio_inhr, self).write(vals)

	@api.multi
	def unlink(self):
		for rec in self:
			up = self.env['hotel.folio'].search([('seq','>',rec.seq)], order='seq desc')
			if up:
				for line in up:
					line.seq -= 1
		result = super(hotel_folio_inhr, self).unlink()


class Extendreservation(models.Model):
	_name = 'hotel.extend.reservation'


	pre_check_in_date = fields.Date(' check in' )
	pre_check_out_date = fields.Date(' check out' )
	new_checkout_date = fields.Date('New check out', required=True )
	extended_res_id = fields.Many2one('hotel.folio', 'Reservation id : ')
	# room_type = fields.Many2one('hotel.room.type','Room Type')

	@api.multi
	def get_room_details(self):
		for room in self.extended_res_id.room_lines:
			# print '############', room.product_id
			room_no = self.env['hotel.room'].search([('id','=',room.product_id.id)])
			room_type = self.env['hotel.room.type'].search([('cat_id','=',room_no.categ_id.id)])
			reservation = self.env['room.type.reservation'].search([('room_type_id','=',room_type.id),('check_in','<=',self.new_checkout_date),('check_out','>',self.new_checkout_date)])
			booked_rooms = 1
			for reserv in reservation:
				booked_rooms += reserv.nos
			if booked_rooms <= room_type.capacity:
				# raise ValidationError(_('rooms are avaliable in this category!'))
				chckin = room.checkin_date
				chckout = self.new_checkout_date
				if chckin and chckout:
					server_dt = DEFAULT_SERVER_DATE_FORMAT
					chkin_dt = datetime.datetime.strptime(chckin, server_dt)
					chkout_dt = datetime.datetime.strptime(chckout, server_dt)
					dur = chkout_dt - chkin_dt
					sec_dur = dur.seconds
					if (not dur.days and not sec_dur) or (dur.days and not sec_dur):
						myduration = dur.days
					else:
						myduration = dur.days + 1
				room.product_uom_qty = myduration
				# reservation.check_out= self.new_checkout_date
				values = {
						'room_type_id':room_type.id,
						'state':'assigned',
						'reservation_id':self.extended_res_id.reservation_id.id,
						'nos':1,
						'status':'assigned',
						'check_in':room.checkout_date,
						'check_out':self.new_checkout_date,
						}
				self.env['room.type.reservation'].create(values)
				room.checkout_date= self.new_checkout_date
				temp = False
				if temp == False:
					self.extended_res_id.duration = myduration
					self.extended_res_id.checkout_date = self.new_checkout_date
					temp = True
					for extrabed in self.extended_res_id.extrabed_lines:
						extrabed.product_uom_qty = (extrabed.product_uom_qty/self.extended_res_id.duration)*myduration
						extrabed.checkout_date = self.new_checkout_date
			else:
				raise ValidationError(_('no rooms are avaliable in this category!'))

class HotelFolioLine(models.Model):
	_inherit='hotel.folio.line'

	@api.multi
	def current_room_checkout(self):
		reservation_lines = self.env['hotel.room.reservation.line'].search([('reservation_id','=', self.folio_id.reservation_id.id)])

		for lines in reservation_lines:
			if lines.room_id == self.env['hotel.room'].search([('product_id','=',self.product_id.id)]):
				lines.check_in = self.checkin_date
				lines.check_out = self.checkout_date
				lines.status = 'checkout'
				lines.state = 'unassigned'
		self.is_check_out = True
	@api.multi
	def current_room_check_in(self):
		reservation_obj = self.env['hotel.room.reservation.line']
		values = {'room_id':self.env['hotel.room'].search([('product_id','=',self.product_id.id)]).id,
				  'check_in': self.checkin_date,
				  'check_out': self.checkout_date,
				  'state': 'assigned',
				  'reservation_id': self.folio_id.reservation_id.id,
				  'status': 'done'}
		reservation_obj.create(values)
		self.is_check_in = True


	@api.onchange('product_id','checkout_date','checkin_date')
	def on_change_product_id(self):
		if not self.product_id:

			hotel_room_obj = self.env['hotel.room'].search([('id','!=',False)])
			product_ids = []
			room_ids = []
			for room in hotel_room_obj:
				assigned = False
				for line in room.room_reservation_line_ids:
					if line.status not in ['cancel','checkout']:
						checkout2 = self.checkout_date
						end_dt = datetime.datetime.strptime(checkout2, "%Y-%m-%d")
						h=end_dt.hour+5
			  #          print 'h================',h
						m=end_dt.minute+1
						mytime = datetime.datetime.strptime(checkout2, "%Y-%m-%d")
						mytime -= timedelta(hours=h,minutes=m)
			#            print mytime.strftime("%Y.%m.%d")
						dummy_check_out=mytime.strftime("%Y-%m-%d")
			#                     print 'dummy_check_out================', dummy_check_out

						checkin2 = self.checkin_date
						str_dt = datetime.datetime.strptime(checkin2, "%Y-%m-%d")
						h2=str_dt.hour+5
			  #          print 'h================',h2
						m2=str_dt.minute-1
						mytime = datetime.datetime.strptime(checkin2, "%Y-%m-%d")
						mytime -= timedelta(hours=h2,minutes=m2)
			  #          print mytime.strftime("%Y.%m.%d")
						dummy_check_in=mytime.strftime("%Y-%m-%d")
			#                     print 'dummy_check_in================', dummy_check_in


			#                     print 'line.check_in=====================', line.check_in
			#                     print 'self.line_id.checkin===============', self.line_id.checkin
			#                     print 'dummy_check_in=================================' ,dummy_check_in
			#                     print 'line.check_out=====================', line.check_out
			#                     print 'line.check_in=====================', line.check_in
			#                     print 'dummy_check_out==============================', dummy_check_out
			#                     print 'self.line_id.checkout===============', self.line_id.checkout
			#                     print 'line.check_out=====================', line.check_out

						if (line.check_in <= dummy_check_in <=
							line.check_out) or (line.check_in <=
												dummy_check_out <=
												line.check_out):
							assigned = True
			#                     if dummy_check_out < line.check_out:
				for rm_line in room.room_line_ids:
					if rm_line.status not in ['cancel','checkout']:

						if (rm_line.check_in <= self.checkin_date <=
							rm_line.check_out) or (rm_line.check_in <=
												self.checkout_date <=
												rm_line.check_out):
							assigned = True
				if not assigned:
					room_ids.append(room.id)
			rooms = self.env['hotel.room'].search([('id','in',room_ids)])
			product_ids = [room.product_id.id for room in rooms]
			domain = {'product_id': [('id', 'in', product_ids)]}
			return {'domain': domain}
		if self.product_id:
			self.price_unit = self.product_id.lst_price
			self.name = self.folio_id.reservation_id.reservation_no
			taxes_ids = []
			taxes_ids = [tax.id for tax in self.product_id.taxes_id]
			self.tax_id = [(6, 0, taxes_ids)]


	@api.onchange('checkin_date', 'checkout_date')
	def on_change_checkout(self):
		'''
		When you change checkin_date or checkout_date it will checked it
		and update the qty of hotel folio line
		-----------------------------------------------------------------
		@param self: object pointer
		'''
		if not self.checkin_date:
			self.checkin_date = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
		if not self.checkout_date:
			self.checkout_date = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
		chckin = self.checkin_date
		chckout = self.checkout_date
		if chckin and chckout:
			server_dt = DEFAULT_SERVER_DATE_FORMAT
			chkin_dt = datetime.datetime.strptime(chckin, server_dt)
			chkout_dt = datetime.datetime.strptime(chckout, server_dt)
			dur = chkout_dt - chkin_dt
			sec_dur = dur.seconds
			if (not dur.days and not sec_dur) or (dur.days and not sec_dur):
				myduration = dur.days
			else:
				myduration = dur.days + 1
		self.product_uom_qty = myduration



	@api.constrains('checkin_date', 'checkout_date')
	def check_dates(self):
		'''
		This method is used to validate the checkin_date and checkout_date.
		-------------------------------------------------------------------
		@param self: object pointer
		@return: raise warning depending on the validation
		'''
		if self.checkin_date and self.checkout_date:
			if self.checkin_date > self.checkout_date:
				raise ValidationError(_('Check in Date Should be \
				less than the Check Out Date!'))
#         if self.folio_id.date_order and self.checkin_date:
#             if self.checkin_date <= self.folio_id.date_order:
#                 raise ValidationError(_('Check in date should be \
#                 greater than the current date.'))


	# @api.multi
	# @api.depends('product_id','price_unit','product_uom_qty','tax_id')
	# def _compute_total_with_tax(self):
	# 	for line in self:
	# 		tax = 0
	# 		included = False
	# 		for lines in line.tax_id:
	# 			if lines.price_include == True:
	# 				included = True
	# 			tax += lines.amount
	# 		if included == False:
	# 			# print 'test==================1', (1 + tax)*line.price_unit*line.product_uom_qty
	# 			line.total_with_tax = round(1 + tax)*line.price_unit*line.product_uom_qty
	# 		if included == True:
	# 			# print 'test==================2', line.price_unit*line.product_uom_qty
	# 			line.total_with_tax = line.price_unit*line.product_uom_qty
	# 			# print 'test==================3', line.total_with_tax
	# 		line.tax_amount = tax*line.price_subtotal


	# 		for lines in line.tax_id:
 #                tax += lines.amount
 #                if lines.price_include == True:
 #                    included = True
 #            line.total_with_tax = (1 + tax)*line.price_unit*line.product_uom_qty
 #            line.tax_amount = tax*line.price_unit*line.product_uom_qty
 #            if included == True:
 #            	line.total_with_tax = line.price_unit*line.product_uom_qty
 #            	line.tax_amount = tax*((line.price_unit*line.product_uom_qty)/(1+tax))




	# total_with_tax = fields.Float(compute='_compute_total_with_tax', store=True, string='Total')
	# tax_amount = fields.Float(compute='_compute_total_with_tax', store=True, string='Tax')
	checkin_date = fields.Date('Check In', required=True)
	checkout_date = fields.Date('Check Out', required=True)
	folio_id2 = fields.Many2one('hotel.folio', 'Folio')
	desc = fields.Char("Item")

class HotelFolioLine(models.Model):
	_inherit = 'hotel.folio.line'

	is_check_out = fields.Boolean('CheckOut', default=False)
	is_check_in = fields.Boolean('CheckIn', default=False)



class FolioRestReservation(models.TransientModel):
	_inherit = 'folio.rest.reservation'



	date_start = fields.Datetime('Start Date')
	date_end = fields.Datetime('End Date')
	check = fields.Boolean('With Details')


	@api.multi
	def cash_sale_report(self):
		data = {
			'ids': self.ids,
			'model': 'hotel.folio',
			'form': self.read(['date_start', 'date_end', 'check'])[0]
		}

		return self.env['report'
						].get_action(self,
									 'hrms.report_restaurant_cash_sale',
									 data=data)


	@api.multi
	def credit_sale_report(self):
		data = {
			'ids': self.ids,
			'model': 'hotel.folio',
			'form': self.read(['date_start', 'date_end', 'check'])[0]
		}
		return self.env['report'
						].get_action(self,
									 'hrms.report_cash_credit',
									 data=data)


