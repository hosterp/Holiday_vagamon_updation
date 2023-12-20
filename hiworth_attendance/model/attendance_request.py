from openerp import models, fields, api, _
from openerp.osv import osv


class AttendanceRequest(models.Model):
	_name = 'attendance.request'

	date = fields.Date('Requested Date',default=fields.Date.today())
	attendance_date = fields.Date('Date of Attendance',default=fields.Date.today())
	# sign_in = fields.Datetime('Requested Sign In',required=True)
	# sign_out = fields.Datetime('Requested Sign Out',required=True)
	user = fields.Many2one('res.users','Logged User')
	attendance = fields.Selection([('full', 'Full Present'),
								('half','Half Present'),
								# ('absent','Absent')
								], default='full', string='Attendance')

	_defaults = {
		'user':lambda obj, cr, uid, ctx=None: uid,
		}

	@api.one
	def request_attendance(self):
		self.ensure_one()
		if self.attendance:
			self.env['pending.attendance.request'].create({'date':self.date,
												   # 'sign_in':self.sign_in,
												   # 'sign_out':self.sign_out,
												   'attendance_date':self.attendance_date,
												   'attendance':self.attendance,
												   'user1':self.user.employee_id.id})

			return

class PendingRequests(models.Model):
	_name = 'pending.attendance.request'

	date = fields.Date('Requested Date')
	attendance_date = fields.Date('Date of Attendance',default=fields.Date.today())
	# sign_in = fields.Datetime('Sign In')
	# sign_out = fields.Datetime('Sign Out')
	user1 = fields.Many2one('hr.employee','Logged User')
	state = fields.Selection([('pending','Pending'),('approved','Approved')],default="pending")
	attendance = fields.Selection([('full', 'Full Present'),
								('half','Half Present'),
								# ('absent','Absent')
								], default='full', string='Attendance')


	@api.multi
	def approve_attendance(self):
		self.state = 'approved'
		entry = self.env['hiworth.hr.attendance'].search([('name','=',self.user1.id),('date','=',self.date)])
		print 'entry--------------------------', entry
		if len(entry) != 0:
			entry[-1].write({'attendance':self.attendance})
			# raise osv.except_osv(_('Warning!'), _("Already entered attendance for employee '%s'") % (lines.employee_id.name,))

		else:
			self.env['hiworth.hr.attendance'].with_context(default_name=self.user1.id,default_check=1).create({
												  'name':self.user1.id,
												  'attendance':self.attendance,
												  'date':self.attendance_date,
												  # 'sign_in':self.sign_in,
												  # 'sign_out':self.sign_out,
												  # 'state':'sign_in',
												  # 'employee_type':self.user1.employee_type,
												  # 'attendance_signin_id':0,
												  # 'attendance_signout_id':0,
												  })



