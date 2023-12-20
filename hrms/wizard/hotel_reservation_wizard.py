# -*- coding: utf-8 -*-
#############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Serpent Consulting Services Pvt. Ltd.
#    (<http://www.serpentcs.com>)
#    Copyright (C) 2004 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
#############################################################################
# 
from openerp.exceptions import except_orm, ValidationError
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp import models, fields, api, _
from openerp import workflow
import time
import datetime
#from datetime import datetime, timedelta
from datetime import date
#from openerp.osv import fields, osv
from openerp.tools.translate import _
#from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
#from openerp.osv import fields, osv
from datetime import timedelta
from docutils.nodes import line
from pychart.arrow import default


class HotelReservationWizard(models.TransientModel):
    _inherit = 'hotel.reservation.wizard'
    
    @api.multi
    @api.depends('date_start')
    def _compute_date_start_new(self):
        
        for line in self:
    #        line.total_cost=line.product_id.standard_price*line.product_qty
            
            date_start_new = line.date_start
            start_dt = datetime.datetime.strptime(date_start_new, "%Y-%m-%d %H:%M:%S")
            h=start_dt.hour-18
            
            m=start_dt.minute-30
  #          print 'h.m=====================================', h, m
            mytime = datetime.datetime.strptime(date_start_new, "%Y-%m-%d %H:%M:%S")
  #          print 'mytime=========='
            mytime += timedelta(hours=h,minutes=m)
     #       print 'qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq',mytime.strftime("%Y.%m.%d %H:%M:%S")
            line.date_start_new=mytime.strftime("%Y-%m-%d %H:%M:%S")
   #         print 'reeeeeeeeeeeeeesssssssssssssssssss',line.date_start_new
    
#    total_cost = fields.Float(compute='_compute_total_cost', store=True, string='Total Cost')

    date_start_new = fields.Datetime(compute='_compute_date_start_new', store=True, string='Start Date New')
#     date_end = fields.Datetime('End Date', required=True)


# class room_availability(models.Model):
#     _name = 'room.availability'
#     
#     
#     name = fields.Char('Name')
#     date_start = fields.Date('Checkin')
    
    
