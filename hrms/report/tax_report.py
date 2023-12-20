from datetime import datetime

from openerp import models, fields, api, _

class TaxReportWizard(models.TransientModel):
   _name = "tax.report.wizard"

   date_from = fields.Date('Date From', required=True)
   date_to = fields.Date('Date To', required=True)
   b2b=fields.Boolean(string='BTOB')
   b2c=fields.Boolean(string='BTOC')
   inter_state=fields.Boolean(string='Interstate')
   local=fields.Boolean(string='kerala')

   @api.onchange('b2c')
   def b2c_boolean(self):
      if self.b2c:
         self.b2b = False
         self.inter_state=False
         self.local=False


   @api.onchange('b2b')
   def b2b_boolean(self):
      if self.b2b:
         self.b2c = False
         self.inter_state = False
         self.local = False

   @api.onchange('inter_state')
   def  inter_state_boolean(self):
       if self.inter_state:
           self.local = False

   @api.onchange('local')
   def local_boolean(self):
       if self.local:
           self.inter_state = False



   @api.multi
   def print_b2b_tax_report(self):
       self.ensure_one()

       datas = {
           'ids': self._ids,
           'model': self._name,
           'form': self.read(),
           'context': self._context,
       }
       if self.b2b:
           data = self.env['ir.actions.report.xml'].search(
               [('model', '=', 'tax.report.wizard'),
                ('report_name', '=', 'hrms.report_b2b_tax_report_template',)])
           data.download_filename = 'B2B Tax report.pdf'
       elif self.b2c:
           data = self.env['ir.actions.report.xml'].search(
               [('model', '=', 'tax.report.wizard'),
                ('report_name', '=', 'hrms.report_b2b_tax_report_template',)])
           data.download_filename = 'B2C Tax report.pdf'
       else:
           data = self.env['ir.actions.report.xml'].search(
               [('model', '=', 'tax.report.wizard'),
                ('report_name', '=', 'hrms.report_b2b_tax_report_template',)])
           data.download_filename = 'Tax report.pdf'
       return {
           'type': 'ir.actions.report.xml',
           'report_name': 'hrms.report_b2b_tax_report_template',
           'datas': datas,
           'report_type': 'qweb-pdf',
       }

   @api.multi
   def get_tax_report_record(self):
       data_list = []

       def create_values_dict(rec):

           formatted_date = ''
           if rec.date_invoice:
               try:
                   date_obj = datetime.strptime(str(rec.date_invoice), '%Y-%m-%d')
                   formatted_date = date_obj.strftime('%d/%m/%Y')
               except ValueError:
                   pass

           return {
               'date':formatted_date,
               'customer_name': rec.partner_id.name,
               'cgst': rec.cgst,
               'sgst': rec.sgst,
               'igst': rec.igst,
               'total_tax': rec.amount_tax,
               'total': rec.amount_total
           }

       criteria = [
           ('type', '=', 'out_invoice'),
           ('date_invoice', '>=', self.date_from),
           ('date_invoice', '<=', self.date_to),
           ('state', 'in', ['paid', 'open']),
       ]

       if self.b2b:
           criteria.extend([('b2b', '=', True)])
           if self.inter_state:
               criteria.extend([('inter_state', '=', True)])
           elif self.local:
               criteria.extend([('local', '=', True)])

       elif self.b2c:
           criteria.extend([('b2c', '=', True)])
           if self.inter_state:
               criteria.extend([('inter_state', '=', True)])
           elif self.local:
               criteria.extend([('local', '=', True)])

       invoices = self.env['account.invoice'].search(criteria)

       for rec in invoices:
           values = create_values_dict(rec)
           data_list.append(values)
           print(data_list, 'data')

       return data_list

       # print(rec.date_invoice,rec.partner_id.name,rec.amount_tax,rec.cgst,rec.sgst,rec.igst,'print')