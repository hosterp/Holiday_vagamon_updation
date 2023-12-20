from openerp import models, fields, api, _
import time
import datetime
from datetime import date
from datetime import timedelta


class HotelReservation(models.Model):
	_inherit = 'hotel.reservation'

	@api.multi
	def get_checkin(self,checkin):
		mytime = datetime.datetime.strptime(checkin, "%Y-%m-%d %H:%M:%S")
		mytime += timedelta(hours=5,minutes=30)
		return mytime

	@api.multi
	def get_checkout(self,checkout):
		mytime = datetime.datetime.strptime(checkout, "%Y-%m-%d %H:%M:%S")
		mytime += timedelta(hours=5,minutes=30)
		return mytime


	
	
	@api.onchange('external_user','user_id')
	def onchange_user(self):
		if self.external_user == True:
			self.partner_id = self.user_id.partner_id.id
			self.customer_name = self.user_id.partner_id.name
	
	customer_name = fields.Char(related='partner_id.name', string="Name")
	street = fields.Char(related='partner_id.street', string="Street")
	street2 = fields.Char(related='partner_id.street2', string="Street2")
	city = fields.Char(related='partner_id.city', string="City")
	state_id = fields.Many2one(related='partner_id.state_id', string="State")
	zip = fields.Char(related='partner_id.zip', string="ZIP")
	country_id = fields.Many2one(related='partner_id.country_id', string="Country")
	phone = fields.Char(related='partner_id.phone', string="Phone")
	Mobile = fields.Char(related='partner_id.mobile', string="Mobile")
	email = fields.Char(related='partner_id.email', string="Email")
	user_id = fields.Many2one('res.users', 'Assigned to', select=True, track_visibility='onchange')
	external_user = fields.Boolean('External User', default=False)

	no_male = fields.Integer('No. of Male')
	no_female = fields.Integer('No. of Female')
	no_pax = fields.Integer('No. of Pax')
	
	_defaults = {
		'user_id': lambda obj, cr, uid, ctx=None: uid,
		'stage_id': 'draft',
		}
	
	


