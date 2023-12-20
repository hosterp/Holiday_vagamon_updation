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
from openerp.tools import float_compare


class account_account(models.Model):
    _inherit = 'account.account'

    @api.multi
    @api.depends('journal_item_line')
    def _compute_debit(self):
        total_debit=0.0
        for line in self:
            #print'test100',self.transaction_line
            for transaction_line in line.journal_item_line:
                #print'test101',transaction_line.debit
                total_debit += transaction_line.debit
            line.debit2=total_debit
            line.debit=total_debit

    @api.multi
    @api.depends('journal_item_line')
    def _compute_credit(self):
        total_credit=0.0
        for line in self:
            for transaction_line in line.journal_item_line:
                total_credit += transaction_line.credit
            line.credit2=total_credit
            line.credit=total_credit

    @api.multi
    @api.depends('debit2','credit2')
    def _compute_balance(self):
        '''
        price_subtotal will display on change of item_rate
        --------------------------------------------------
        @param self: object pointer
        '''

        for line in self:
            line.balance2 = line.debit2 - line.credit2
            line.balance = line.debit2 - line.credit2


    balance2 = fields.Float(compute='_compute_balance', store=True,  string='Balance')
    debit2 = fields.Float(compute='_compute_debit', store=True, string='Debit' )
    credit2 = fields.Float(compute='_compute_credit', store=True, string='Credit')
#    parent_id2 = fields.Many2one('account.account', 'Parent', ondelete='cascade')
#    child_parent_ids2 = fields.One2many('account.account','parent_id','Children')
#    opening_balance = fields.Float(string='Opening Balance')
#    total_balance2 = fields.Float(compute='_compute_total_balance', store=True,string='Total Balance')

    journal_item_line = fields.One2many('account.move.line', 'account_id')
    code = fields.Char('Code', size=64, required=False, select=1)


class account_move_line(models.Model):
     _inherit = 'account.move.line'

     _order = "date asc"

     reserv_id = fields.Many2one('hotel.reservation', string='Reservation No')
     invoice_id = fields.Many2one('account.invoice', 'Invoice')



class account_voucher(models.Model):
    _inherit = 'account.voucher'

    invoice_id = fields.Many2one('account.invoice', 'Invoice')
    account_holder = fields.Char(string="Card Holder")
    account_no = fields.Char(string='Card Number')
    travel_agency = fields.Many2one('res.partner','Agency')

    @api.multi
    def get_id(self,invoice_id):
        # print "aaaaaaaaaaaaaaaaa=================="
        # print "invoice_id================", invoice_id
        if invoice_id:
            # print "bbbbbbbbbbbbbbbbb"
            list = []
            invoice = self.env['account.invoice'].search([('id','=',invoice_id)])
            if invoice:
                list.append(invoice.partner_id.id)
                list.append(invoice.traval_agent_id.id)
                return {'domain': {'partner_id': [('id', 'in', list)]}}


    def _compute_writeoff_amount(self, cr, uid, line_dr_ids, line_cr_ids, amount, type):
        debit = credit = 0.0
        sign = type == 'receipt' and -1 or 1
        for l in line_dr_ids:
            if isinstance(l, dict):
                debit += l['amount']
        for l in line_cr_ids:
            if isinstance(l, dict):
                credit += l['amount']
        return amount - sign * (credit - debit)

    # @api.onchange('travel_agency')
    # def onchange_travel_agency(self): 
    #     if self.travel_agency:
    #         if self.journal_id.code == 'ota':    
    #             self.account_id = self.travel_agency.property_account_receivable.id     

    # @api.multi
    # def button_proforma_voucher(self):
    #     if self.amount == self.invoice_id.residual:
    #         self.invoice_id.state = 'paid'
    #     self.signal_workflow('proforma_voucher')
    #     return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def button_proforma_voucher2(self):
        if self.amount == self.invoice_id.residual:
            self.invoice_id.state = 'paid'
        move = self.env['account.move']
        move_line = self.env['account.move.line']
        values = {
                'journal_id': self.journal_id.id,
                'date': self.date,
                'period_id': self.period_id.id,
                }

        move_id = move.create(values)
        
        partner_id = self.invoice_id.partner_id
        account_id = self.invoice_id.account_id
        payment_ids = []
        payment_ids = [payment.id for payment in self.invoice_id.payment_ids]
        if account_id.type == 'receivable':
            if self.journal_id.code == 'ota':
                if self.travel_agency:
           
                    values2 = {
                            'account_id': self.travel_agency.property_account_receivable.id,
                            'name': self.invoice_id.number,
                            'debit': self.amount,
                            'credit': 0,
                            'move_id': move_id.id,
                            }
                      
                    line_id = move_line.create(values2)
                    line_id.invoice_id = False
                    values3 = {
                        'account_id': self.journal_id.default_debit_account_id.id,
                        'name': self.invoice_id.number,
                        'debit': 0,
                        'credit': self.amount,
                        'move_id': move_id.id,
                        'invoice_id': self.invoice_id.id,
                        'partner_id': self.partner_id.id,
                        }
                    line_id2 = move_line.create(values3)
                else:
                    raise Exception('You have not given agency.')


            else:
                # self.button_proforma_voucher()
                values2 = {
                        'account_id': self.journal_id.default_debit_account_id.id,
                        'name': self.invoice_id.number,
                        'debit': self.amount,
                        'credit': 0,
                        'move_id': move_id.id,
                        # 'partner_id': self.partner_id.id,
                        }
                print 'values2===============',values2
                line_id = move_line.create(values2)
                line_id.invoice_id = False
                values3 = {
                        'account_id': self.partner_id.property_account_receivable.id,
                        'name': self.invoice_id.number,
                        'debit': 0,
                        'credit': self.amount,
                        'move_id': move_id.id,
                        'invoice_id': self.invoice_id.id,
                        # 'partner_id': self.partner_id.id,
                        }
                # print 'values2===============',values3
                line_id2 = move_line.create(values3)

        if account_id.type == 'payable':
            values2 = {
                    'account_id': self.journal_id.default_credit_account_id.id,
                    'name': self.invoice_id.name,
                    'debit': 0,
                    'credit': self.amount,
                    'move_id': move_id.id,
                    }
            line_id = move_line.create(values2)
            line_id.invoice_id = False
            values3 = {
                'account_id': account_id.id,
                'name': self.invoice_id.name,
                'debit': self.amount,
                'credit': 0,
                'move_id': move_id.id,
                'invoice_id': self.invoice_id.id
                }
            line_id2 = move_line.create(values3)

        move_id.button_validate()
        return {'type': 'ir.actions.act_window_close'}
