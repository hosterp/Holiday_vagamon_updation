from openerp import models, fields, api
import time
import datetime
#from datetime import datetime, timedelta
from datetime import date

class ReservationQuick(models.Model):
    _name = 'quick.room.reservation.view'

    name = fields.Many2one('res.partner','Customer',readonly=True)
    check_in = fields.Datetime('CheckIn',readonly=True)
    check_out = fields.Datetime('CheckOut',readonly=True)
    room = fields.Many2one('hotel.room','Room',readonly=True)

    @api.multi
    def room_block_reserve(self):
        return True

    @api.model
    def default_get(self, fields):

        if self._context is None:
            self._context = {}
        res = super(ReservationQuick, self).default_get(fields)
        date_format = "%Y-%m-%d %H:%M:%S"

        # print "2222222222222222222222222", self._context
        if self._context:
            keys = self._context.keys()
            
            if 'room_id' in keys:
                roomid = self._context['room_id']
                res.update({'room': int(roomid)})
                date = ((datetime.datetime.strptime(self._context['date'],date_format)-datetime.timedelta(1))).date()
                room = self.env['hotel.room.reservation.line'].search([('room_id','=',int(roomid))])
                for line in room:
                    print 'line.check_in-------------', line.check_in
                    # check_in = (datetime.datetime.strptime(line.check_in,"%Y-%m-%d %H:%M:%S")).date()
                    # check_out = (datetime.datetime.strptime(line.check_out,"%Y-%m-%d %H:%M:%S")).date()
                    check_in = (datetime.datetime.strptime(line.check_in,"%Y-%m-%d")).date()
                    check_out = (datetime.datetime.strptime(line.check_out,"%Y-%m-%d")).date()
                    if check_out >= date and check_in <= date:
                      res.update({'name': line.reservation_id.partner_id.id,'check_in':line.reservation_id.checkin,'check_out':line.reservation_id.checkout})
        return res


class ReservationQuickTable(models.Model):
    _name = 'quick.room.reservation.table'

    name = fields.Many2one('res.partner','Customer',readonly=True)
    check_in = fields.Datetime('CheckIn',readonly=True)
    check_out = fields.Datetime('CheckOut',readonly=True)
    room = fields.Many2one('hotel.room','Room',readonly=True)

    @api.multi
    def room_reserved(self):
        return True

    @api.model
    def default_get(self, fields):

        if self._context is None:
            self._context = {}
        res = super(ReservationQuickTable, self).default_get(fields)
        date_format = "%Y-%m-%d %H:%M:%S"

        print "11111111111111111111111", self._context
        if self._context:
            keys = self._context.keys()
            
            if 'rooms_id' in keys:
                roomid = self._context['rooms_id']
                res.update({'room': int(roomid)})
                # date = ((datetime.datetime.strptime(self._context['dates'],date_format)-datetime.timedelta(1))).date()
                # room = self.env['hotel.room.reservation.line'].search([('room_id','=',int(roomid))])
                # for line in room:
                #     check_in = (datetime.datetime.strptime(line.check_in,"%Y-%m-%d %H:%M:%S")).date()
                #     check_out = (datetime.datetime.strptime(line.check_out,"%Y-%m-%d %H:%M:%S")).date()
                #     if check_out >= date and check_in <= date:
                #       res.update({'name': line.reservation_id.partner_id.id,'check_in':line.reservation_id.checkin,'check_out':line.reservation_id.checkout})
        return res

class Calendar(models.Model):
    _inherit = 'calendar.event'

    name = fields.Char('Meeting Subject', required=True, states={'done': [('readonly', False)]})