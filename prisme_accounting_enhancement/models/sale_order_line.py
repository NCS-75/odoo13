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
#    Project ID:    OERP-002-01 - T492
#
##########################################################################
from odoo import api, fields, models, _

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    
    def _prepare_invoice_line(self):
        """Adding the discount_amount from the sale line to the res dictionary that will create the invoice line."""
        self.ensure_one()
        res = super(sale_order_line, self)._prepare_invoice_line()
        
        res['discount_amount'] = self.discount_amount
        res['origin_price_unit'] = self.price_unit
        return res