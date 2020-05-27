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

class account_move_line(models.Model):
    _inherit = 'account.move.line'

    # ------------------------- Fields management
    def _is_number(self,s):
        try:
            float(s)
            return True
        except:
            return False

    layout_type = fields.Selection(layout.LAYOUTS_LIST, 'Layout type', required=True, index=True, default=lambda *a: 'article')
    rel_subtotal = fields.Float(compute='_sub_total', string='Rel. Sub-total', digits='Account')

#     _order = 'move_id desc, sequence asc , id'

    def _sub_total(self):
        for invl in self:
 
            invl.rel_subtotal = 0
            invl.sequence_number_next = 2
 
            sub_total = 0.0
 
            if invl.layout_type == 'subtotal' and self._is_number(invl.move_id.id):
                id = invl.id
                if not isinstance(id, int):
                    id = id.origin
                sub_invls = self.env['account.move.line'].search([('move_id','=',invl.move_id.id),('sequence','<=',invl.sequence),('id','!=',id)], order='sequence desc,id desc')
                for sub_invl in sub_invls:
                    if invl.sequence > sub_invl.sequence or (invl.sequence == sub_invl.sequence and id > sub_invl.id ):
                        if (sub_invl.layout_type == 'subtotal') or (sub_invl.sequence == invl.sequence and sub_invl.id > id):                             
                            break
                        if sub_invl.layout_type == 'article' and not sub_invl.account_internal_type == 'receivable' and not sub_invl.tax_group_id and not sub_invl.move_id.account_internal_type == 'payable':
                            sub_total += sub_invl.price_subtotal
            invl.rel_subtotal = sub_total
 
    # ------------------------- Instance management
    @api.model_create_multi
    def create(self, vals_list):    
        for vals in vals_list:
            layout_type = vals.get('layout_type')
            if not vals.get('name'):
                vals['name'] = layout.layout_val_2_text(layout_type)                
        return super(account_move_line, self).create(vals_list)
  
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