
import logging
import psycopg2
import time
from datetime import datetime
from operator import attrgetter

from openerp import tools, models
from openerp.osv import fields, osv
from openerp.tools import float_is_zero
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp
import openerp.addons.product.product
from lxml import etree


_logger = logging.getLogger(__name__)



class purchase_order(osv.osv):

    _inherit = "purchase.order"


    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        # print "aaaaaaaaaaa1111"
        cur_obj=self.pool.get('res.currency')
        line_obj = self.pool['purchase.order.line']
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'igst': 0.0,
                'cgst': 0.0,
                'sgst': 0.0,

                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                val1 += line.price_subtotal
                line_price = line_obj._calc_line_base_price(cr, uid, line,
                                                            context=context)
                line_qty = line_obj._calc_line_quantity(cr, uid, line,
                                                        context=context)
                gst_ids = []
                igst_ids = []
                for tax in line.taxes_id:
                    if tax.tax_based == 'gst':
                        gst_ids.append(tax.id)
                    if tax.tax_based == 'igst':
                        igst_ids.append(tax.id)
                gst = self.pool['account.tax'].browse(cr, uid, gst_ids)
                igst = self.pool['account.tax'].browse(cr, uid, igst_ids)
                gst_val = 0.0
                igst_val = 0.0
                for c in self.pool['account.tax'].compute_all(
                        cr, uid, gst, line_price, line_qty,
                        line.product_id, order.partner_id)['taxes']:
                    gst_val += c.get('amount', 0.0)
                for c in self.pool['account.tax'].compute_all(
                        cr, uid, igst, line_price, line_qty,
                        line.product_id, order.partner_id)['taxes']:
                    igst_val += c.get('amount', 0.0)

                for c in self.pool['account.tax'].compute_all(
                        cr, uid, line.taxes_id, line_price, line_qty,
                        line.product_id, order.partner_id)['taxes']:
                    val += c.get('amount', 0.0)
            res[order.id]['igst']=cur_obj.round(cr, uid, cur, igst_val)
            res[order.id]['cgst']=cur_obj.round(cr, uid, cur, gst_val/2)
            res[order.id]['sgst']=cur_obj.round(cr, uid, cur, gst_val/2)
            res[order.id]['amount_tax']=cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed']=cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total']=res[order.id]['amount_untaxed'] + res[order.id]['amount_tax'] + order.round_off

        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()



   
    _columns = {
        
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The amount without tax", track_visibility='always'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Taxes',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The tax amount"),

        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'purchase.order.line': (_get_order, None, 10),
                'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['round_off'], 10),
            }, multi="sums", help="The total amount"),
        'round_off': fields.float('Rounf Off', track_visibility='always')
        
    }


    def action_invoice_create(self, cr, uid, ids, context=None):
        """Generates invoice for given ids of purchase orders and links that invoice ID to purchase order.
        :param ids: list of ids of purchase orders.
        :return: ID of created invoice.
        :rtype: int
        """
        context = dict(context or {})
        
        inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')

        res = False
        uid_company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        for order in self.browse(cr, uid, ids, context=context):
            context.pop('force_company', None)
            if order.company_id.id != uid_company_id:
                #if the company of the document is different than the current user company, force the company in the context
                #then re-do a browse to read the property fields for the good company.
                context['force_company'] = order.company_id.id
                order = self.browse(cr, uid, order.id, context=context)
            
            # generate invoice line correspond to PO line and link that to created invoice (inv_id) and PO line
            inv_lines = []
            for po_line in order.order_line:
                if po_line.state == 'cancel':
                    continue
                acc_id = self._choose_account_from_po_line(cr, uid, po_line, context=context)
                inv_line_data = self._prepare_inv_line(cr, uid, acc_id, po_line, context=context)
                inv_line_id = inv_line_obj.create(cr, uid, inv_line_data, context=context)
                inv_lines.append(inv_line_id)
                po_line.write({'invoice_lines': [(4, inv_line_id)]})

            # get invoice data and create invoice
            inv_data = self._prepare_invoice(cr, uid, order, inv_lines, context=context)
            if order.round_off != 0:
                inv_data['round_off'] = order.round_off
                print 'order.invoice_no-----------------', order.invoice_no
            inv_data['purchase_bill_no'] = order.invoice_no
            # print 'test=======================', inv_data, asd
            inv_id = inv_obj.create(cr, uid, inv_data, context=context)

            # compute the invoice
            inv_obj.button_compute(cr, uid, [inv_id], context=context, set_total=True)

            # Link this new invoice to related purchase order
            order.write({'invoice_ids': [(4, inv_id)]})
            res = inv_id
        return res



    def action_cancel(self, cr, uid, ids, context=None):
        for purchase in self.browse(cr, uid, ids, context=context):
            for pick in purchase.picking_ids:
                for move in pick.move_lines:
                    if pick.state == 'done':
                        raise osv.except_osv(
                            _('Unable to cancel the purchase order %s.') % (purchase.name),
                            _('You have already received some goods for it.  '))
            self.pool.get('stock.picking').action_cancel(cr, uid, [x.id for x in purchase.picking_ids if x.state != 'cancel'], context=context)
            for inv in purchase.invoice_ids:
                inv.action_cancel() 
                if inv and inv.state not in ('cancel', 'draft'):
                    raise osv.except_osv(
                        _('Unable to cancel this purchase order.'),
                        _('You must first cancel all invoices related to this purchase order.'))
            self.pool.get('account.invoice') \
                .signal_workflow(cr, uid, map(attrgetter('id'), purchase.invoice_ids), 'invoice_cancel')
        self.signal_workflow(cr, uid, ids, 'purchase_cancel')
        return True
    