from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError



class TaxMapping(models.Model):
	_name = 'tax.mapping'
	_rec_name = "id"

	price_from = fields.Float(string="Price From")
	price_to = fields.Float(string="Price To")
	tax_id = fields.Many2one('account.tax',string="Tax")


	@api.model
	def create(self, vals):
		record = self.env['tax.mapping'].search([])
		for line in record:
			if vals.get('price_from') == line.price_from and vals.get('price_to') == line.price_to:
				raise UserError("Already Exist")
		return super(TaxMapping, self).create(vals)
	
	