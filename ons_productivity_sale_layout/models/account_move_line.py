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
 
    # ------------------------- Instance management
    @api.model_create_multi
    def create(self, vals_list):    
        for vals in vals_list:
            layout_type = vals.get('layout_type')
            if not vals.get('exclude_from_invoice_tab') and not vals.get('name'):
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