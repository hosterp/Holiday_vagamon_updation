from openerp import models, fields, api, _


class Seasons(models.Model):
    _name = 'hotel.seasons'

    name = fields.Char('Season')
    period_from = fields.Date('Period From')
    period_to = fields.Date('Period To')


class HotelTemplates(models.Model):
    _name = 'hotel.templates'

    name = fields.Char('Template')
    templates = fields.One2many('hotel.templates.season', 'template_id')


class HotelTemplatesSeason(models.Model):
    _name = 'hotel.templates.season'

    template_id = fields.Many2one('hotel.templates')
    season_id = fields.Many2one('hotel.seasons', 'Season')
    
    meal_plan = fields.Selection([
    	('with_meal_plan','With Meal Plan'),
    	('without_meal_plan','Without Meal Plan')
    	], string="Select Meal Plan")
    extra_pax_rate = fields.Float('Rate for additional pax')
    packages = fields.One2many('hotel.templates.packages', 'package_id')
    lines = fields.One2many('hotel.templates.details', 'line_id')
    property_rate = fields.Float('Property Utilization Charge')
    food_lines = fields.One2many('hotel.templates.meals', 'food_line_id')

    


class HotelTemplatesPackages(models.Model):
    _name = 'hotel.templates.packages'

    package_id = fields.Many2one('hotel.templates.season')
    room_type = fields.Many2one('hotel.room.type')
    ap_rate = fields.Float('AP')
    map_rate = fields.Float('MAP')
    cp_rate = fields.Float('CP')


class HotelTemplatesDetails(models.Model):
    _name = 'hotel.templates.details'

    line_id = fields.Many2one('hotel.templates.season')
    room_type = fields.Many2one('hotel.room.type')
    rate = fields.Float('Rate')

class HotelTemplatesFood(models.Model):
    _name = 'hotel.templates.meals'

    food_line_id = fields.Many2one('hotel.templates.season')
    food_id = fields.Many2one('hotel.menucard','Food')
    rate = fields.Float('Rate')

    @api.onchange('food_id')
    def onchange_food_rates(self):
    	foods = self.env['hotel.menucard'].search([('id','=',self.food_id.id)])
    	if foods:
    		self.rate = foods.list_price
    
