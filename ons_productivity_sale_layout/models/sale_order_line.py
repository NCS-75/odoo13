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
from odoo import api, fields, models, _
from . import layout

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    
    layout_type = fields.Selection(layout.LAYOUTS_LIST, 'Layout type', required=True, index=True, default=lambda *a: 'article')
    rel_subtotal = fields.Float(compute='_sub_total', string='Rel. Sub-total', digits='Account')

    # ------------------------- Fields management
    def _is_number(self,s):
        try:
            float(s)
            return True
        except:
            return False
        
    
    def _sub_total(self):
        for sol in self:

            sub_total = 0.0
            if sol.layout_type == 'subtotal' and self._is_number(sol.order_id.id) and self._is_number(sol.id):
                sub_sols = self.env['sale.order.line'].search([('order_id','=',sol.order_id.id),('sequence','<=',sol.sequence),('id','!=',sol.id)], order='sequence desc,id desc')
                for sub_sol in sub_sols:
                    if sol.sequence > sub_sol.sequence or (sol.sequence == sub_sol.sequence and sol.id > sub_sol.id ):
                        if sub_sol.layout_type == 'subtotal': break
                        if sub_sol.sequence == sol.sequence and sub_sol.id > sol.id: break
                        if sub_sol.layout_type == 'article':
                            sub_total += sub_sol.price_subtotal
            
            sol.rel_subtotal = sub_total

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
                record.product_id = False
                record.quantity = 1
                record.discount = 0.0
                record.move_line_tax_ids = False
                record.name = layout.layout_val_2_text(record.layout_type)
                
            record._sub_total()
    
    
    def layout_type_change(self, layout_type):
        if layout_type == 'article':
            return { 'value':{} }

        vals = {
            'name': '',
            'product_id': False,
            'uos_id': False,
            'account_id': False,
            'price_unit': 0.0,
            'price_subtotal': 0.0,
            'quantity': 0,
            'discount': 0.0,
            'move_line_tax_id': False,
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

