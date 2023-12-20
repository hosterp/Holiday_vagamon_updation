from openerp import fields, models, api
from openerp.osv import fields as old_fields, osv, expression
import time
from datetime import datetime
import datetime

#from openerp.osv import fields
from openerp import tools
from openerp.tools import float_compare
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from pychart.arrow import default
from cookielib import vals_sorted_by_key
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
# from openerp.osv import osv



class stock_move(models.Model):
    _inherit = 'stock.move'
               
    @api.multi
    def unlink(self):
        for move in self:
            quants = self.env['stock.quant'].search([('reservation_id','=', move.id)])
            for quant in move.quant_ids:
                quant.qty = 0.0
                quant.unlink()
            move.state = 'draft'
            move.product_id.product_tmpl_id.qty_available = move.product_id.product_tmpl_id.qty_available - move.product_uom_qty
#             if move.state not in ('draft', 'cancel'):
#                 raise osv.except_osv(_('User Error!'), _('You can only delete draft moves.'))
            if move.picking_id:
                packs = self.env['stock.pack.operation'].search([('picking_id','=',move.picking_id.id)])
                for pack in packs:
                    pack.unlink()
            return  super(stock_move, move).unlink()
            
            
            
            
class stock_quant(osv.osv):
    _inherit = 'stock.quant'
    
    def unlink(self, cr, uid, ids, context=None):
        context = context or {}
#         if not context.get('force_unlink'):
#             raise osv.except_osv(_('Error!'), _('Under no circumstances should you delete or change quants yourselves!'))
#         super(stock_quant, self).unlink(cr, uid, ids, context=context)
        osv.osv.unlink(self, cr, uid, ids, context=context)
            
            
class stock_picking(models.Model):
    _inherit = 'stock.picking' 


    @api.multi
    def unlink(self):
        #on picking deletion, cancel its move then unlink them too
        move_obj = self.env['stock.move']
#         context = context or {}
        for pick in self:
            move_ids = [move.id for move in pick.move_lines]
            move_obj.action_cancel()
            move_obj.unlink()
            packs = self.env['stock.pack.operation'].search([('picking_id','=',pick.id)])
            for pack in packs:
                pack.unlink()
        return super(stock_picking, self).unlink()   
        
            