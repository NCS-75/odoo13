# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HrTimesheetConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'

    timesheet_range = fields.Selection(related='company_id.timesheet_range', string="Timesheet range", readonly=False)
    timesheet_max_difference = fields.Float(related='company_id.timesheet_max_difference', string="Timesheet allowed difference(Hours)", readonly=False)

