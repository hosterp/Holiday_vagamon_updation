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
from openerp.osv import osv
from datetime import timedelta
from docutils.nodes import line
from pychart.arrow import default
from openerp.osv import expression
from lxml import etree
import dateutil.parser
import pytz

class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'


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

	invoice_no = fields.Char('Bill No')

	
	@api.multi
	def button_confirm(self):
		for rec in self:
			rec.wkf_confirm_order()
			rec.wkf_approve_order()
			rec.action_invoice_create()
			rec.action_picking_create()
			for pick in rec.picking_ids:
				pick.do_transfer()
			for inv in rec.invoice_ids:
				inv.invoice_validate()
			rec.picking_done()
			rec.wkf_po_done()

	@api.multi
	@api.depends('order_line')
	def get_tax_amount(self):
		for records in self:
			igst = 0
			gst = 0
			for lines in records.order_line:
				gst += lines.gst_tax
				igst += lines.igst_tax
			records.cgst = gst/2
			records.sgst = gst/2
			records.igst = igst
	igst = fields.Float(compute='get_tax_amount', store=True, string="IGST")
	cgst = fields.Float(compute='get_tax_amount', store=True, string="IGST")
	sgst = fields.Float(compute='get_tax_amount', store=True, string="IGST")


class purchaseOrderLine(models.Model):
	_inherit = 'purchase.order.line'

	gst_tax = fields.Float(compute="_compute_tax_based", store=True, string='GST Tax')
	igst_tax = fields.Float(compute="_compute_tax_based", store=True, string='IGST Tax')
	# hsn_code = fields.Char(related='product_id.product_tmpl_id.hsn_code', store=True, string='HSN Code')

	@api.one
	@api.depends('price_subtotal','product_qty','price_unit','taxes_id')
	def _compute_tax_based(self):
		gst = 0
		igst = 0
		for tax in self.taxes_id:
			if tax.tax_based == 'gst':
				gst += tax.amount
			if tax.tax_based == 'igst':
				igst += tax.amount
		print "gst_tax=================", gst, self.price_subtotal
		self.gst_tax = gst * self.price_subtotal
		self.igst_tax = igst * self.price_subtotal


	

