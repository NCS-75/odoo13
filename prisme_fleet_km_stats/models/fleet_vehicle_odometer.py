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
from odoo import api, models, _
from odoo.exceptions import ValidationError

# Add constrains on the 'value' field of the original 'fleet.vehicle.odometer' class
class FleetVehicleOdometer(models.Model):
    _inherit = 'fleet.vehicle.odometer'
    
    # If the user tries to save an odometer with a negative value, send an error.
    @api.constrains('value')
    def _constrains_odometer(self):
        for record in self:
            if record.value < 0:
                raise ValidationError(_("Odometer value may not be negative."))
            
    
