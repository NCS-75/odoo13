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
#    Project ID:    OERP-005-03 - T730
#
##########################################################################

from odoo import models, fields, api, SUPERUSER_ID

class PurchaseOrderLine(models.Model):
    _inherit = 'project.project'
    
    @api.model
    def stage_groups(self, stages, domain, order):

        stage_ids = stages._search(domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)


    
    stage_id = fields.Many2one('prisme.project.stage', string="Stage", group_expand='stage_groups')