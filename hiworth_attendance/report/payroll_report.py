from openerp import models, fields, api, _

class PayrollReport(models.TransientModel):
	_name = 'payroll.report'
	
	
	company_person_id = fields.Many2one('res.partner', string="Company")
	start_date = fields.Date('Start Date')
	end_date = fields.Date('End Date')
	
	@api.multi
	def print_xls_report(self):
		for rec in self:
			data = {}
			data['form'] = rec.read(['company_person_id', 'start_date', 'end_date'])
			return {'type': 'ir.actions.report.xml',
					'report_name': 'hiworth_attendance.report_payroll_report.xlsx',
					'datas': data
					}
	
	# def print_xls_report(self, cr, uid, ids, context=None):
	# rec = self.browse(data)
	# data = {}
	# data['form'] = rec.read(['sales_person', 'start_date', 'end_date'])
	# return self.env['report'].get_action(rec, 'crm_won_lost_report.report_crm_won_lost_report.xlsx',
	# 									 data=data)