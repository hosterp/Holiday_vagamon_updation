from openerp.exceptions import except_orm, ValidationError
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp import models, fields, api, _
import time
import datetime
from datetime import date
import openerp.addons.decimal_precision as dp
from datetime import timedelta, datetime




class HouseKeepingAllocation(models.Model):
    _name = 'house.keeping.allocation'
    _description = 'Items Allocations to rooms by housekeeping'
    
    @api.multi
    @api.onchange('folio_id')
    def onchange_folio(self):
        for line in self:
            if line.folio_id:
                line.partner_id = line.folio_id.partner_id.id
            
            
                
    name = fields.Char('Name')
    date = fields.Date('Date')
    partner_id = fields.Many2one('res.partner', 'Customer')
    folio_id = fields.Many2one('hotel.folio', 'Folio No')
    state = fields.Selection([('open', 'Open'),
                              ('close', 'Closed')], 'Status', default='open')
    allocation_room_ids = fields.One2many('allocation.room', 'allocation_id', 'Rooms')
    
    _defaults = {
                'date': date.today(),
    }
    
    @api.multi
    def action_close(self):
        temp = False
        for line in self.allocation_room_ids:
            for lines in line.allocation_ids:
                if lines.state == 'alloted':
                    temp = True
        if temp == True:
           raise ValidationError(_('All items in each rooms should be in returned state.')) 
        self.state = 'close'


class AllocationRoom(models.Model):
    _name = 'allocation.room'
    
    @api.multi
    @api.onchange('allocation_id','room_id')
    def onchange_room(self):
        if not self.allocation_id.folio_id:
           raise ValidationError(_('Please Select a Folio No.'))  
        room_ids = []
        if self.allocation_id.folio_id:
            reservation_id = self.allocation_id.folio_id.reservation_id
            for reservation in reservation_id:
                room_ids = [room.id for room in reservation.reservation_line]
        return {'domain': {'room_id': [('id', 'in', room_ids)]}}
    
    name = fields.Char('Name')
    room_id = fields.Many2one('hotel.room', 'Room')
    allocation_ids = fields.One2many('allocation.items', 'room_id', 'Items')
    allocation_id = fields.Many2one('house.keeping.allocation', 'Allocation')
    
class AllocationItems(models.Model):
    _name = 'allocation.items'
    
    @api.onchange('alloted_qty','state','returned_qty')
    def onchange_returned_qty(self):
        if self.state != 'alloted' and not self.returned_qty:
            self.returned_qty = self.alloted_qty
        if self.state == 'damage' and self.returned_qty:
            self.damaged_qty = self.alloted_qty-self.returned_qty
#         if self.returned_qty == 0.0:
#             raise ValidationError(_('Please Enter a valid number.'))
    
    name = fields.Char('Name')
    product_id = fields.Many2one('product.product', 'Items', domain=[('isservice','!=',True),('isroom','!=',True),('ismenucard','!=',True),('room_status2','!=',True),('is_hotel_service','!=',True),('is_laundry','!=',True)])
    alloted_qty = fields.Float('Alloted Qty')
    returned_qty = fields.Float('Returned Qty')
    damaged_qty = fields.Float('Damaged Qty')
    state = fields.Selection([('alloted', 'Alloted'),
                              ('return', 'Returned'),
                              ('damage', 'Damaged')], 'Status', default='alloted')
    remarks = fields.Text('Remarks')
    room_id = fields.Many2one('allocation.room', 'Room')
    
    
    
    
