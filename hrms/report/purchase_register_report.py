from openerp import models, fields, api, _
import dateutil.parser
import datetime
from datetime import datetime, date, time



class PurchaseRegisterWizard(models.TransientModel):
   _name = "purchase.register.wizard"


   date_from = fields.Date('Date From',required=True)
   date_to = fields.Date('Date To',required=True)


   @api.multi
   def view_purchase_report(self):
      self.ensure_one()

      datas = {
          'ids': self._ids,
          'model': self._name,
          'form': self.read(),
          'context':self._context,
         }
       
      return{
         'name' : 'Purchase Register',
         'type' : 'ir.actions.report.xml',
         'report_name' : 'hrms.report_purchase_register_template',
         'datas': datas,
         'report_type': 'qweb-html'
      }

   @api.multi
   def print_purchase_report(self):
      self.ensure_one()

      datas = {
          'ids': self._ids,
          'model': self._name,
          'form': self.read(),
          'context':self._context,
         }
       
      return{
         'name' : 'Purchase Register',
         'type' : 'ir.actions.report.xml',
         'report_name' : 'hrms.report_purchase_register_template',
         'datas': datas,
         'report_type': 'qweb-pdf'
      }

   
   @api.multi
   def get_purchase_register(self):
      list = []
      invoice = self.env['account.invoice'].search([('type','=','in_invoice'),('purchase_order_date','>=',self.date_from),('purchase_order_date','<=',self.date_to),('state','in',['open','paid'])])
      # print 'invoice-----------------------------', invoice
      for inv_line in invoice:
        # print 'origin-------------------', inv_line.origin

        total = 0
        taxable_0 = 0
        taxable_5 = 0
        taxable_12 = 0
        taxable_18 = 0
        taxable_28 = 0
        gst_5 = 0
        igst_5 = 0
        gst_12 = 0
        igst_12 = 0
        gst_18 = 0
        igst_18 = 0
        gst_28 = 0
        igst_28 = 0
        # print 'inv_line.tax_line----------', inv_line.tax_line
        if inv_line.tax_line:
            for taxes in inv_line.tax_line:
              # print 'taxe111=--------------------------', taxes.tax_id.tax_type, taxes.tax_id.tax_based
              if taxes.tax_id.tax_type == '5':
                taxable_5 += taxes.base
                if taxes.tax_id.tax_based == 'gst':
                  gst_5 += taxes.amount
                elif taxes.tax_id.tax_based == 'igst':
                  igst_5 += taxes.amount
                else:
                  pass
              elif taxes.tax_id.tax_type == '12':
                taxable_12 += taxes.base
                if taxes.tax_id.tax_based == 'gst':
                  gst_12 += taxes.amount
                elif taxes.tax_id.tax_based == 'igst':
                  igst_12 += taxes.amount
                else:
                  pass
              elif taxes.tax_id.tax_type == '18':
                # print 'taxesamt-----------', taxes.amount
                taxable_18 += taxes.base
                if taxes.tax_id.tax_based == 'gst':
                  gst_18 += taxes.amount
                elif taxes.tax_id.tax_based == 'igst':
                  igst_18 += taxes.amount
                else:
                  pass
              elif taxes.tax_id.tax_type == '28':
                taxable_28 += taxes.base
                if taxes.tax_id.tax_based == 'gst':
                  gst_28 += taxes.amount
                elif taxes.tax_id.tax_based == 'igst':
                  igst_28 += taxes.amount
                else:
                  pass
              else:
                pass
        else:
            taxable_0 = inv_line.amount_total

        date = dateutil.parser.parse(inv_line.purchase_order_date).date()
        dt = datetime.strftime(date, "%d/%m/%y")
        total = taxable_0 + taxable_5 + taxable_12 + taxable_18 + taxable_28 + gst_5 + igst_5 + gst_12 + igst_12 + gst_18 + igst_18 + gst_28 + igst_28 + inv_line.round_off
        list.append({
                     'date': dt,
                     'particulars': inv_line.partner_id.name,
                     'vch_type': 'Purchase',
                     'bill_no': inv_line.purchase_bill_no,
                     'gst_no': inv_line.partner_id.gst_no,
                     'bill_amt': inv_line.amount_total,
                     'taxable_0': taxable_0,
                     'taxable_5': taxable_5,
                     'taxable_12': taxable_12,
                     'taxable_18': taxable_18,
                     'taxable_28': taxable_28,
                     'cgst_5': gst_5/2,
                     'sgst_5': gst_5/2,
                     'igst_5': igst_5,
                     'cgst_12': gst_12/2,
                     'sgst_12': gst_12/2,
                     'igst_12': igst_12,
                     'cgst_18': gst_18/2,
                     'sgst_18': gst_18/2,
                     'igst_18': igst_18,
                     'cgst_28': gst_28/2,
                     'sgst_28': gst_28/2,
                     'igst_28': igst_28,
                     'round_off': inv_line.round_off,
                     'total': total,
                     })

      return list



class account_invoice_tax1(models.Model):
    _inherit = "account.invoice.tax"
   
    tax_id = fields.Many2one('account.tax', string='tax')

    @api.v8
    def compute(self, invoice):
        tax_grouped = {}
        currency = invoice.currency_id.with_context(date=invoice.date_invoice or fields.Date.context_today(invoice))
        company_currency = invoice.company_id.currency_id
        for line in invoice.invoice_line:
            taxes = line.invoice_line_tax_id.compute_all(
                (line.price_unit * (1 - (line.discount or 0.0) / 100.0)),
                line.quantity, line.product_id, invoice.partner_id)['taxes']
            for tax in taxes:
                val = {
                    'invoice_id': invoice.id,
                    'name': tax['name'],
                    'tax_id': tax['id'],
                    'amount': tax['amount'],
                    'manual': False,
                    'sequence': tax['sequence'],
                    'base': currency.round(tax['price_unit'] * line['quantity']),
                }
                if invoice.type in ('out_invoice','in_invoice'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = currency.compute(val['base'] * tax['base_sign'], company_currency, round=False)
                    val['tax_amount'] = currency.compute(val['amount'] * tax['tax_sign'], company_currency, round=False)
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_collected_id']
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = currency.compute(val['base'] * tax['ref_base_sign'], company_currency, round=False)
                    val['tax_amount'] = currency.compute(val['amount'] * tax['ref_tax_sign'], company_currency, round=False)
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_paid_id']

                # If the taxes generate moves on the same financial account as the invoice line
                # and no default analytic account is defined at the tax level, propagate the
                # analytic account from the invoice line to the tax line. This is necessary
                # in situations were (part of) the taxes cannot be reclaimed,
                # to ensure the tax move is allocated to the proper analytic account.
                if not val.get('account_analytic_id') and line.account_analytic_id and val['account_id'] == line.account_id.id:
                    val['account_analytic_id'] = line.account_analytic_id.id

                key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        for t in tax_grouped.values():
            t['base'] = currency.round(t['base'])
            t['amount'] = currency.round(t['amount'])
            t['base_amount'] = currency.round(t['base_amount'])
            t['tax_amount'] = currency.round(t['tax_amount'])

        return tax_grouped
