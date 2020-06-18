from odoo import api, fields, models, _


class sale_order(models.Model):
    _inherit = 'sale.order'
    
    def _prepare_invoice(self):
        self.ensure_one()
        res = super(sale_order, self)._prepare_invoice()
        res['rounding_on_subtotal'] = self.rounding_on_subtotal
        
        return res