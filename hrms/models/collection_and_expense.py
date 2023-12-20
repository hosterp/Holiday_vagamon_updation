from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning


class CollectionAndExpense(models.Model):
	_name = 'collection.and.expense'
	_rec_name = 'date_collect'

	date_collect = fields.Date("Date")
	collection_ids = fields.One2many('collection.line','collection_expense_id','Collections')
	expense_ids = fields.One2many('expense.line','collection_expense_id','Expenses')
	state = fields.Selection([('open','Open'),('closed','Closed')],default='open',string='Status')
	total_collection = fields.Float("Total Collections", compute='_compute_total',store=True)
	total_expense = fields.Float("Total Expenses", compute='_compute_total',store=True)
	total = fields.Float("Total")



	@api.depends('collection_ids','expense_ids')
	def _compute_total(self):
		for rec in self:
			collection = 0.0
			expense = 0.0
			total = 0.0
			for collect in rec.collection_ids:
				collection += collect.amount
			for expe in rec.expense_ids:
				expense += expe.amount

			rec.total_collection = collection
			rec.total_expense = expense
			rec.total = collection - expense



	@api.multi
	def action_close(self):
		for rec in self:
			rec.state = 'closed'

	@api.model
	def create(self,vals):

		if vals.get('date_collect',False):
			if self.search([('date_collect','=',vals.get('date_collect')),('state','=','open')]):
				raise Warning(_('Already a record in Open State'))
		res = super(CollectionAndExpense , self).create(vals)
		return res


class CollectionLine(models.Model):
	_name = 'collection.line'

	desc = fields.Char("Description")
	amount = fields.Float("Amount")
	collection_expense_id = fields.Many2one('collection.and.expense','Collection and Expense')


class ExpenseLine(models.Model):
	_name = 'expense.line'

	desc = fields.Char("Description")
	amount = fields.Float("Amount")
	collection_expense_id = fields.Many2one('collection.and.expense','Collection and Expense')