# -*- coding: utf-8 -*-
#
#  File: layout.py
#  Module: ons_productivity_sale_layout
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2013 Open-Net Ltd. All rights reserved.
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

LAYOUTS_LIST = [
    ('article', 'Product'),
    ('title', 'Title'),
    ('text', 'Note'),
    ('subtotal', 'Sub Total'),
    ('line', 'Separator Line'),
    ('break', 'Page Break'),
]

def layout_val_2_text(layout_type):
    val = _( 'Product' )
    if layout_type == 'title':
        val = _( 'Title' )
    elif layout_type == 'text':
        val = _( 'Note' )
    elif layout_type == 'subtotal':
        val = _( 'Sub Total' )
    elif layout_type == 'line':
        val = _( 'Separator Line' )
    elif layout_type == 'break':
        val = _( 'Page Break' )

    return val

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    
    layout_type = fields.Selection(LAYOUTS_LIST, 'Layout type', required=True, index=True, default=lambda *a: 'article')
    rel_subtotal = fields.Float(compute='_sub_total', string='Rel. Sub-total', digits= dp.get_precision('Account'))

    # ------------------------- Fields management
    def _is_number(self,s):
        try:
            float(s)
            return True
        except:
            return False
        
    @api.multi
#     @api.depends('rel_subtotal')
    def _sub_total(self):
        for sol in self:

            sub_total = 0.0
            if sol.layout_type == 'subtotal' and self._is_number(sol.order_id.id):
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
                    vals['name'] = layout_val_2_text(layout_type)
        else:
            layout_type = vals_list.get('layout_type', 'article')
            if not vals_list.get('name'):
                vals_list['name'] = layout_val_2_text(layout_type)
        return super(sale_order_line, self).create(vals_list)


    # ------------------------- Interface related
    @api.onchange('layout_type')
    def _layout_type_change(self):
        for record in self:
            if not(record.layout_type == 'article'):
                record.product_id = False
                record.quantity = 1
                record.discount = 0.0
                record.invoice_line_tax_ids = False
                record.name = layout_val_2_text(record.layout_type)
                
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
            'invoice_line_tax_id': False,
            'account_analytic_id': False,
            'product_uom_qty': 0.0,
        }
        vals['name'] = layout_val_2_text(layout_type)

        self.env.cr.execute("Select id from product_uom where name ilike 'unit%%' or name ilike '%%pce%%'")
        row = self.env.cr.fetchone()
        if row and row[0]:
            vals.update({
                'product_uom': row[0],
                'product_uos': row[0],
            })

        return { 'value': vals }

    # ------------------------- Utilities
#     def invoice_line_create(self, invoice_id, qty):
#         ret = super(sale_order_line, self).invoice_line_create(invoice_id, qty)
#         invl_obj = self.env['account.invoice.line']
# 
#         for sol in self:
#             invl_ids = [x.id for x in sol.invoice_lines]
#             if invl_ids:
#                 invl_obj.write(invl_ids, {'layout_type': sol.layout_type})
#         
#         return ret

class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'

    # ------------------------- Fields management
    def _is_number(self,s):
        try:
            float(s)
            return True
        except:
            return False
        
    layout_type = fields.Selection(LAYOUTS_LIST, 'Layout type', required=True, index=True, default=lambda *a: 'article')
    rel_subtotal = fields.Float(compute='_sub_total', string='Rel. Sub-total', digits= dp.get_precision('Account'))
    
    _order = 'invoice_id desc, sequence asc , id'
        
    @api.multi
#     @api.depends('rel_subtotal')
    def _sub_total(self):            
            
        for invl in self:
            invl.sequence_number_next = 2

            
            sub_total = 0.0
            if invl.layout_type == 'subtotal' and self._is_number(invl.invoice_id.id):
                sub_invls = self.env['account.invoice.line'].search([('invoice_id','=',invl.invoice_id.id),('sequence','<=',invl.sequence),('id','!=',invl.id)], order='sequence desc,id desc')
                for sub_invl in sub_invls:
                    if invl.sequence > sub_invl.sequence or (invl.sequence == sub_invl.sequence and invl.id > sub_invl.id ):
                        if sub_invl.layout_type == 'subtotal':                             
                            break
                        if sub_invl.sequence == invl.sequence and sub_invl.id > invl.id:                            
                            break
                        if sub_invl.layout_type == 'article':
                            sub_total += sub_invl.price_subtotal
                            
            
            invl.rel_subtotal = sub_total



    # ------------------------- Instance management
    @api.model
    def create(self, vals_list):
        if vals_list is list:            
            for vals in vals_list:
                layout_type = vals.get('layout_type', 'article')
                if not vals.get('name'):
                    vals['name'] = layout_val_2_text(layout_type)
        else:
            layout_type = vals_list.get('layout_type', 'article')
            if not vals_list.get('name'):
                vals_list['name'] = layout_val_2_text(layout_type)
        return super(account_invoice_line, self).create(vals_list)
    
    # ------------------------- Interface related
    @api.onchange('layout_type')
    def _layout_type_change(self):
        for record in self:
            
            if not(record.layout_type == 'article'):
                record.product_id = False
                record.quantity = 1
                record.discount = 0.0
                record.invoice_line_tax_ids = False
                record.name = layout_val_2_text(record.layout_type)
