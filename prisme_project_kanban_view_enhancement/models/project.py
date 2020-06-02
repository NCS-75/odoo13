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

from odoo import models, api, fields, _

class Project(models.Model):
    _inherit = 'project.project'
    
    prisme_sequence = fields.Integer('Sequence')
    
    
    @api.model
    def create(self, vals):
        vals_account = {'name': vals.get("name")}
        analytic_account= self.env['account.analytic.account']
        vals['analytic_account_id'] = analytic_account.create(vals_account).id
        vals['prisme_sequence'] = self.env['ir.sequence'].next_by_code('prisme.project.sequence') or 0
        return super(Project, self).create(vals)
