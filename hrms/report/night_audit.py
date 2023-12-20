from openerp import models, fields, api, _

class Nightaudit(models.Model):
	_name = 'night.audit.wizard'

	date_from = fields.Date('Date ',required=True)
	# date_to = fields.Date('Date To',required=True)

	@api.multi
	def action_open_window2(self):
		for rec in self:
			datas = {
	    	'ids' : self._ids,
	    	'model' : self._name,
	    	'form' : self.read(),
	    	'context' : self._context,
	    	}
	    	return {
		    	'name' : 'Night Audit Report',
		    	'type' : 'ir.actions.report.xml',
		    	'report_name' : 'hrms.report_nightaudit_template',
		    	'datas' : datas,
		    	'report_type' : 'qweb-html'
		    	}

	@api.multi
	def check_nightaudit(self):
		list = []
		dt1 = datetime.strptime(self.date_to, "%Y-%m-%d").date()
		dt2 = datetime.strptime(self.date_from, "%Y-%m-%d").date()
		delta = dt1 - dt2
		for i in range(delta.days + 1):
			date = dt2 + td(days=i)

			var = self.env['account.account'].search([('checkin_date','>=',self.date_from),('checkout_date','<=',self.date_to)])
			for checkin_id in var:
				guest_name = checkin_id.customer_id.name
				checkin = checkin_id.checkin_date
				checkout = checkin_id.checkout_date
				total = checkin_id.amount_total
				bal = checkin_id.residual
				room = checkin_id.reservation_id.reservation_line.reserved.name



		list.append({
					'date': date,
					'room':room,
					'guest_name' : guest_name,
					'checkin': checkin,
					'checkout' : checkout,
					'total' : total,
					'bal' : bal
					})
		print "aaaaaaaaaaaaaaaaaaaaaa",guest_name,"cccccccc",checkin

		return list

	@api.multi
	def get_checkin(self):
		list = []
		var = self.env['hotel.reservation'].search([('checkin','=',self.date_from)])

		for checkin_id in var:
			guest_name = checkin_id.partner_id.name
			checkin = checkin_id.checkin
			checkout = checkin_id.checkout
			room = ''
			for x in checkin_id.reservation_line:
				for y in x.reserved:
					print "aaaaaaaaaaaaaaaaaaa",y
					room += y.name.name + ','



			list.append({
						'room':room,
						'guest_name' : guest_name,
						'checkin': checkin,
						'checkout' : checkout,
						})
		return list

	@api.multi
	def get_checkout(self):
		list = []
		var = self.env['hotel.folio'].search([('checkout_date','=',self.date_from)])

		for checkout_id in var:
			guest_name = checkout_id.partner_id.name
			checkin = checkout_id.checkin_date
			checkout = checkout_id.checkout_date
			subtotal = checkout_id.grand_total or 0
			amount_tax = checkout_id.tax_amount or 0
			advance = checkout_id.advance or 0
			discount = checkout_id.discount or 0
			total = checkout_id.last_total or 0
			room = ''
			for x in checkout_id.room_lines:
				room += x.product_id.name + ','



			list.append({
						'room':room,
						'guest_name' : guest_name,
						'checkin': checkin,
						'checkout' : checkout,
						'subtotal' : subtotal,
						'amount_tax' : amount_tax,
						'advance' : advance,
						'discount' : discount,
						'total' : total,
						})
		return list

	@api.multi
	def get_advance_payment(self):
		list = []
		var = self.env['reservation.advance'].search([('date','=',self.date_from)])

		for val in var:
			date = val.date
			guest_name = val.partner_id.name
			amount = val.amount or 0
			total = val.total_amount or 0
			mode = val.mode.name
			bank = val.bank_name



			list.append({
						'date' : date,
						'guest_name' : guest_name,
						'amount' : amount,
						'total' : total,
						'mode' : mode,
						'bank' : bank,
						})
		return list



	@api.multi
	def get_invoice(self):
		list = []
		var = self.env['account.invoice'].search([('date_invoice','=',self.date_from)])

		for val in var:
			guest_name = val.customer_id.name
			res_no = val.reservation_id.reservation_no
			amount = val.amount_total or 0
			advance = val.advance or 0
			paid = val.payment_total or 0
			bal = val.residual



			list.append({
						'guest_name' : guest_name,
						'res_no' : res_no,
						'amount' : amount,
						'advance' : advance,
						'paid' : paid,
						'bal' : bal,
						})
		return list


	@api.multi
	def get_summary(self):
		list = []
		var = self.env['payment.vouchers'].search([('date','=',self.date_from)])

		for val in var:
			account_id = val.account_id.name
			amount = val.cash_amt or 0

			list.append({
						'account' : account_id,
						'amount' : amount,
						})
		return list



	# @api.multi
	# def get_liability1_lines(self):
	# 	move_ids = []
	# 	parent_ids = []
	# 	account_ids = []
	# 	dict = {'parent':"", 'amount':0, 'account_list':[{'account':"",'amount':0}]}
	# 	list = []
	# 	list.append(dict)
	# 	account_obj = self.env['account.account']

	# 	if self.target_move == 'posted':
	# 	  orders = self.env['account.move.line'].search([('date','>=',self.date_from),('date','<=',self.date_to),('company_id','=',self.company_id.id),('status','=','posted'),('account_type','=','liability')])
	# 	else:
	# 		orders = self.env['account.move.line'].search([('date','>=',self.date_from),('date','<=',self.date_to),('company_id','=',self.company_id.id),('account_type','=','liability')])
	# 	for order in orders:
	# 		final_list = filter(lambda x: x['parent'] == order.account_id.parent_id.name, list)
	# 		if len(final_list) == 0:
	# 			list.append({'parent':order.account_id.parent_id.name, 'amount':order.credit-order.debit, 'account_list':[{'account':order.account_id.name,'amount':order.credit-order.debit}]})
	# 		if len(final_list) != 0:
	# 			a = list.index(final_list[0])
	# 			list[a]['amount'] -= order.debit
	# 			list[a]['amount'] += order.credit
	# 			if self.visible_details == True:
	# 				final_list1 = filter(lambda x: x['account'] == order.account_id.name, list[a]['account_list'])
	# 				if len(final_list1) == 0:
	# 					list[a]['account_list'].append({'account':order.account_id.name,'amount':order.credit-order.debit})
	# 				if len(final_list1) != 0:
	# 					b = list[a]['account_list'].index(final_list1[0])
	# 					list[a]['account_list'][b]['amount'] -= order.debit
	# 					list[a]['account_list'][b]['amount'] += order.credit
	# 	return list


