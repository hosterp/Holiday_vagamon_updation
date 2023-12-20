from openerp import models, fields, api, _
import time
import datetime
from datetime import date, timedelta as td
from datetime import timedelta, datetime

class Nightaudit(models.Model):
	_name = 'outstanding.wizard'

	date_from = fields.Date('Date From',required=True)
	date_to = fields.Date('Date To',required=True)

	@api.multi
	def action_open_window1(self):
		for rec in self:
			datas = {
	    	'ids' : self._ids,
	    	'model' : self._name,
	    	'form' : self.read(),
	    	'context' : self._context,
	    	}
	    	return {
		    	'name' : 'Outstanding Report',
		    	'type' : 'ir.actions.report.xml',
		    	'report_name' : 'hrms.report_outstanding_template',
		    	'datas' : datas,
		    	'report_type' : 'qweb-html'
		    	}

	@api.multi
	def check_outstanding(self):
		list = []

		var = self.env['account.invoice'].search([('checkin_date','>=',self.date_from),('checkout_date','<=',self.date_to)],order='checkin_date asc')

		for checkin_id in var:
			guest_name = checkin_id.customer_id.name
			checkin = checkin_id.checkin_date
			checkout = checkin_id.checkout_date
			total = checkin_id.amount_total
			bal = checkin_id.residual
			room = ''
			for x in checkin_id.reservation_id.reservation_line:
				for y in x.reserved:
					print "aaaaaaaaaaaaaaaaaaa",y
					room += y.name.name



			list.append({
						'room':room,
						'guest_name' : guest_name,
						'checkin': checkin,
						'checkout' : checkout,
						'total' : total,
						'bal' : bal
						})
		print "aaaaaaaaaaaaaaaaaaaaaa",guest_name,"cccccccc",checkin

		return list
