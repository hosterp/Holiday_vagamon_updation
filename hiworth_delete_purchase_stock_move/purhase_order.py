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



class purchase_order(models.Model):
    _inherit = 'purchase.order'
    
    
    
    @api.multi
    def action_delete(self): 
        for line in self:
            picking_ids = self.env['stock.picking'].search([('origin','=',line.name)])
            for picking_id in picking_ids:
                move_ids = self.env['stock.move'].search([('picking_id','=',picking_id.id)])
                for move in move_ids:
                    quants = self.env['stock.quant'].search([('reservation_id','=', move.id)])
                    for quant in move.quant_ids:
                        quant.qty = 0.0
                    move.state = 'draft'
                    move.product_id.product_tmpl_id.qty_available = move.product_id.product_tmpl_id.qty_available - move.product_uom_qty
                    move.sudo().unlink()
                packs = self.env['stock.pack.operation'].search([('picking_id','=',picking_id.id)])
                for pack in packs:
                    pack.sudo().unlink()
                picking_id.sudo().unlink()
            line.state = 'draft'
            line.sudo().action_cancel()
            line.sudo().unlink()


    @api.multi
    def action_cancel_stock_moves(self): 
        for line in self:
            picking_ids = self.env['stock.picking'].search([('origin','=',line.name)])
            for picking_id in picking_ids:
                move_ids = self.env['stock.move'].search([('picking_id','=',picking_id.id)])
                for move in move_ids:
                    quants = self.env['stock.quant'].search([('reservation_id','=', move.id)])
                    for quant in move.quant_ids:
                        quant.sudo().qty = 0.0
                    move.sudo().state = 'draft'
                    move.product_id.product_tmpl_id.sudo().qty_available = move.product_id.product_tmpl_id.qty_available - move.product_uom_qty
                    move.sudo().unlink()
                packs = self.env['stock.pack.operation'].search([('picking_id','=',picking_id.id)])
                for pack in packs:
                    pack.sudo().unlink()
                picking_id.sudo().unlink()
            line.state = 'sanction'
            line.action_cancel()
            # line.state = 'draft'
            # line.shipped = False
            # line.unlink()
