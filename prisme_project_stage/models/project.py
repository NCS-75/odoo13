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
#    Project ID:    
#
##########################################################################

from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'project.project'
    
    @api.model
    def stage_groups(self, present_ids, domain, **kwargs):
        stages = self.env['prisme.project.stage'].search([]).name_get()
        return stages, None

    _group_by_full = {
        'stage_id': stage_groups,
    }
    
    stage_id = fields.Many2one('prisme.project.stage', string="Stage")