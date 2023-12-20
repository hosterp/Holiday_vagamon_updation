from openerp import models, fields, api, _


class ParticularsParticulars(models.Model):
    _name = 'particulars.particulars'
    _rec_name = 'name'

    name = fields.Char("Name")
    is_room_rent = fields.Boolean("Is Room Rent?")


class ParticularsLine(models.Model):
    _name = 'particulars.line'
    _rec_name = 'particulars_id'

    @api.depends('number', 'rate', 'taxes_id')
    def compute_total(self):
        for rec in self:
            tax_amount = 0.0
            taxi = 0.0
            taxe = 0.0
            total = 0.0
            total = (rec.number * rec.rate)
            for tax in rec.taxes_id:
                if tax.price_include == True:
                    tax_amount = (rec.number * rec.rate) * (100 / (100 + tax.amount))
                    total = (rec.number * rec.rate)
                if tax.price_include == False:
                    tax_amount = (rec.number * rec.rate) * tax.amount
                    total = (rec.number * rec.rate) + tax_amount
            # if taxe != 0.0:

            rec.total = total

    particulars_id = fields.Many2one('particulars.particulars', "Particular")
    number = fields.Integer("NoS")
    rate = fields.Float("Rate")
    taxes_id = fields.Many2many('account.tax', 'tax_id_particular_rel', 'particular_id', 'tax_id', 'Tax')
    total = fields.Float("Total", compute='compute_total', store=True)
    hotel_reservation_line_id = fields.Many2one('hotel_reservation.line', "Hotel Reservation Line")


class HotelReservationLine(models.Model):
    _inherit = "hotel_reservation.line"

    @api.depends('particulars_ids')
    def compute_grand_total(self):
        for rec in self:
            total = 0
            tax = 0
            untaxed = 0
            amount_total = 0
            for particular in rec.particulars_ids:
                total = (particular.rate * particular.number)
                # untaxed += (particular.rate * particular.number)
                for taxe in particular.taxes_id:
                    if taxe.price_include:
                        tax += total - total * (100 / (100 + (taxe.amount * 100)))
                        # print "taxxxxincludeeeeeeeeeeeeeeeeee", taxe.amount
                    if not taxe.price_include:
                        tax += (total * taxe.amount)
                        untaxed += (particular.rate * particular.number)
                        # print "taxxxxexclihjjjjjjjjjjjjjjjjjjjjj", tax
                amount_total += total
                if not particular.taxes_id:
                    untaxed += (particular.rate * particular.number)
            untaxed_amount = amount_total - tax
            if amount_total != untaxed:
                untaxed = untaxed_amount
            rec.total = untaxed
            rec.tax_amount = tax
            rec.grand_total = untaxed + tax

    particulars_ids = fields.One2many('particulars.line', 'hotel_reservation_line_id', "Particulars")
    grand_total = fields.Float("Grand Total", compute='compute_grand_total', store=True)
    tax_amount = fields.Float("Tax Amount", compute='compute_grand_total', store=True)
    total = fields.Float("Untaxed Amount", compute='compute_grand_total', store=True)
