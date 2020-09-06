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

from odoo import models, api, fields

class Project(models.Model):
    _name = 'project.project'
    _inherit = ['project.project', 'mail.activity.mixin']
    prisme_sequence = fields.Char('Prisme Analytic Account Sequence', related='analytic_account_id.prisme_sequence')


    @api.onchange('partner_id')
    def _check_change(self):
        self.analytic_account_id.partner_id = self.partner_id

    @api.model
    def create(self, vals):
        if not 'analytic_account_id' in vals:
            vals_account = {'name': vals.get("name"),
                            'prisme_sequence': (self.env['ir.sequence'].next_by_code('prisme.analytic.account.sequence') or 0),
                            'partner_id': vals.get('partner_id')}
            analytic_account= self.env['account.analytic.account']
            vals['analytic_account_id'] = analytic_account.create(vals_account).id
        return super(Project, self).create(vals)
        
    @api.multi
    def write(self, vals):
        for rec in self:
            vals = self._prepare_params_for_update(vals, rec)
            if vals['has_problem']:
                act_type_id = self.env['mail.activity.type'].search(
                    [('name', 'ilike', 'Record Has Problems')], limit=1).id
                self.env['mail.activity'].create({
                    'res_model_id': self.env.ref( < my_model_id > ).id,
                    'res_id': rec.id,
                    'user_id': rec.user_id.id,
                    'activity_type_id': act_type_id,
                    'date_deadline': vals['date_submitted'],
                })
        return super(Project, self).write(vals)
