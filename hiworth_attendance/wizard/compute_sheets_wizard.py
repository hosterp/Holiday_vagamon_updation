from openerp import models, fields, api, _

class ComputeSheetWizard(models.TransientModel):
    _name = 'compute.sheet.wizard'\
    
    
    
    @api.multi
    def action_submit(self):
        active_model = self._context.get('active_model')
        active_ids = self._context.get('active_ids')
        if active_model == 'hr.payslip':
            for active in active_ids:
                active_id = self.env['hr.payslip'].browse(active)
                active_id.compute_sheet()
            return True
    