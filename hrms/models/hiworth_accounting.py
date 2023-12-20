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

'''
class account_receipt(models.Model):
    _name = 'account.receipt'
    
    
    name = fields.Char('Name')
    amount = fields.Float('Amount', size=64)
    receiving_mode = fields.Selection([('bank', 'Bank'),
                              ('cash', 'Cash')], 'Payment Mode')
    narration = fields.Text('Narration', size=64)
    account_id = fields.Many2one('account.account', 'Account')
    particular = fields.Char('Particulars')
    date_entry = fields.Datetime('Date', required=True, 
                                 default=(lambda *a:
                                          time.strftime
                                          (DEFAULT_SERVER_DATETIME_FORMAT))) 
                                          

                                          
class account_payment(models.Model):
    _name = 'account.payment'
    
    
    name = fields.Char('Name')
    amount = fields.Float('Amount', size=64)
    receiving_mode = fields.Selection([('bank', 'Bank'),
                              ('cash', 'Cash')], 'Payment Mode')
    narration = fields.Text('Narration', size=64)
    particular = fields.Char('Particulars')
    account_id = fields.Many2one('account.account', 'Account')
    date_entry = fields.Datetime('Date', required=True, 
                                 default=(lambda *a:
                                          time.strftime
                                          (DEFAULT_SERVER_DATETIME_FORMAT))) '''
                                
class account_transaction_lines(models.Model):
    _name = 'account.transaction.lines'
    
    
    name = fields.Char('Name')
    transaction_no = fields.Char('Bill No', size=64)
    particular = fields.Char('Particulars')
    debit = fields.Float('Debit', size=64)
    credit = fields.Float('Credit', size=64)
    receiving_mode = fields.Selection([('bank', 'Bank'),
                              ('cash', 'Cash')], 'Payment Mode')
    line_id_transaction = fields.Many2one('account.account', 'Account')
    date_entry = fields.Datetime('Date', required=True, 
                                 default=(lambda *a:
                                          time.strftime
                                          (DEFAULT_SERVER_DATETIME_FORMAT)))
    narration = fields.Text('Narration', size=64)
    
    
    def create(self, cr, uid, vals, context=None):
            vals['transaction_no'
             ] = self.pool['ir.sequence'].get(cr, uid, 'hotel.accounting.entry.no2')            
            result = super(account_transaction_lines, self).create(cr, uid, vals, context=None)
            return result
    
    
class account_account(models.Model):
    _inherit = 'account.account'
    
    @api.multi
    @api.depends('transaction_line')
    def _compute_debit(self):
        total_debit=0.0        
        for line in self:
            #print'test100',self.transaction_line
            for transaction_line in self.transaction_line:
                #print'test101',transaction_line.debit
                total_debit += transaction_line.debit
            line.debit2=total_debit
            line.debit=total_debit
            
    @api.multi
    @api.depends('transaction_line')
    def _compute_credit(self):
        total_credit=0.0        
        for line in self:
            for transaction_line in self.transaction_line:
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
            
    @api.multi
    @api.depends('opening_balance','balance2')
    def _compute_total_balance(self):
        '''
        price_subtotal will display on change of item_rate
        --------------------------------------------------
        @param self: object pointer
        '''
        for line in self:
            line.total_balance2 = line.opening_balance + line.balance2

    
    transaction_line = fields.One2many('account.transaction.lines', 'line_id_transaction',
                                       'Transaction Line')
    balance2 = fields.Float(compute='_compute_balance', store=True,  string='Balance')
    debit2 = fields.Float(compute='_compute_debit', store=True, string='Debit' )
    credit2 = fields.Float(compute='_compute_credit', store=True, string='Credit')
    opening_balance = fields.Float(string='Opening Balance')
    total_balance2 = fields.Float(compute='_compute_total_balance', store=True,string='Total Balance')
    
    
                                       
                                       
                                       
                                       
                                       
                                       
                                       
                                       