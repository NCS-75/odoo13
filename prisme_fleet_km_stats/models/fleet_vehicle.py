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

from odoo import models

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
# Gets the most recent odometer value for the give vehicle
    def _get_odometer(self):
        FleetVehicalOdometer = self.env['fleet.vehicle.odometer']
        for record in self:
            vehicle_odometer = FleetVehicalOdometer.search([('vehicle_id', '=', record.id)], limit=1, order='date desc, value desc')
            if vehicle_odometer:
                record.odometer = vehicle_odometer.value
            else:
                record.odometer = 0

            
    
