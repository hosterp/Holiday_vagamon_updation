from openerp import models, fields, api


class MealPlan(models.Model):
	_name = 'meal.plan'

	name = fields.Char('Name')
	adult_rate = fields.Float('Adult Rate')
	child_rate = fields.Float('Child(6-12) Rate')
	tax_id = fields.Many2one('account.tax',string="Tax")