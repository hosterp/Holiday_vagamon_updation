from openerp import models, fields, api, _
from datetime import date, timedelta as td
from datetime import datetime, date, time
import dateutil.parser


class DailyInvoiceWizard(models.Model):
    _name = 'daily.invoice.wizard'
    
    
    date_from = fields.Date('Date From',required=True)
    date_to = fields.Date('Date To',required=True)
    


    @api.multi
    def action_open_window2(self):
       

       datas = {
           'ids': self._ids,
           'model': self._name,
           'form': self.read(),
           'context':self._context,
       }
       
       return{
           'name' : 'Check In/Out Report',
           'type' : 'ir.actions.report.xml',
           'report_name' : 'hrms.report_daily_invoice_template',
           'datas': datas,
           'report_type': 'qweb-pdf'
       }

    @api.multi
    def action_open_window1(self):
       

       datas = {
           'ids': self._ids,
           'model': self._name,
           'form': self.read(),
           'context':self._context,
       }
       
       return{
           'name' : 'Check In/Out Report',
           'type' : 'ir.actions.report.xml',
           'report_name' : 'hrms.report_daily_invoice_template',
           'datas': datas,
           'report_type': 'qweb-html'
       }   



    @api.multi
    def get_daily_invoice_details(self):

        list = []
        dt1 = datetime.strptime(self.date_to, "%Y-%m-%d").date()
        dt2 = datetime.strptime(self.date_from, "%Y-%m-%d").date()
        delta = dt1 - dt2
        for i in range(delta.days + 1):
            room_advance_amt = service_amt = restaurant_amt = out_amt = 0
            date = dt2 + td(days=i)


            advance = self.env['reservation.advance'].search([('date','=',date)])
            for advance_id in advance:
              room_advance_amt += advance_id.amount

            service = self.env['service.invoice'].search(['|',('state','=','paid'),('state','=','credited'),('date','=',date)])
            for service_id in service:
              for line in service_id.line_ids:
                service_amt += line.sub_total

            restaurant = self.env['hotel.restaurant.order'].search(['|',('state','=','credited'),('state','=','payed'),('o_date','=',date)])
            for restaurant_id in restaurant:
                restaurant_amt += restaurant_id.amount_total

            # out = self.env['hotel.folio'].search([])
            # for out_id in out:
            #   date_out = dateutil.parser.parse(out_id.checkout_date).date()
            #   if date_out == date and out_id.reservation_id.state == 'checkout':
            #     out_amt += out_id.last_total

            out = self.env['account.invoice'].search([('date_invoice','=',date)])
            for out_id in out:
              for ids in out_id.invoice_line:
                if ids.product_id.isroom == True:
                  out_amt += ids.price_subtotal

            # print "333333333333333333333333333"
            # dateutil.parser.parse(self.env['hotel.folio'].search([('id','=',1)]).date_order).date()
            check_out = self.env['hotel.folio'].search([('date_folio3','=',date),('invoiced','=',True)])
            tot = 0
            for recs in check_out:
              print "dateeeeeeeeeeeeeeeeeeee", recs.date_folio3
              for rec in recs.room_lines:
                tot += rec.total_with_tax
                # print "hcdvefjkdmedrrrrrrrrrrrrrrrrrrrrrrrrrr", rec.name
            # print "totttttttttttttttt", check_out

            # list1 = []
            # check_out = self.env['hotel.folio'].search([])
            # for record in check_out:
            #   if dateutil.parser.parse(record.date_order).date() not in list1:
            #     list1.append(dateutil.parser.parse(record.date_order).date())
            # print "11111111111111111111111111",tot


            list.append({
                        'date': date,
                        'room_advance_amt' : room_advance_amt,
                        'service_amt' : service_amt,
                        'restaurant_amt' : restaurant_amt,
                        'out_amt' : tot,
                        'total' : room_advance_amt + restaurant_amt + service_amt + tot
                    })

        return list

