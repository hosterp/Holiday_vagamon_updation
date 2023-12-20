from openerp import fields, models, api

class res_partner_inhr(models.Model):
	_inherit = 'res.partner'

	# passport = fields.Char(string="Passport No/ID No")

	dob = fields.Date('DOB')
	wdng_day = fields.Date('Wedding Anniversary Date')
	occupation = fields.Char('Occupation')
	is_foreigner = fields.Boolean('IS Foreigner')
	passport_no = fields.Char('Passport No')
	nationality = fields.Char('Nationality')
	pspt_issue_date = fields.Date('Date Of Issue')
	pspt_passport_place = fields.Char('Place Of Issue')
	pspt_expiry_date = fields.Date('Expiry Date')
	visa_no = fields.Char('Visa No')
	visa_issue_date = fields.Date('Date Of Issue')
	visa_place = fields.Char('Place Of Issue')
	visa_expiry_date = fields.Date('Expiry Date')
	id_type1 = fields.Selection([('passport', 'Passport'),
                              ('adhar', 'Adhar Card'),
                              ('voter', 'Voter ID'),
                              ('pan', 'PAN Card'),
                              ('licence', 'Licence'), ], 'Type of ID Card')
	id_no1 = fields.Char('ID No.')
	id_type2 = fields.Selection([('passport', 'Passport'),
                              ('adhar', 'Adhar Card'),
                              ('voter', 'Voter ID'),
                              ('pan', 'PAN Card'),
                              ('licence', 'Licence'), ], 'Type of ID Card')
	id_no2 = fields.Char('ID No.')
	