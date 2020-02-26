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
#    Project ID:    OERP-006-03
#    Phabricator:   T516
#
##########################################################################
from odoo import models, fields, api, _

class stock_picking(models.Model):
    _inherit = "stock.picking"
    
    psi_transporter = fields.Char("Transporter")
    
    # Gets the shipping date for the given stock.picking
    def get_shipping_date(self, picking):
        shipping_date = None
        for line in picking.move_lines:
            shipping_date = line.date

        return shipping_date
    
    # Gets the backorder quantity for the given backorder and line
    def get_backorder_quantity(self, picking, move):
        sale_line_id = move.sale_line_id
        backorder = self.get_backorder_picking(picking)
        back_order_quantity = 0.0
        if(backorder and sale_line_id):
            back_order_id = backorder.id
            back_order_line = backorder.env['stock.move'].search([('sale_line_id','=',sale_line_id.id),('picking_id','=',back_order_id)])
            
            if back_order_line:
                back_order_quantity = back_order_line.product_uom_qty
            
        return back_order_quantity
    
    # Gets the back order related to the given stock.picking
    def get_backorder_picking(self, picking):
        result = None
        picking_id = picking.id
        backorder_picking = picking.env["stock.picking"].search([("backorder_id", "=", picking_id)])
        
        if backorder_picking:
            result = backorder_picking
        return result
    
    # Checks if the give move is already in the origin picking
    def is_in_origin_picking(self, picking, move):
        result = False
        move_sale_line = move.sale_line_id
        if(move_sale_line and self.env['stock.move'].search([('picking_id', '=', picking.id),('sale_line_id','=', move_sale_line.id)])):
            result = True
        return result
    
    # Gets the S/N list for the given move
    def get_move_sn(self, move):
        sn = []
        for move_line in self.env['stock.move.line'].search([('move_id', '=', move.id)]):
            if(move_line.lot_name or (move_line.lot_id and move_line.lot_id.name)):
                sn.append(move_line.lot_name or (move_line.lot_id and move_line.lot_id.name))
        
        print(str(sn))
        return sn

