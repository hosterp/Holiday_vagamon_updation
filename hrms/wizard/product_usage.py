from openerp import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import time
import datetime
from datetime import date
from datetime import timedelta


class ProductUsageReport(models.Model):
	_name = 'product.usage.report'

	date_from = fields.Date('Period From',required=True)
	date_to = fields.Date('Period To',required=True)
	location_id = fields.Many2one('stock.location','Location',required=True)

	@api.model
	def default_get(self, default_fields):
		vals = super(ProductUsageReport, self).default_get(default_fields)
		location = self.env['stock.location'].search([('usage','=','internal'),('name','=','Stock')],limit=1)
		if location:
			vals.update({'location_id' : location.id})
		
		return vals

	# @api.multi
	# def get_location(self):
	# 	print "hhhhhhhhhhhhhhhhhhhhhhh"
	# 	return self.env['stock.location'].search([('usage','=','internal'),('name','=','Stock')],limit=1).id




	@api.multi
	def get_product_usage(self,date_from,date_to,location):
		# date_range_list = []
		# d_frm_obj = datetime.datetime.strptime(date_from, "%Y-%m-%d")
		# d_to_obj = datetime.datetime.strptime(date_to, "%Y-%m-%d")
		# temp_date = d_frm_obj
		# while(temp_date <= d_to_obj):
		# 	date_range_list.append(temp_date.strftime
		# 						   (DEFAULT_SERVER_DATETIME_FORMAT))
		# 	temp_date = temp_date + timedelta(days=1)
		list = []
		products = [i.id for i in self.env['product.product'].search([('type','=','product')])]
		# product_lines = self.env['stock.move'].search([('location_dest_id','=',location.id),('date','>=',date_from),('date','<=',date_to)])
		# for product in product_lines:
		# 	if product.product_id not in products:
		# 		products.append(product.product_id.id)

		# for date in date_range_list:
			
		for prd in products:
			opening_val = 0
			closing_val = 0
			usage = 0
			avg_price = 0
			avg_count = 0
			inventory_value = 0
			purchase = 0
			came = 0
			gone = 0

			stock_moves_opening = self.env['stock.move'].search([('state','=','done'),('product_id','=',prd),('location_dest_id','=',location.id),('date','<',date_from)])
			for stock_moves in stock_moves_opening:
				came += stock_moves.product_uom_qty

			stock_moves_opening = self.env['stock.move'].search([('state','=','done'),('product_id','=',prd),('location_id','=',location.id),('date','<',date_from)])
			for stock_moves in stock_moves_opening:
				gone += stock_moves.product_uom_qty

			opening_val = came - gone

			purchase_moves = self.env['stock.move'].search([('state','=','done'),('product_id','=',prd),('location_dest_id','=',location.id),('date','>=',date_from),('date','<=',date_to)])
			for lines in purchase_moves:
				purchase += lines.product_uom_qty


			stock_history = self.env['stock.history'].search([('product_id','=',prd),('location_id','=',location.id),('date','>=',date_from),('date','<=',date_to)])
			for line in stock_history:
				inventory_value += line.inventory_value
				avg_count += 1

			usage_closing = self.env['stock.move'].search([('product_id','=',prd),('location_id','=',location.id),('location_dest_id','=',self.env['stock.location'].search([('usage','=','inventory'),('name','=','Inventory loss')],limit=1).id),('state','=','done'),('date','>=',date_from),('date','<=',date_to)])
			for ul in usage_closing:
				# if datetime.datetime.strptime(ul.inventory_id.date, '%Y-%m-%d %H:%M:%S').date() == datetime.datetime.strptime(date_to, '%Y-%m-%d').date():
				usage += ul.product_uom_qty

			closing_val = opening_val + purchase - usage

			# usage = purchase + opening_val - closing_val


			# usage_closing = self.env['stock.inventory.line'].search([('product_id','=',prd),('location_id','=',location.id),('inventory_id.state','=','done'),('inventory_id.date','>=',date_from),('inventory_id.date','<=',date_to)])
			# for ol in usage_closing:
			# 	if datetime.datetime.strptime(ol.inventory_id.date, '%Y-%m-%d %H:%M:%S').date() == datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date():
			# 		closing_val += ol.product_qty
			# 		opening_val += ol.theoretical_qty

			# usage = opening_val - closing_val


			dict = {}
			dict['product'] = self.env['product.product'].search([('id','=',prd)]).name
			dict['opening_stock'] = opening_val
			dict['purchase'] = purchase
			dict['usage'] = usage
			dict['avg_price'] = round((inventory_value/closing_val),2) if avg_count != 0 else 0
			dict['uom'] = self.env['product.product'].search([('id','=',prd)]).uom_id.name
			dict['inventory_value'] = inventory_value if avg_count !=0 else 0
			dict['closing_stock'] = closing_val
			if closing_val != 0:
				list.append(dict)
		return list


	@api.multi
	def print_product_usage_report(self):
		datas = {
		   'ids': self._ids,
		   'model': self._name,
		   'form': self.read(),
		   'context':self._context,
				}
		return{
		   'name' : 'Product Usage Report',
		   'type' : 'ir.actions.report.xml',
		   'report_name' : 'hrms.report_product_usage_report_template',
		   'datas': datas,
		   'report_type': 'qweb-pdf'
				}
			
	@api.multi
	def view_product_usage_report(self):
		datas = {
		   'ids': self._ids,
		   'model': self._name,
		   'form': self.read(),
		   'context':self._context,
	   }
		return{
		   'name' : 'Product Usage Report',
		   'type' : 'ir.actions.report.xml',
		   'report_name' : 'hrms.report_product_usage_report_template',
		   'datas': datas,
		   'report_type': 'qweb-html'
	   }