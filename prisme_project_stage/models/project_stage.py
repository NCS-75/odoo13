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

from odoo import models, fields

class project_stage(models.Model):
    _name = 'prisme.project.stage'
    _description = "Project Stage"
    _order = 'sequence, id'
    

    
    name = fields.Char(string="Project Stage", required=True)
    project_ids = fields.One2many('project.project', 'stage_id', string='Projects')
    sequence = fields.Integer(default=1)