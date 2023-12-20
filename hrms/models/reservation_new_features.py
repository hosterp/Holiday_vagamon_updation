from openerp.exceptions import except_orm, ValidationError
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp import models, fields, api, _
from openerp import workflow
import time
import datetime
# from datetime import datetime, timedelta
from datetime import date
# from datetime import datetime
# from openerp.osv import fields, osv
from openerp.tools.translate import _
# from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
# from openerp.osv import fields, osv
from datetime import timedelta, datetime
from docutils.nodes import line
from pychart.arrow import default
# from pygments.lexer import _inherit
from lxml import etree
from dateutil.relativedelta import relativedelta



class room_type_reservation(models.Model):
    _name = 'room.type.reservation'
    _description = 'Reservation Based on Type'

#     @api.multi
#     @api.depends('room_type_id', 'check_in', 'check_out')
#     def _compute_available_rooms(self):
#         for line in self:
#             if line.room_type_id.id != False:

#                 checkin = line.reservation_id.checkin
#                 # mytime = datetime.strptime(checkin, "%Y-%m-%d %H:%M:%S")
#                 # mytime += timedelta(hours=5, minutes=30)
# #                 print mytime.strftime("%Y.%m.%d %H:%M:%S")
#                 # check_in = mytime.strftime("%Y-%m-%d %H:%M:%S")

#                 checkout = line.reservation_id.checkout
#                 # mytime = datetime.strptime(checkout, "%Y-%m-%d %H:%M:%S")
#                 # mytime += timedelta(hours=5, minutes=30)
# #                 print mytime.strftime("%Y.%m.%d %H:%M:%S")
#                 # check_out = mytime.strftime("%Y-%m-%d %H:%M:%S")

#                 line.check_in = datetime.strptime(line.reservation_id.checkin, '%Y-%m-%d').date()
#                 line.check_out = datetime.strptime(line.reservation_id.checkout, '%Y-%m-%d').date()


#                 room_reserved = 0
#                 reserve_list = []
#                 reserve_lines = self.search([('room_type_id', '=', line.room_type_id.id)])
#                 reserve_list = [reserv.id for reserv in reserve_lines]
# #                 print 'reserv_lines ====================', reserve_lines,reserve_list

#                 if reserve_list == []:
#                     print 'test=============1'
#                     line.room_available = line.room_type_id.room_no
# #                     print 'test=================2'
#                 if reserve_list != []:
#                     for lines in reserve_lines:

#                         if (lines.check_in <= line.check_in <
#                             lines.check_out) or (lines.check_in <
#                                                 line.check_out <=
#                                                 lines.check_out):
#                             room_reserved += lines.nos
#                         if (lines.check_in > line.check_in) and (lines.check_out < line.check_out):
#                             room_reserved += lines.nos
#                     line.room_available = line.room_type_id.room_no - room_reserved

    room_type_id = fields.Many2one('hotel.room.type', string='Room id')
    nos = fields.Integer('No of Rooms')
    check_in = fields.Date(string='Check In Date')
    check_out = fields.Date(string='Check Out Date')
    state = fields.Selection([('assigned', 'Assigned'),
                              ('unassigned', 'Unassigned')], 'Status')
    reservation_id = fields.Many2one('hotel.reservation', ondelete='cascade',
                           string='Reservation')
    status = fields.Selection([('assigned', 'Assigned'),
                              ('unassigned', 'Unassigned')],string='state')
    room_available = fields.Integer(store=True, string="Rooms Available")


class ProductCategory(models.Model):
    _inherit = "product.category"

    product_ids = fields.One2many('product.product', 'categ_id', 'products')
    company_id = fields.Many2one('res.company', 'Company', required=True)
    extra_adult = fields.Float(string='Extra Adult Rate')
    extra_child = fields.Float(string='Extra Children Rate') 
    rate = fields.Float('Rate')

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
        }

class HotelRoomType(models.Model):
    _inherit = "hotel.room.type"


    @api.multi
    @api.depends('product_ids')
    def _compute_room_nos(self):
#         print 'test===================================4'
        for line in self:
            line.room_no = 0
#             print 'aaaaaaaaaaaaaaaaaaaaaaaaa', line
            for lines in line.product_ids:
                line.room_no += 1

    reservation_ids = fields.One2many('room.type.reservation', 'room_type_id', 'Reservations')
#     room_ids = fields.One2many(related='cat_id.', 'categ_id', 'Rooms')
    room_no = fields.Integer(compute='_compute_room_nos', string="Total Rooms")
    company_id = fields.Many2one('res.company', 'Company', required=True)
    tax_ids = fields.Many2many('account.tax','hotel_room_tax_rel','room_type_id','tax_id',string="Taxes")
    capacity = fields.Float('Capacity')

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
        }


class HotelFloor(models.Model):
    _inherit = "hotel.floor"

    company_id = fields.Many2one('res.company', 'Company', required=True)

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
        }

class res_company(models.Model):
    _inherit = "res.company"

    code = fields.Char('Code', size=5)
    signature = fields.Html('Company Signature')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    gst_no = fields.Char('GST No')
    country_id = fields.Many2one('res.country', 'Country', ondelete='restrict', default=105)
    agency = fields.Boolean('Agency')



    @api.model
    def create(self, vals):
        if vals.get('website'):
            vals['website'] = self._clean_website(vals['website'])
        if vals.get('name'):
            vals['name'] = vals.get('name').upper()
        if vals.get('street'):
            vals['street'] = vals.get('street').upper()
        if vals.get('street2'):
            vals['street2'] = vals.get('street2').upper()
        if vals.get('city'):
            vals['city'] = vals.get('city').upper()
        partner = super(ResPartner, self).create(vals)
        self._fields_sync(partner, vals)
        self._handle_first_contact_creation(partner)
        return partner


class ResCompany(models.Model):
    _inherit = 'res.company'

    gst_no = fields.Char('GST No')
    invoice_declaration = fields.Text('Invoice Declaration')
    pan_no = fields.Char('PAN No')
    menu_card = fields.Binary('Restaurant Menucard')
    filename = fields.Char('Filename')
    cutoff_date = fields.Integer('Customer lead time for Advance Payment')
    # grc_no = fields.Char('GRC No')
    restaurant_tax_id = fields.Many2one('account.tax',
         string="Taxes")
    restaurant_income_account = fields.Many2one('account.account', string="Restaurant Default Income Account", domain=[('type','=','other')])
    round_odd_account = fields.Many2one('account.account', string="Round Off Account", domain=[('type','=','other')])

class CheckSummary(models.Model):
    _name = 'checkin.checkout.summary'

    date_from = fields.Date('Period From',required=True)
    date_to = fields.Date('Period To',required=True)

    @api.multi
    def check_summary(self):


       datas = {
           'ids': self._ids,
           'model': self._name,
           'form': self.read(),
           'context':self._context,
       }

       return{
           'name' : 'Check In/Out Summary',
           'type' : 'ir.actions.report.xml',
           'report_name' : 'hrms.report_checkin_checkout_template',
           'datas': datas,
           'report_type': 'qweb-html'
       }

    @api.multi
    def get_header(self):
        date_range_list = []
        summary_header_list = []
        d_frm_obj = datetime.strptime(self.date_from, "%Y-%m-%d")
        d_to_obj = datetime.strptime(self.date_to, "%Y-%m-%d")
        temp_date = d_frm_obj
        while(temp_date <= d_to_obj):
            val = ''
            val = (
                   str(temp_date.strftime("%b")) + ' ' +
                   str(temp_date.strftime("%d")))
            summary_header_list.append({'summary':val})
            date_range_list.append(temp_date.strftime
                                   (DEFAULT_SERVER_DATETIME_FORMAT))
            temp_date = temp_date + timedelta(days=1)
        return summary_header_list

    @api.multi
    def get_body(self):
        room_ids = []
        reserve = []
        rooms = self.env['hotel.room.reservation.line'].search([])
        for room in rooms:
            if room.room_id.id not in room_ids:
                room_ids.append(room.room_id.id)
        for line in room_ids:
            r = self.env['hotel.room'].search([('id','=',line)])
            reserve.append({'room':r.name,'room_id':r.id,})
        # print "resereeeeeeeeeeeeeeeeeeeeeeee", reserve

        return reserve

    @api.multi
    def get_body_val(self,room_id):
        date_range_list = []
        reserve = []
        rooms = self.env['hotel.room.reservation.line'].search([('room_id','=',room_id)])
        d_frm_obj = datetime.strptime(self.date_from, "%Y-%m-%d")
        d_to_obj = datetime.strptime(self.date_to, "%Y-%m-%d")
        temp_date = d_frm_obj
        while(temp_date <= d_to_obj):
            date_range_list.append(temp_date.strftime
                                   (DEFAULT_SERVER_DATETIME_FORMAT))
            temp_date = temp_date + timedelta(days=1)
        for date in date_range_list:
            flag = 0
            b = 0
            a = ''
            for room in rooms:
                check_in = (datetime.strptime(room.check_in, '%Y-%m-%d %H:%M:%S')+timedelta(days=1)).strftime('%Y-%m-%d 00:00:00')
                check_out = (datetime.strptime(room.check_out, '%Y-%m-%d %H:%M:%S')+timedelta(days=1)).strftime('%Y-%m-%d 00:00:00')
                if date > check_in and date < check_out:
                    flag = 1
                    reserve.append({'state':'****'})
                if date < check_out and date == check_in:
                    flag = 1
                    if b == 0:
                        reserve.append({'state':'---'+' '+':'+' '+(room.reservation_id.checkin_time if room.reservation_id.checkin_time else '---')})
                    if b == 1:
                        reserve.append({'state':a+':'+(room.reservation_id.checkin_time if room.reservation_id.checkin_time else '---')})
                        b = 0
                        a = ''
                elif date == check_out:
                    b = 1
                    a = room.reservation_id.folio_id.checkout_time if room.reservation_id.folio_id.checkout_time else '---'
            if flag == 0 and b != 1:
                reserve.append({'state':'Free'})
            if b ==1 and a != '':
                reserve.append({'state':a+' '+':'+' '+'---'})

        return reserve




class RoomReservationSummary(models.Model):
    _inherit = 'room.reservation.summary'


    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = models.Model.fields_view_get(self, cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            for sheet in doc.xpath("//sheet"):
                parent = sheet.getparent()
                index = parent.index(sheet)
                for child in sheet:
                    parent.insert(index, child)
                    index += 1
                parent.remove(sheet)
            res['arch'] = etree.tostring(doc)
        return res

    @api.onchange('date_from', 'date_to')
    def get_room_summary(self):
        '''
        @param self: object pointer
         '''
        res = {}
        all_detail = []
        room_obj = self.env['hotel.room']
        reservation_line_obj = self.env['hotel.room.reservation.line']
        folio_room_line_obj = self.env['folio.room.line']
        date_range_list = []
        main_header = []
        summary_header_list = ['Rooms']
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise except_orm(_('User Error!'),
                                 _('Please Check Time period Date \
                                 From can\'t be greater than Date To !'))
            d_frm_obj = (datetime.strptime
                         (self.date_from, DEFAULT_SERVER_DATETIME_FORMAT))
            d_to_obj = (datetime.strptime
                        (self.date_to, DEFAULT_SERVER_DATETIME_FORMAT))
            temp_date = d_frm_obj
            while(temp_date <= d_to_obj):
                val = ''
                val = (str(temp_date.strftime("%a")) + ' ' +
                       str(temp_date.strftime("%b")) + ' ' +
                       str(temp_date.strftime("%d")))
                summary_header_list.append(val)
                date_range_list.append(temp_date.strftime
                                       (DEFAULT_SERVER_DATETIME_FORMAT))
                temp_date = temp_date + timedelta(days=1)
            all_detail.append(summary_header_list)
            room_ids = room_obj.search([])
            all_room_detail = []
            for room in room_ids:
                room_detail = {}
                room_list_stats = []
                room_detail.update({'name': room.name or ''})
                if not room.room_reservation_line_ids and \
                   not room.room_line_ids:
                    for chk_date in date_range_list:
                        room_list_stats.append({'state': 'Free',
                                                'date': chk_date})
                else:
                    for chk_date in date_range_list:
                        reserline_ids = room.room_reservation_line_ids.ids
                        reservline_ids = (reservation_line_obj.search
                                          ([('id', 'in', reserline_ids),
                                            ('check_in', '<=', chk_date),
                                            ('check_out', '>', chk_date),
                                            ('status', '=', 'confirm')
                                            ]))
                        reservline_ids2 = (reservation_line_obj.search
                                          ([('id', 'in', reserline_ids),
                                            ('check_in', '<=', chk_date),
                                            ('check_out', '>', chk_date),
                                            ('status', '=', 'confirm')
                                            ]))
                        fol_room_line_ids = room.room_line_ids.ids
                        chk_state = ['draft', 'cancel']
                        folio_resrv_ids = (reservation_line_obj.search
                                           ([('id', 'in', reserline_ids),
                                             ('check_in', '<=', chk_date),
                                             ('check_out', '>', chk_date),
                                             ('status', 'not in', chk_state)
                                             ]))
                        # folio_resrv_ids = (folio_room_line_obj.search
                        #                    ([('id', 'in', fol_room_line_ids),
                        #                      ('check_in', '<=', chk_date),
                        #                      ('check_out', '>=', chk_date),
                        #                      ('status', 'not in', chk_state)
                        #                      ]))
                        block_ids = (reservation_line_obj.search
                                          ([('id', 'in', reserline_ids),
                                            ('check_in', '<=', chk_date),
                                            ('check_out', '>', chk_date),
                                            ('status', '=', 'block')
                                            ]))
                        done_ids = (reservation_line_obj.search
                                          ([('id', 'in', reserline_ids),
                                            ('check_in', '<=', chk_date),
                                            ('check_out', '>', chk_date),
                                            ('status', '=', 'done')
                                            ]))
                        dirty_ids = (reservation_line_obj.search
                                          ([('id', 'in', reserline_ids),
                                            ('check_in', '<=', chk_date),
                                            ('check_out', '>', chk_date),
                                            ('state', '=', 'dirty')
                                            ]))

                        maintenance_ids = (reservation_line_obj.search
                                          ([('id', 'in', reserline_ids),
                                            ('check_in', '<=', chk_date),
                                            ('check_out', '>=', chk_date),
                                            ('state', '=', 'block')
                                            ]))
                        

                        if reservline_ids or reservline_ids2 or maintenance_ids:
                            
                            if maintenance_ids:
                                room_list_stats.append({'state': 'Maintenance',
                                                    'date': chk_date,
                                                    'room_id': room.id,

                                                   })
                            else:
                                room_list_stats.append({'state': 'Dirty' if dirty_ids else 'Reserved',
                                                    'date': chk_date,
                                                    'room_id': room.id,
                                                    'is_draft': 'No',
                                                    'data_model': '',
                                                    'data_id': 0})
                        elif block_ids:
                            room_list_stats.append({'state': 'Dirty' if dirty_ids else 'Blocked',
                                                    'date': chk_date,
                                                    'room_id': room.id})
                        elif done_ids:
                            room_list_stats.append({'state': 'Dirty' if dirty_ids else 'Occupied',
                                                    'date': chk_date,
                                                    'room_id': room.id})
                        elif dirty_ids:
                            room_list_stats.append({'state': 'Dirty',
                                                    'date': chk_date,
                                                    'room_id': room.id})
                        else:
                            room_list_stats.append({'state': 'Free',
                                                    'date': chk_date,
                                                    'room_id': room.id})

                room_detail.update({'value': room_list_stats})
                all_room_detail.append(room_detail)
            main_header.append({'header': summary_header_list})
            self.summary_header = str(main_header)
            self.room_summary = str(all_room_detail)
        return res



class CountryState(models.Model):
    _inherit = 'res.country.state'

    country_id = fields.Many2one('res.country', 'Country', required=False)
    code = fields.Char('State Code', size=3, help='The state code in max. three chars.', required=False)

class ServiceInvoice(models.Model):
    _name = 'service.invoice'


    @api.multi
    @api.onchange('room_no')
    def _from_room_no(self):
        DATE_FORMAT = "%Y-%m-%d"
        for record in self:
            if not record.room_no:
                    room_ids = []
                    reservations = self.env['hotel.room.reservation.line'].search([('status','=','done')])
                    room_ids = [reserve.room_id.id for reserve in reservations]
                    return {
                        'domain': {
                            'room_no':[('id','=', room_ids)]
                        }
                    }
            if record.room_no:
                record.partner_id=False
                record.folio_id = False
                reserve_id = False
                for val in record.room_no.room_reservation_line_ids:
                    if val.status == 'done':
                        date_field1 = datetime.strptime(val.check_in, DATE_FORMAT)+timedelta(hours=5,minutes=30)
                        date_field2 = datetime.strptime(val.check_out, DATE_FORMAT)+timedelta(hours=5,minutes=30)
                        check_in = date_field1.strftime("%Y-%m-%d")
                        check_out = date_field2.strftime("%Y-%m-%d")
                        # if self.o_date ==
                        if self.date >= check_in and self.date <= check_out:
                            reserve_id = val.reservation_id
                if reserve_id:
                    record.folio_id = reserve_id.folio_id.id
                    record.partner_id = reserve_id.partner_id.id
                else:
                    raise except_orm(_('Error'),_('There is no any guest in this specified room for this specified date'))

    @api.multi
    @api.depends('line_ids')
    def compute_total_amount(self):
        for line in self:
            for lines in line.line_ids:
                line.total_amount += lines.sub_total

    @api.multi
    @api.depends('seq')
    def compute_name(self):
        for rec in self:
            rec.name = 'S/'+str(rec.seq)

    name = fields.Char(compute='compute_name', string='Bill No')
    seq = fields.Integer('Sequence')
    date = fields.Date('Date', default=datetime.now())
    partner_id = fields.Many2one('res.partner', 'Guest')
    type = fields.Char('Status')
    room_no = fields.Many2one('hotel.room', 'Room No')
    folio_id = fields.Many2one('hotel.folio', 'Folio')
    line_ids = fields.One2many('service.invoice.line', 'invoice_id', 'Lines')
    is_hotel_guest = fields.Boolean('Is Guest', default=1)
    # therapist1 = fields.Many2one('res.partner', 'Therapist-1')
    # therapist2 = fields.Many2one('res.partner', 'Therapist-2')
    state = fields.Selection([('draft', 'Draft'),('cancel', 'Cancelled'),
                              ('paid', 'Paid'),('credited', 'Credited')],
                             'State', select=True, required=True,
                             readonly=True, default=lambda * a: 'draft')
    status = fields.Selection(related='folio_id.reservation_id.state', store=True, string="Status")
    total_amount = fields.Float(compute='compute_total_amount', string="Total Amount")

    @api.model
    def create(self,vals):
        invoice = self.env['service.invoice'].search([], order='seq desc', limit=1)
            # print 'order======================', order.seq, asd
        if not invoice:
            vals['seq'] = 1
        else:
            vals['seq'] = invoice.seq + 1 
        result = super(ServiceInvoice, self).create(vals)
        return result


    @api.multi
    def unlink(self):
        for rec in self:
            up = self.env['service.invoice'].search([('seq','>',rec.seq)], order='seq desc')
            if up:
                for line in up:
                    line.seq -= 1
        result = super(ServiceInvoice, self).unlink()


    @api.multi
    def done_paid(self):

        invoice_line_obj = self.env['account.invoice.line']
        invoice_obj = self.env['account.invoice']

        for invoice in self:
            values2 = {   'reference': invoice.name,
                          'internal_number': invoice.name,
                          'date_invoice': date.today().strftime('%Y-%m-%d'),
                          'date_due': date.today().strftime('%Y-%m-%d'),
                          'partner_id': invoice.partner_id.id,
                          'origin': invoice.name,
                          'account_id': invoice.partner_id.property_account_receivable.id,
                          }
            acc_id=invoice_obj.create(values2)
            for lines in invoice.line_ids:
                taxes_ids = []
                taxes_ids = [tax.id for tax in lines.tax_ids]
                values1 = {   'origin': invoice.name,
                              'partner_id': invoice.partner_id.id,
                              'name': invoice.name,
                              'product_id': lines.product_id.id,
                              'account_id': self.env['ir.property'].get('property_account_income_categ', 'product.category').id,
                              'quantity': lines.qty,
                              'price_unit': lines.price_unit,
                              'invoice_id': acc_id.id,
                              'date_service':invoice.date,
                              'invoice_line_tax_id': [(6, 0, taxes_ids)],
                              }
                line_id = invoice_line_obj.create(values1)
            invoice_obj2 = self.env['account.invoice'].browse(acc_id.id)
            invoice_obj2.action_date_assign()
            invoice_obj2.action_move_create()
            invoice_obj2.action_number()
            invoice_obj2.invoice_validate()
        self.write({'state': 'paid'})
        return True

    @api.multi
    def done_credited(self):
        hotel_folio_obj = self.env['hotel.folio']
        hsl_obj = self.env['hotel.service.line']

        for invoice in self:
            if invoice.folio_id:
                for lines in invoice.line_ids:
                    taxes_ids = []
                    taxes_ids = [tax.id for tax in lines.tax_ids]
                    values = {'name': invoice.name,
                              'product_id':lines.product_id.id,
                              'product_uom_qty': lines.qty,
                              'price_unit': lines.price_unit,
                              'tax_id': [(6, 0, taxes_ids)],
                              'date_order':invoice.date,
                              'folio_id': invoice.folio_id.id,
                              'is_service': True,
                              }
                    hsl_obj.create(values)
            self.write({'state': 'credited'})
        return True


    @api.multi
    def action_cancel(self,final=False):
            if self.state == 'paid':
                invoice_record = self.env['account.invoice'].search([('reference','=',self.name)])
                invoice_record.internal_number = ''
                invoice_record.unlink()

            if self.state == 'credited':
                folio_record = self.env['hotel.folio'].search([('id','=',self.folio_id.id)])
                if final == False:
                    if folio_record.state == 'manual' or folio_record.state == 'progress':
                        raise except_orm(_('Warning'),_('The Guest related to this bill is already Checked Out'))
                for lines in folio_record.service_lines:
                    if lines.name == self.name:
                        lines.state = 'draft'
                        lines.unlink()

            self.write({'state': 'draft'})
            return True


class ServiceInvoiceLine(models.Model):
    _name = 'service.invoice.line'

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.price_unit = self.product_id.lst_price
            self.tax_ids = self.product_id.taxes_id


    @api.one
    @api.depends('price_unit', 'tax_ids', 'tax', 'qty', 'product_id')
    def _compute_price(self):
        for line in self:
            line.total = 0.0
            tax = 0
            included = False
            for lines in line.tax_ids:
                tax += lines.amount
                if lines.price_include == True:
                    included = True
            if included == False:
	            line.sub_total = (1 + tax)*line.price_unit*line.qty
	            line.cgst = (tax * line.price_unit * line.qty) / 2
	            line.sgst = (tax * line.price_unit * line.qty) / 2
	            line.total = line.sub_total + line.cgst + line.sgst
            if included == True:
            	line.sub_total = (line.price_unit*line.qty)/(1+tax)
            	line.cgst = (tax * line.sub_total) / 2
             	line.sgst = (tax * line.sub_total) / 2
             	line.total = line.price_unit*line.qty

    name = fields.Char('Name')
    product_id = fields.Many2one('product.product', 'Particulars', domain=[('is_hotel_service', '=', True)])
    qty = fields.Float('qty', default=1)
    price_unit = fields.Float('Rate')
    tax_ids = fields.Many2many('account.tax',
        'service_invoice_line_tax', 'service_line_id', 'tax_id', string="Taxes")
    tax = fields.Float('Tax %')
    sub_total = fields.Float(compute='_compute_price', string="Sub Total", store=True)
    cgst = fields.Float(compute='_compute_price', string='CGST', store=True)
    sgst = fields.Float(compute='_compute_price', string='SGST', store=True)
    total = fields.Float(compute='_compute_price', string="Net Amount", store=True)
    invoice_id = fields.Many2one('service.invoice', 'Invoice')


class HotelRestaurantOrder(models.Model):
    _inherit = 'hotel.restaurant.order'

    morning = fields.Boolean()
    lunch = fields.Boolean()
    dinner = fields.Boolean()
    other = fields.Boolean()


class HotelRestaurantOrderList(models.Model):
    _inherit = 'hotel.restaurant.order.list'

    @api.multi
    @api.depends('o_list.tax_id')
    def get_tax_ids(self):
        for line in self:
            taxes_ids = [line.o_list.tax_id.id]
            line.tax_ids = [(6, 0, taxes_ids)]
        return 
        


    # @api.model
    # def default_get(self, default_fields):
    #     vals = super(HotelRestaurantOrderList, self).default_get(default_fields)
    #     taxes_ids=[]
    #     taxes_ids = [tax.id for tax in self.env.user.company_id.restaurant_tax_id]
    #     if len(taxes_ids) > 0:
    #         vals['tax_ids'] = [(6, 0, taxes_ids)]
    #     else:
    #         pass
    #     return vals


    @api.one
    @api.depends('price_subtotal')
    def _compute_amount_tax_included(self):
        gst = 0
        igst = 0
        for tax in self.tax_ids:
            if tax.tax_based == 'gst':
                gst += tax.amount
            if tax.tax_based == 'igst':
                igst += tax.amount
        gst_total = gst * self.price_subtotal
        self.sgst = self.cgst = gst_total/2
        self.igst = igst * self.price_subtotal

    @api.one
    @api.depends('item_rate','item_qty')
    def _get_amount(self):
        self.amount = float(self.item_qty) * float(self.item_rate)



    @api.one
    @api.depends('price_subtotal','cgst','igst','sgst')
    def _get_total_amount(self):
        self.total_amount = self.price_subtotal + self.igst + self.cgst + self.sgst


    @api.multi
    @api.depends('item_qty', 'item_rate','complimentary')
    def _sub_total(self):
       
        tax_obj = self.env['account.tax']

        for line in self:
            taxi = 0
            price_subtotal = 0
            for tax in line.tax_ids:
               if tax.price_include == True:
                    taxi += tax.amount

           
            line.price_subtotal = (line.item_rate*(1 - (line.discount or 0.0) / 100.0) * int(line.item_qty))/(1+taxi)
            
    date = fields.Date(related='o_list.o_date', store=True, string='Date')
    bill_no = fields.Char(related='o_list.bill_no', store=True, string='Bill No')
    state = fields.Selection(related='o_list.state', store=True, string='Status')
    complimentary = fields.Boolean(string='Complimentary')
    cgst = fields.Float('CGST',compute="_compute_amount_tax_included")
    sgst = fields.Float('SGST',compute="_compute_amount_tax_included")
    igst = fields.Float('IGST',compute="_compute_amount_tax_included")
    amount = fields.Float('Amount',compute="_get_amount")
    tax_ids = fields.Many2many('account.tax', 'hotel_order_tax', 'order_line_id', 'tax_id', string='Taxes',compute="get_tax_ids")
    discount = fields.Float('Discount(%)')
    total_amount = fields.Float('Total',compute="_get_total_amount")


class HotelRoomReservationLine(models.Model):

    _inherit = 'hotel.room.reservation.line'


    status = fields.Selection(string='state', store=True, related='reservation_id.state')
    state = fields.Selection([('assigned', 'Assigned'),
                              ('unassigned', 'Unassigned'),
                              ('dirty', 'Dirty'),
                              ('block', 'Block')], 'Room Status')
    check_in = fields.Date('Check In Date', required=True)
    check_out = fields.Date('Check Out Date', required=True)
