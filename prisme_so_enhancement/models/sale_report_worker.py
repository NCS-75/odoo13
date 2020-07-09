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
from odoo import fields, models

class sale_report(models.Model):
    _inherit = 'sale.report'
    

    so_name = fields.Char('Sale Order', readonly=True)
#     discount_total = fields.Float('Total Discount', digits=(16, 2))
#     net_price_total = fields.Float('Total Price (Net)', digits=(16, 2))
#     purchase_total = fields.Float('Total Purchase', digits=(16, 2))
#     margin_total = fields.Float('Total Margin', digits=(16, 2))
#                 
# 
#     def _select2(self):
#         select_str = super(sale_report, self)._select() + """,
#                     sum((l.product_uom_qty * l.price_unit) - l.price_subtotal) as discount_total,
#                     sum(l.price_subtotal) as net_price_total,
#                     sum(l.product_uom_qty * l.purchase_price) as purchase_total, 
#                     sum(l.margin) as margin_total,
#                     s.name as so_name
#         """
# 
#         return select_str
# 
# 
#     def _select(self):
#         select_str = super(sale_report, self)._select() + """,
#                     sum((l.product_uom_qty * l.price_unit) - l.price_subtotal) as discount_total,
#                     sum(l.price_subtotal) as net_price_total,
#                     sum(l.product_uom_qty * l.purchase_price) as purchase_total, 
#                     sum(l.margin) as margin_total,
#                     s.name as so_name
#         """
#         return select_str

    def _group_by(self):
        return super(sale_report, self)._group_by() + ", s.name"
