from openerp.exceptions import except_orm, ValidationError
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp import models, fields, api, _
from openerp import workflow
import time
import datetime
#from datetime import datetime, timedelta
from datetime import date
#from openerp.osv import fields, osv
from openerp.tools.translate import _
#from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
#from openerp.osv import fields, osv
from datetime import timedelta
from docutils.nodes import line
from pychart.arrow import default


class RestaurantReport(models.TransientModel):
	_name = 'restaurant.report'


	date_from = fields.Date('Date From',required=True)
	date_to = fields.Date('Date To',required=True)
	tax_type = fields.Selection([('5','5 %'),
								 ('12','12 %'),
								 ('18','18 %'),
								 ('28','28 %')], 'Tax Type',required=True)


	@api.multi
	def get_restaurant_details(self,date_from,date_to,tax_type):
		list = []
		invoice = self.env['account.invoice.line'].search([('invoice_id.state','=','paid'),('product_id.product_tmpl_id.name','=','Restaurant Bill'),('invoice_id.date_invoice','>=',date_from),('invoice_id.date_invoice','<=',date_to)])
		if invoice:
			for line in invoice:
				for tax in line.invoice_line_tax_id:
					if tax.tax_type == tax_type:
						dict = {}
						dict['date'] = line.invoice_id.date_invoice
						dict['particulars'] = "Dr " + str(self.env['account.move.line'].search([('invoice_id','=',line.invoice_id.id)],limit=1).journal_id.name)
						dict['vch_type'] = "Sales"
						dict['bill_no'] = line.name
						dict['taxable_value'] = line.price_subtotal
						dict['cgst'] = round(line.cgst,2)
						dict['sgst'] = round(line.sgst,2)
						dict['total'] = round(line.amount_with_tax,2)
						dict['gst_no'] = line.invoice_id.partner_id.gst_no
						dict['name'] = line.name
						list.append(dict)
		return list


	@api.multi
	def print_restaurant_report(self):
		datas = {
		   'ids': self._ids,
		   'model': self._name,
		   'form': self.read(),
		   'context':self._context,
				}
		return{
		   'name' : 'Resturant Report',
		   'type' : 'ir.actions.report.xml',
		   'report_name' : 'hrms.report_restaurant_report_template',
		   'datas': datas,
		   'report_type': 'qweb-pdf'
				}
			
	@api.multi
	def view_restaurant_report(self):
		datas = {
		   'ids': self._ids,
		   'model': self._name,
		   'form': self.read(),
		   'context':self._context,
	   }
		return{
		   'name' : 'Resturant Report',
		   'type' : 'ir.actions.report.xml',
		   'report_name' : 'hrms.report_restaurant_report_template',
		   'datas': datas,
		   'report_type': 'qweb-html'
	   }


	# @api.multi
	# def get_purchase_register(self):
	# 	product_ids = []
	# 	list = []
	# 	invoice = self.env['account.invoice'].search([('purchase_order_date','>=',self.date_from),('purchase_order_date','<=',self.date_to)])
	# 	for inv_line in invoice:
	# 		round_off = 0
	# 		total = 0
	# 		taxable_0 = 0
	# 		taxable_5 = 0
	# 		taxable_12 = 0
	# 		taxable_18 = 0
	# 		taxable_28 = 0
	# 		gst_5 = 0
	# 		igst_5 = 0
	# 		gst_12 = 0
	# 		igst_12 = 0
	# 		gst_18 = 0
	# 		igst_18 = 0
	# 		gst_28 = 0
	# 		igst_28 = 0
	# 		for taxes in inv_line.tax_line:
	# 			if taxes.tax_id.tax_type == 5:
	# 			   taxable_5 += taxes.base
	# 			   if taxes.tax_id.tax_based == 'gst':
	# 				  gst_5 += taxes.base
	# 			   if taxes.tax_id.tax_based == 'igst':
	# 				  igst_5 += taxes.base
	# 			   else:
	# 				  pass
	# 			if taxes.tax_id.tax_type == 12:
	# 			   taxable_12 += taxes.base
	# 			   if taxes.tax_id.tax_based == 'gst':
	# 				  gst_12 += taxes.base
	# 			   if taxes.tax_id.tax_based == 'igst':
	# 				  igst_12 += taxes.base
	# 			   else:
	# 				  pass
	# 			if taxes.tax_id.tax_type == 18:
	# 			   taxable_18 += taxes.base
	# 			   if taxes.tax_id.tax_based == 'gst':
	# 				  gst_18 += taxes.base
	# 			   if taxes.tax_id.tax_based == 'igst':
	# 				  igst_18 += taxes.base
	# 			   else:
	# 				  pass
	# 			if taxes.tax_id.tax_type == 28:
	# 			   taxable_28 += taxes.base
	# 			   if taxes.tax_id.tax_based == 'gst':
	# 				  gst_28 += taxes.base
	# 			   if taxes.tax_id.tax_based == 'igst':
	# 				  igst_28 += taxes.base
	# 			   else:
	# 				  pass
	# 			list.append({
	# 					 'date': inv_line.purchase_order_date,
	# 					 'particulars': inv_line.partner_id.name,
	# 					 'vch_type': 'Purchase',
	# 					 'bill_no': 123,
	# 					 'gst_no': inv_line.partner_id.gst_no,
	# 					 'bill_amt': inv_line.amount_total,
	# 					 'taxable_0': taxable_0,
	# 					 'taxable_5': taxable_5,
	# 					 'taxable_12': taxable_12,
	# 					 'taxable_18': taxable_18,
	# 					 'taxable_28': taxable_28,
	# 					 'cgst_5': gst_5/2,
	# 					 'sgst_5': gst_5/2,
	# 					 'igst_5': igst_5,
	# 					 'cgst_12': gst_12/2,
	# 					 'sgst_12': gst_12/2,
	# 					 'igst_12': igst_12,
	# 					 'cgst_18': gst_18/2,
	# 					 'sgst_18': gst_18/2,
	# 					 'igst_18': igst_18,
	# 					 'cgst_28': gst_28/2,
	# 					 'sgst_28': gst_28/2,
	# 					 'igst_28': igst_28,
	# 					 'round_off': round_off,
	# 					 'total': total,
	# 					 })

	# 			return list