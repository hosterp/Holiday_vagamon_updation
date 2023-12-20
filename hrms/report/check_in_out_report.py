from openerp.exceptions import except_orm, ValidationError
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp import models, fields, api, _
from openerp import workflow
import time
import datetime
# from datetime import datetime, timedelta
from datetime import date, timedelta as td

# from datetime import datetime
# from openerp.osv import fields, osv
from openerp.tools.translate import _
# from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
# from openerp.osv import fields, osv
from datetime import timedelta, datetime
from docutils.nodes import line
from pychart.arrow import default
# from pygments.lexer import _inherit
from lxml import etree
from dateutil.relativedelta import relativedelta


import dateutil.parser

class CustomerAvailableRoomsReport(models.Model):
	_name = 'customer.available.rooms.report'

	from_date = fields.Date('From',required=True)
	to_date = fields.Date('To',required=True)

	@api.multi
	def get_dates(self):
		date_range_list = []
		summary_header_list = []
		d_frm_obj = datetime.strptime(self.from_date, "%Y-%m-%d")
		d_to_obj = datetime.strptime(self.to_date, "%Y-%m-%d")
		temp_date = d_frm_obj
		while(temp_date <= d_to_obj):
			val = ''
			val = (
				   str(temp_date.strftime("%b")) + ' ' +
				   str(temp_date.strftime("%d")))
			summary_header_list.append({'date':val})
			date_range_list.append(temp_date.strftime
								   (DEFAULT_SERVER_DATETIME_FORMAT))
			temp_date = temp_date + timedelta(days=1)
		return summary_header_list

	@api.multi
	def get_category(self):
		categories = []
		rooms_type = self.env['hotel.room.type'].search([])
		for line in rooms_type:
			categories.append({'category':line.name,'categ_id':line.id,})
		return categories


	@api.multi
	def get_category_details(self,types):
		date_range_list = []
		reserve = []
		d_frm_obj = datetime.strptime(self.from_date, "%Y-%m-%d")
		d_to_obj = datetime.strptime(self.to_date, "%Y-%m-%d")
		temp_date = d_frm_obj
		while(temp_date <= d_to_obj):
			date_range_list.append(temp_date.strftime
								   (DEFAULT_SERVER_DATETIME_FORMAT))
			temp_date = temp_date + timedelta(days=1)
		list = []
		for date in date_range_list:
			room_type = self.env['hotel.room.type'].search([('id','=',types)])
			categs = self.env['room.type.reservation'].search([('room_type_id','=',room_type.id),('check_in','<=',date),('check_out','>',date)])
			available_rooms = room_type.room_no
			for cat_id in categs:
				available_rooms -= cat_id.nos
			list.append({'vacancy':available_rooms})
		return list

	# @api.multi
	# def get_data(self,from_date,to_date):
	# 	list = []
	# 	rooms = self.env['hotel.room'].search([])
	# 	for room in rooms:
	# 		record = self.env['hotel.room.reservation.line'].search([('check_in','>=',from_date),('check_in','<=',to_date),('room_id','=',room.id)])
	# 		if record:
			
	# 			values = {
	# 				'room_type':room.categ_id.name,
	# 				'room':room.name,
	# 				'status':'Occupied'
	# 			}

	# 			list.append(values)
	# 		else:
	# 			values = {
	# 				'room_type':room.categ_id.name,
	# 				'room':room.name,
	# 				'status':'Free'
	# 			}

	# 			list.append(values)
	# 	return list



	@api.multi
	def action_open_window2(self):
	   

	   datas = {
		   'ids': self._ids,
		   'model': self._name,
		   'form': self.read(),
		   'context':self._context,
	   }
	   
	   return{
		   'name' : 'Available Rooms Report',
		   'type' : 'ir.actions.report.xml',
		   'report_name' : 'hrms.report_available_room_template2',
		   'datas': datas,
		   'report_type': 'qweb-pdf'
	   }

	@api.multi
	def action_open_window1(self):
	   

	   datas = {
		   'ids': self._ids,
		   'model': self._name,
		   'form': self.read(),
		   'context':self._context,
	   }
	   
	   return{
		   'name' : 'Available Rooms Report',
		   'type' : 'ir.actions.report.xml',
		   'report_name' : 'hrms.report_available_room_template2',
		   'datas': datas,
		   'report_type': 'qweb-html'
	   }   


class CheckWizard(models.Model):
	_name = 'customer.check.in_out.wizard'
	
	
	date_from = fields.Date('Date From',required=True)
	date_to = fields.Date('Date To',required=True)
	


	@api.multi
	def action_open_window2(self):
	   

	   datas = {
		   'ids': self._ids,
		   'model': self._name,
		   'form': self.read(),
		   'context':self._context,
	   }
	   
	   return{
		   'name' : 'Check In/Out Report',
		   'type' : 'ir.actions.report.xml',
		   'report_name' : 'hrms.report_check_in_out_template2',
		   'datas': datas,
		   'report_type': 'qweb-pdf'
	   }

	@api.multi
	def action_open_window1(self):
	   

	   datas = {
		   'ids': self._ids,
		   'model': self._name,
		   'form': self.read(),
		   'context':self._context,
	   }
	   
	   return{
		   'name' : 'Check In/Out Report',
		   'type' : 'ir.actions.report.xml',
		   'report_name' : 'hrms.report_check_in_out_template2',
		   'datas': datas,
		   'report_type': 'qweb-html'
	   }   



	@api.multi
	def get_check_in_out_details(self):

		# date_to = datetime.strptime(self.date_to, "%Y-%m-%d").strftime("%Y, %m, %d").date()
		# date_from = datetime.strptime(self.date_from, "%Y-%m-%d").strftime("%Y, %m, %d").date()

		list = []
		dt1 = datetime.strptime(self.date_to, "%Y-%m-%d").date()
		dt2 = datetime.strptime(self.date_from, "%Y-%m-%d").date()
		delta = dt1 - dt2
		for i in range(delta.days + 1):
			adults_in = children_in = adults_out = children_out = 0
			date = dt2 + td(days=i)


			checkin = self.env['hotel.reservation'].search([('state','=','done')])
			# print 'in==============================================', checkin
			for checkin_id in checkin:
				var1 = dateutil.parser.parse(checkin_id.checkin).date()

				if var1 == date:
					adults_in += checkin_id.adults
					children_in += checkin_id.children

			checkout = self.env['hotel.reservation'].search([('state','=','checkout')])
			for checkout_id in checkout:
				# print '0000000000000000000000000000============================================================', checkout_id
				
				var2 = dateutil.parser.parse(checkout_id.checkout).date()

				if var2 == date:
					
					adults_out += checkout_id.adults
					children_out += checkout_id.children
				# print 'out==============================================', checkout_id.adults
				# print 'out2222222222====================================', checkout_id.children
			list.append({
						'date': date,
						'checkin' : adults_in + children_in,
						'checkout': adults_out + children_out
					})

		return list


class OccupancyWizard(models.Model):
	_name = 'customer.occupancy.wizard'
	
	
	date_from = fields.Date('Date From',required=True)
	date_to = fields.Date('Date To',required=True)
	


	@api.multi
	def action_open_window2(self):
	   

	   datas = {
		   'ids': self._ids,
		   'model': self._name,
		   'form': self.read(),
		   'context':self._context,
	   }
	   
	   return{
		   'name' : 'Occupancy Report',
		   'type' : 'ir.actions.report.xml',
		   'report_name' : 'hrms.report_customer_occupancy_template2',
		   'datas': datas,
		   'report_type': 'qweb-pdf'
	   }

	@api.multi
	def action_open_window1(self):
	   

	   datas = {
		   'ids': self._ids,
		   'model': self._name,
		   'form': self.read(),
		   'context':self._context,
	   }
	   
	   return{
		   'name' : 'Occupancy Report',
		   'type' : 'ir.actions.report.xml',
		   'report_name' : 'hrms.report_customer_occupancy_template2',
		   'datas': datas,
		   'report_type': 'qweb-html'
	   }   



	@api.multi
	def get_occupancy_details(self):
		list = []
		
		reservation = self.env['hotel.reservation'].search(['|',('state','=','done'),('state','=','checkout'),'|',('checkin','>=',self.date_from),('checkout','>=',self.date_from),'|',('checkin','<=',self.date_to),('checkout','<=',self.date_to)])
		for reserv_id in reservation:
			room_name = ''
			for room in reserv_id.reservation_line:
				room_name = room.room_allocate + room_name
			# print 'room==============', room_name
			if room_name == '':
				for line in reserv_id.folio_id:
					for lines in line.room_lines:
						room_name = lines.product_id.name +' '+ room_name
			list.append({
					'room_no': room_name,
					'guest': reserv_id.partner_id.name,
					'no_pax' : reserv_id.adults,
					'no_child':reserv_id.children,
					'checkin': reserv_id.checkin,
					'checkout': reserv_id.checkout
				})

		# print 'lines==============', list,asdasd
		return list

