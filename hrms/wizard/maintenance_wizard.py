from openerp import models, fields, api, _

class MaintenanceWizard(models.TransientModel):
    _name = 'maintenance.wizard'

    

    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')


    @api.multi
    def action_submit(self):
        hotel_room_reserv_line_obj = self.env['hotel.room.reservation.line']
        for rec in self:
            active_model = self.env.context.get('active_model')
            active_id = self.env.context.get('active_id')
            if active_model == 'hotel.room':
                vals = {'room_id':active_id,
                        'state':'block',
                        'check_in':rec.date_from,
                        'check_out':rec.date_to,
                        }
                # self.env['hotel.room'].browse(active_id).write({'status':'blocked'})
        hotel_room_reserv_line_obj.create(vals)

