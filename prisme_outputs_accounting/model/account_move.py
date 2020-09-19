# -*- coding: utf-8 -*-
###########################################################################
#
#    Prisme Solutions Informatique SA
#    Copyright (c) 2020 Prisme Solutions Informatique SA <http://prisme.ch>
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
#    Project ID :    OERP-002-03
#    Phabricator :   T494
#
##########################################################################
from odoo import models

class account_move(models.Model):
    _inherit = 'account.move'
    
    def _get_line_discount(self, line):
        total_discount = 0.0
        
        if line.layout_type == 'article':
            unit_discount =  (line.discount / 100 * (line.price_unit - line.discount_amount)) + line.discount_amount 
            total_discount = line.quantity * unit_discount
            
        if total_discount:
            str_total_discount = '{:.2f}'.format(total_discount * -1)
        else:
            str_total_discount = ''        
        
        return str_total_discount
    
    def _get_partner_address(self):
        partner = self.partner_id
        address_values = [partner.street]
        
        if partner.street2:
            address_values.append(partner.street2)
        
        address_values.append(partner.zip + ' ' + partner.city)
        
        if partner.country_id:
            if partner.country_id.id != self.company_id.partner_id.country_id.id:
                address_values.append(partner.country_id.name)
                
        return address_values
