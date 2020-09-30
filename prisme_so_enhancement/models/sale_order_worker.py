# -*- coding: utf-8 -*-
###########################################################################
#
#    Prisme Solutions Informatique SA
#    Copyright (c) 2016 Prisme Solutions Informatique SA <http://prisme.ch>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#    You should have received a copy of the GNU Affero General Public Lic
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Project ID:    OERP-003-03 - T503
#
#    Modifications:
#
##########################################################################
from odoo import api, fields, models, tools, _
from odoo.exceptions import  ValidationError
from datetime import datetime

class sale_order_prisme(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'
    
    
    refused = fields.Text('refused')

    rounding_on_subtotal = fields.Float('Rounding on Subtotal', default=lambda *a: 0.05)
                    
    quotation_comment = fields.Char('Quotation Comment', translate=True, readonly=False, states={'draft': [('readonly', False)]})
                                               
    cancellation_reason = fields.Char("Cancellation Reason", readonly=True, states={'draft': [('readonly', False)],
                            'sent': [('readonly', False)],
                              'manual': [('readonly', False)],
                              'progress': [('readonly', False)],
                              'shipping_except': [('readonly', False)],
                              'invoice_except': [('readonly', False)],
                              'sale': [('readonly', False)]})
                              
    # Columns overriden to use the Prisme's methode (see _amount_all_prisme)
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all_prisme', track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all_prisme', track_visibility='always')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all_prisme', track_visibility='always')
                    
    shipped = fields.Boolean("Shipped")
    order_line = fields.One2many('sale.order.line', 'order_id', 'Order Lines', readonly=True, 
                    states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'manual': [('readonly', False)]}, copy=True)
    
    # Redefine field confirmation_date to disable copy when duplicating sale.order
    confirmation_date = fields.Datetime(string='Confirmation Date', readonly=True, index=True, help="Date on which the sale order is confirmed.", copy=False)

        # Method copied from sale/sale.py (sale_order._amount_line_tax the 22.09.2011
    # modified the 22.09.2011 by Damien Raemy to compute the subtotal by line 
    # using the discount type (percent, amount or null).
    def _amount_line_tax(self, line):
        val = 0.0
        #Modification begin
        # Modification no       1
        # Author(s):            Damien Raemy
        # Date:                 22.09.2011
        # Last modification:    22.09.2011
        # Description:          Calculate the unit price using discount
        # But:                  Have a price rightly calculated
        unit_price = line.price_unit
        if (line.discount_amount):
            unit_price = unit_price - (line.discount_amount / line.product_uom_qty)
            
        if (line.discount):
            unit_price = unit_price * (1 - (line.discount / 100.0))
        # Modification 1 end    
        
        
        for c in self.env['account.tax'].compute_all(line.tax_id, unit_price, line.product_uom_qty, line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val
    
            
    # Method copied from sale/sale.py (sale_order._amount_all) the 25.01.2017
    # and modified to don't compute the tax in the
    # total when the line is refused        
    @api.depends('order_line.price_total')
    def _amount_all_prisme(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            amount_tax = 0.0
            for line in order.order_line:
                # Prisme Modification begin
                # But: Manage the refused boolean in the lines
           
                if line.refused:
                    continue
                # Prisme Modification end
                
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                if order.company_id.tax_calculation_rounding_method == 'round_globally':
                    # Prisme modification start
                    price = line.price_unit
                    if (line.discount_amount):
                        price = price - (line.discount_amount / line.product_uom_qty)
                    if (line.discount):
                        price = price * (1 - (line.discount / 100.0))
                    
                    # Prisme modification end
                    taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_id)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
            
            """# We need to update the order amount_tax and amount_untaxed separately in v13, otherwise a singleton error is thrown.
            if amount_untaxed:
                order.update({'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed)})
            if amount_tax:
                order.update({'amount_tax': order.pricelist_id.currency_id.round(amount_tax)})
            order.update({'amount_total': amount_untaxed + amount_tax})"""
            
            untaxed_rounded = self._prisme_round(amount_untaxed, order.rounding_on_subtotal)
            taxes_rounded = self._prisme_round(amount_tax, order.rounding_on_subtotal)
            
            order.update({
                'amount_untaxed': untaxed_rounded,
                'amount_tax': taxes_rounded,
                'amount_total': untaxed_rounded + taxes_rounded,
            })
    
    def action_cancel(self):
        result = super(sale_order_prisme, self).action_cancel()
        reason = self.cancellation_reason
        if not reason:
            raise ValidationError(_('You must specify a cancellation reason in the ' + 
                     'Other Information tab before cancelling this ' + 
                     'sale order'))
        return result
    
    def action_confirm(self):
        self.confirmation_date = datetime.now()
        return super(sale_order_prisme,self).action_confirm()
    
    # Rounds the given to the given precision coinage. Added this method here because the native currency.round() method doesn't seem to work and throws errors with our lines.
    def _prisme_round(self, amount, precision):
        value_rouned = amount
        if precision and precision > 0 :
            value_rouned = tools.float_round(amount, precision_rounding=precision)
        return value_rouned
