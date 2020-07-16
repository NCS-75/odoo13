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
#    Project ID:    NEX001-010-001 - T257
#
##########################################################################
from odoo import api, fields, models
from . import layout

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    
    layout_type = fields.Selection(layout.LAYOUTS_LIST, 'Layout type', required=True, index=True, default=lambda *a: 'article')
    _sql_constraints = [
        ('accountable_required_fields',
            "CHECK(display_type IS NOT NULL OR (layout_type <> 'article' OR (product_id IS NOT NULL AND product_uom IS NOT NULL)))",
            "Missing required fields on accountable sale order line."),
    ]



    # ------------------------- Fields management
    def _is_number(self,s):
        try:
            float(s)
            return True
        except:
            return False
        

    # ------------------------- Instance management
    @api.model
    def create(self, vals_list):
        if vals_list is list:            
            for vals in vals_list:
                layout_type = vals.get('layout_type', 'article')
                if not vals.get('name'):
                    vals['name'] = layout.layout_val_2_text(layout_type)
        else:
            layout_type = vals_list.get('layout_type', 'article')
            if not vals_list.get('name'):
                vals_list['name'] = layout.layout_val_2_text(layout_type)
        return super(sale_order_line, self).create(vals_list)


    # ------------------------- Interface related
    @api.onchange('layout_type')
    def _layout_type_change(self):
        for record in self:
            if not(record.layout_type == 'article'):
                
                record.quantity = 1
                record.discount = 0.0
                record.move_line_tax_ids = False
                record.name = layout.layout_val_2_text(record.layout_type)
    
    
    def layout_type_change(self, layout_type):
        if layout_type == 'article':
            return { 'value':{} }

        vals = {
            'name': '',
            'uos_id': False,
            'account_id': False,
            'price_unit': 0.0,
            'price_subtotal': 0.0,
            'quantity': 0,
            'discount': 0.0,
            'invoice_line_tax_id': False,
            'account_analytic_id': False,
            'product_uom_qty': 0.0,
        }
        vals['name'] = layout.layout_val_2_text(layout_type)
        
        self.env.cr.execute("Select id from product_uom where name ilike 'unit%%' or name ilike '%%pce%%'")
        row = self.env.cr.fetchone()
        if row and row[0]:
            vals.update({
                'product_uom': row[0],
                'product_uos': row[0],
            })
        
        return { 'value': vals }

