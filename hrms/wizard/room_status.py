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


class RoomStatusWizard(models.TransientModel):
    _inherit = 'room.status.wizard'

    

    folio_id = fields.Many2one('hotel.folio', 'Folio')

    line_ids = fields.One2many('room.status.wizard.line', 'wizard_id', 'Lines')

class RoomStatusWizardLine(models.TransientModel):
    _inherit = 'room.status.wizard.line'

    wizard_id = fields.Many2one('room.status.wizard', 'Wizard')
    room_id = fields.Many2one('hotel.room', 'Room')
    status = fields.Selection([('unassigned', 'Unassigned'),
                              ('dirty', 'Dirty'),
                              ('block', 'Block')], 'Room Status')




