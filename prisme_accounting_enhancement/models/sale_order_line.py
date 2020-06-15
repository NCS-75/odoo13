from odoo import api, fields, models, _


class sale_order_line(models.Model):
    _name = 'sale.order.line' 
    _inherit = 'sale.order.line'
    
    def _prepare_invoice_line(self):
        """Adding the discount_amount from the sale line to the res dictionary that will create the invoice line."""
        self.ensure_one()
        res = super(sale_order_line, self)._prepare_invoice_line()
        
        res['discount_amount'] = self.discount_amount

        return res