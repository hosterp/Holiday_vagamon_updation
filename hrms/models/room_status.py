from openerp import models, fields, api
from openerp.exceptions import except_orm, ValidationError


class RoomStatus(models.Model):
	_name = 'room.status'

	room = fields.Many2one('hotel.room','Room Number')
	date_status = fields.Date('Date')
	status = fields.Selection([('assigned','Assigned'),('unassigned','Unassigned'),('dirty','Dirty')])


	@api.onchange('room','date_status')
	def onchange_room(self):
		if self.room:
			datetime = fields.Datetime.now()
			rooms = self.env['hotel.room.reservation.line'].search([('room_id','=',self.room.id)])
			for room in rooms:
				if room.check_in <= datetime and room.check_out >= datetime:
					print "================================================="
					self.status = room.state
		if self.room and self.date_status:
			rooms = self.env['hotel.room.reservation.line'].search([('room_id','=',self.room.id)])
			rooms_new = self.env['hotel.room.reservation.line'].search([('check_in','=',self.date_status),('check_out','=',self.date_status),('room_id','=',self.room.id),('room_id','=',self.room.id)])
			if rooms_new:
				self.status = rooms_new.state
			else:
				for room in rooms:
					if room.check_in <= self.date_status and room.check_out >= self.date_status:
						print "================================================="
						self.status = room.state


	@api.multi
	def apply_status(self):
		rec = self.env['hotel.room.reservation.line'].search([('check_in','=',self.date_status),('check_out','=',self.date_status),('room_id','=',self.room.id)])
		if rec:
			for vals in rec:
				vals.unlink()
				print "reccccccc========================"
		else:
			self.env['hotel.room.reservation.line'].create(
								{
								'state':self.status,
								'room_id':self.room.id,
								'check_in':self.date_status,
								'check_out':self.date_status
								})
