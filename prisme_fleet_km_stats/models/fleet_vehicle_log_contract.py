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
#    Project ID:    OERP-004-05
#    Phabricator :  T594
#
##########################################################################

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError

class FleetVehicleLogContract(models.Model):
    _inherit = 'fleet.vehicle.log.contract'
   
    contract_duration = fields.Float(compute='_onchange_contract_duration', string='Contract duration', default=0, readonly=True, digits=(12,2))
    contract_duration_unit = fields.Text(readonly=True, compute='_set_contract_duration_unit')
    odometer_last_date = fields.Date('Odometer Last Date', compute='_get_last_odometer')
    odometer_last_value = fields.Integer('Odometer Value', compute='_get_last_odometer')
    cur_contract_km = fields.Integer(string='Last odometer from this contract', compute='_compute_contract_last_odometer')
    
    km_plan_yearly = fields.Integer('Km planned per year',  required=True, default=25000)
    km_plan_monthly = fields.Integer('Km planned per month', compute='_onchange_km_plan_yearly')
    
    km_cur_perf = fields.Integer(string='Kilometers currently performed during this contract', compute='_compute_km_cur_perf')
    km_cur_perf_percent = fields.Integer(compute='_compute_km_cur_perf_percent')

    km_cur_perf_year = fields.Integer(string='Kilometers currently performed this year', compute='_compute_km_cur_perf_year')
    km_cur_perf_year_percent = fields.Integer(compute='_compute_km_cur_perf_year_percent')
    
    km_cur_perf_month = fields.Integer(string='Kilometers currently performed this month', compute='_compute_km_cur_perf_month')
    km_cur_perf_month_percent = fields.Integer(compute='_compute_km_cur_perf_month_percent')
    
    # Sets the contract's duration in years, given the the start date and end date.
    @api.onchange('start_date', 'expiration_date')
    def _onchange_contract_duration(self):
        for record in self:
            start_date = record.start_date
            exp_date = record.expiration_date
            
            # Rounding the contract's duration up by one week.
            exp_date_rounded = exp_date + timedelta(days=7)
            delta_date = relativedelta(exp_date_rounded, start_date)
            duration = delta_date.years + delta_date.months / 12
            
            record.contract_duration = duration

    # Checks whether the contract's end date is higher than start date, and raises a validation error otherwise.
    @api.constrains('start_date', 'expiration_date')
    def _constrains_contract_duration(self):
        for record in self:
            start_date = record.start_date
            exp_date = record.expiration_date
            if start_date >= exp_date:           
                raise ValidationError(_("Contract's expiration date has to be higher than start date."))                               
    
    # Sets the contract's duration unit to 'year' or 'years' given the amount of years.
    @api.depends('contract_duration')
    def _set_contract_duration_unit(self):
        for record in self:
            duration = record.contract_duration
            # Cheking if there is on aor several years
            if duration > 1:
                record.contract_duration_unit = _('years')
            else:
                record.contract_duration_unit = _('year')
    
    # Sets the last odometer value of the actual contract.
    def _compute_contract_last_odometer(self):
        for record in self:
            record.cur_contract_km = 0
            contract_start_date = record.start_date
            contract_exp_date = record.expiration_date
            if(contract_start_date and contract_exp_date):
                # Getting the last odometer entry
                record_odometer = self.env['fleet.vehicle.odometer'].search([('vehicle_id', '=', record.vehicle_id.id),('date', '<=', date.today()),('date', '<=', contract_exp_date),('date', '>=', contract_start_date)], offset=0, limit=1, order="date desc")
                if(record_odometer and record_odometer.date):
                    record.cur_contract_km = record_odometer.value
    
    # Sets the monthly planned kilometers from the yearly planned kilometers
    @api.onchange('km_plan_yearly')
    @api.depends('km_plan_yearly')
    def _onchange_km_plan_yearly(self):
        # Calculates the monthly plan given the annual kilometers
        plan_montlhy = self.km_plan_yearly / 12
        self.km_plan_monthly = plan_montlhy
    
    # Sets the last odometer date and value (not related to the contract's dates)
    def _get_last_odometer(self):        
        for record in self:
            last_odometer = self.env['fleet.vehicle.odometer'].search([('vehicle_id', '=', record.vehicle_id.id)], offset=0, limit=1, order="date desc, value desc")
            record.odometer_last_date = last_odometer.date
            record.odometer_last_value = last_odometer.value
    
    # Sets the total kilometers currently performed for the actual contract
    @api.depends('vehicle_id')
    def _compute_km_cur_perf(self):
        for record in self:
            last_contract_km = 0
            
            # Getting the last odometer entry from the previous contract
            odometer_last_contract = self.env['fleet.vehicle.odometer'].search([('vehicle_id', '=', record.vehicle_id.id),('date', '<', record.start_date)], offset=0, limit=1, order="date desc")
            if(odometer_last_contract and odometer_last_contract.value):
                last_contract_km = odometer_last_contract.value
            
            # If the km performed are negative, we assume 0 km were performed
            km_performed = record.cur_contract_km - last_contract_km
            if(km_performed >= 0):
                record.km_cur_perf = km_performed
            else:
                record.km_cur_perf = 0
    
    # Sets the total kilometers currently performed for the actual contract as a percentage of the planned kilometers
    @api.onchange('km_cur_perf', 'km_plan_yearly', 'contract_duration')
    def _compute_km_cur_perf_percent(self):
        for record in self:
            
            amount = record.km_plan_yearly
            if record.contract_duration != 0:
                amount *= record.contract_duration
               
            if not amount:
                record.km_cur_perf_percent = 0
            else:
                record.km_cur_perf_percent = 100 * record.km_cur_perf / amount + 0.5

            # A warning is shown if the km performed excess the contract's limit
            if self.km_cur_perf > amount:
                return {
                'warning': {
                    'title': _("WARNING"),
                    'message': _("Odometer excess the contract"),
                },
            }
    
    # Sets the kilometers performed this year for the actual contract 
    @api.depends('vehicle_id')
    def _compute_km_cur_perf_year(self):
        for record in self:
            last_year_odometer_value = 0
            # Creating date for the first day of the actual year. We will search the first record before this day.
            first_day_year = datetime(date.today().year, 1,1)
            
            # Getting the last odometer from previous year
            record_odometer = self.env['fleet.vehicle.odometer'].search([('vehicle_id', '=', record.vehicle_id.id),('date', '<', first_day_year)], offset=0, limit=1, order="date desc")
            if(record_odometer and record_odometer.value):
                last_year_odometer_value = record_odometer.value

            # Subtracts the last value of the last year to the actual value of the odometer
            km_performed = record.cur_contract_km - last_year_odometer_value
            if(km_performed >= 0):
                record.km_cur_perf_year = km_performed
            else:
                record.km_cur_perf_year = 0
            
    # Sets the kilometers performed this year for the actual contract as a percentage of the planned kilometers
    @api.depends('km_cur_perf_year', 'km_plan_yearly')
    def _compute_km_cur_perf_year_percent(self):
        for record in self:
            if not record.km_plan_yearly:
                record.km_cur_perf_year_percent = 0
            else:
                if record.contract_duration % 1 == 0:
                    record.km_cur_perf_year_percent = 100 * record.km_cur_perf_year / record.km_plan_yearly + 0.5
                else:
                    today = date.today()
                    if record.start_date.month != 1 & today.year == record.start_date.year:
                        record.km_cur_perf_year_percent = 100 * record.km_cur_perf_year / (record.km_plan_yearly/12*record.start_date.month) + 0.5
                    elif record.expiration_date.month != 1 & today.year == record.expiration_date.year:
                        record.km_cur_perf_year_percent = 100 * record.km_cur_perf_year / (record.km_plan_yearly/12*record.expiration_date.month) + 0.5
    
    # Sets the kilometers performed this month for the actual contract
    @api.depends('vehicle_id')
    def _compute_km_cur_perf_month(self):
        for record in self:
            last_month_odometer_value = 0
            # Creating date for the first day of the actual month. We will search the first record before this day.
            today = date.today()
            first_day_month = datetime(today.year, today.month, 1)
            
            # Getting the last odometer from previous month
            record_odometer = self.env['fleet.vehicle.odometer'].search([('vehicle_id', '=', record.vehicle_id.id),('date', '<', first_day_month)], offset=0, limit=1, order="date desc")
            if(record_odometer and record_odometer.value):
                last_month_odometer_value = record_odometer.value
            
            # Subtracts the last value of the last month to the actual value of the odometer
            km_performed = record.cur_contract_km - last_month_odometer_value
            if(km_performed >= 0):
                record.km_cur_perf_month = km_performed
            else:
                record.km_cur_perf_month = 0
    
    # Sets the kilometers performed this month for the actual contract as a percentage of the planned kilometers
    @api.depends('km_cur_perf_month', 'km_plan_monthly')
    def _compute_km_cur_perf_month_percent(self):
        for record in self:
            if not record.km_plan_monthly:
                record.km_cur_perf_month_percent = 0
            else:
                record.km_cur_perf_month_percent = 100 * record.km_cur_perf_month / record.km_plan_monthly + 0.5