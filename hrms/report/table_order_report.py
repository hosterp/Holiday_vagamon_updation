from openerp import models, fields, api, _



class RestaurantTableOrderWizard(models.Model):
    _name = 'restaurant.table_order.wizard'

   
    date_from = fields.Date('Date From',required=True)
    date_to = fields.Date('Date To',required=True)
    state_done = fields.Boolean('Done')
    state_paid = fields.Boolean('Paid')
    state_credited = fields.Boolean('Credited')
    state_nc = fields.Boolean('Non Chargable')
    state = fields.Selection([
                        ('all','All'),
                        ('paid','Paid'),
                        ('credited','Credited'),
                        ], string='State',default='all',required=True)
    


    @api.multi
    def action_open_window(self):
       

       datas = {
           'ids': self._ids,
           'model': self._name,
           'form': self.read(),
           'context':self._context,
       }
       
       return{
           'name' : 'Table Order Details Report',
           'type' : 'ir.actions.report.xml',
           'report_name' : 'hrms.report_table_order_template',
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
           'name' : 'Table Order Details Report',
           'type' : 'ir.actions.report.xml',
           'report_name' : 'hrms.report_table_order_template',
           'datas': datas,
           'report_type': 'qweb-html'
       }

    @api.multi
    def get_details(self):
        
        list = []
        ids = []
        if self.state_done == True:
            orders1 = self.env['hotel.restaurant.order'].search([('state','=','done'),('o_date','>=',self.date_from),('o_date','<=',self.date_to)])
            for order1 in orders1:
              ids.append(order1.id)
        if self.state_paid == True:
            orders2 = self.env['hotel.restaurant.order'].search([('state','=','payed'),('o_date','>=',self.date_from),('o_date','<=',self.date_to)])
            for order2 in orders2:
              ids.append(order2.id)

        if self.state_credited == True:
            orders3 = self.env['hotel.restaurant.order'].search([('state','=','credited'),('o_date','>=',self.date_from),('o_date','<=',self.date_to)])
            for order3 in orders3:
              ids.append(order3.id)

        if self.state_nc == True:
            orders4 = self.env['hotel.restaurant.order'].search([('state','=','nc'),('o_date','>=',self.date_from),('o_date','<=',self.date_to)])
            for order4 in orders4:
              ids.append(order4.id)


        orders = self.env['hotel.restaurant.order'].search([('id','in',ids)])
        for order in orders:

            list.append({
                    'cname': order.cname,
                    'order_date': order.o_date,
                    'order_no': order.order_no,
                    'room_no':order.room_no,
                    'waiter': order.waiter_name,
                    'state' : order.state,
                    'bill_no': order.bill_no,
                    'total': order.amount_total,
                    })

        return list

