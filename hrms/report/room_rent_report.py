from openerp import models, fields, api, _
import dateutil.parser
import datetime
from datetime import datetime, date, time


class RoomRentReportWizard(models.TransientModel):
   _name = "room.rent.report.wizard"


   date_from = fields.Date('Date From',required=True)
   date_to = fields.Date('Date To',required=True)
   tax_type = fields.Selection([('5','5%'),
                              ('12','12%'),
                              ('18','18%'),
                              ('28','28%')
                              ], string="Tax Type", required=True)


   @api.multi
   def view_room_rent_report(self):
      self.ensure_one()

      datas = {
          'ids': self._ids,
          'model': self._name,
          'form': self.read(),
          'context':self._context,
         }
       
      return{
         'name' : 'Room Rent',
         'type' : 'ir.actions.report.xml',
         'report_name' : 'hrms.report_room_rent_template',
         'datas': datas,
         'report_type': 'qweb-html'
      }

   @api.multi
   def print_room_rent_report(self):
      self.ensure_one()

      datas = {
          'ids': self._ids,
          'model': self._name,
          'form': self.read(),
          'context':self._context,
         }
       
      return{
         'name' : 'Room Rent',
         'type' : 'ir.actions.report.xml',
         'report_name' : 'hrms.report_room_rent_template',
         'datas': datas,
         'report_type': 'qweb-pdf'
      }

   
   @api.multi
   def get_room_rent(self):
    list = []
    invoice = self.env['account.invoice'].search([('date_invoice','>=',self.date_from),('date_invoice','<=',self.date_to),('state','=','paid')])
    for inv_line in invoice:
      # print '------------------------------------------------------------------'
      total = 0
      taxable_value = 0
      gst = 0
      igst = 0
      jounals = ''
      journal_list = []

      # print 'inv_line.tax_line----------', inv_line.tax_line
      # if inv_line.tax_line:
      #     for taxes in inv_line.tax_line:
      #       print 'taxe111=--------------------------', taxes.tax_id.tax_type, taxes.tax_id.tax_based
      #       if taxes.tax_id.tax_type == self.tax_type:
      #         taxable_value += taxes.base
      #         if taxes.tax_id.tax_based == 'gst':
      #           gst += taxes.amount
      #         elif taxes.tax_id.tax_based == 'igst':
      #           igst += taxes.amount
      #         else:
      #           pass
      # else:
      #     taxable_value = inv_line.amount_total

      for line in inv_line.invoice_line:
        if line.product_id.room_status2 == True:
          for tax in line.invoice_line_tax_id:
            if tax.tax_type == self.tax_type:

              taxable_value = taxable_value + line.price_subtotal

              if tax.tax_based == 'gst':
                gst = gst + (line.price_subtotal * tax.amount)
              elif taxes.tax_based == 'igst':
                igst = igst + (line.price_subtotal * tax.amount)
              else:
                pass

      if taxable_value != 0:
        if inv_line.payment_ids:
          for payments in inv_line.payment_ids:
            if payments.journal_id.name not in journal_list:
              journal_list.append(payments.journal_id.name)
        for k in journal_list:
          # print 'jounals------------------------', jounals
          if jounals == '':
            jounals = k
          else:
            jounals = jounals + ',' + k

        date = dateutil.parser.parse(inv_line.date_invoice).date()
        dt = datetime.strftime(date, "%d/%m/%y")
        total = taxable_value + gst + igst
        list.append({
                     'date': dt,
                     'particulars': jounals,
                     'vch_type': 'Journal',
                     'bill_no': inv_line.number2,
                     'gst_no': inv_line.partner_id.gst_no,
                     'taxable_value': taxable_value,
                     'cgst': gst/2,
                     'sgst': gst/2,
                     'igst': igst,
                     'total': total,
                     'name': inv_line.partner_id.name,
                     })

    return list