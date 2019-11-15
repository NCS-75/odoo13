# -*- coding: utf-8 -*-
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
#    Project ID:    OERP-004-02
#
#    Modifications:
#
##########################################################################
from odoo import api, models, _
from odoo.exceptions import UserError


class account_move(models.Model):
    _inherit = "account.move"

    def unlink(self):
        for move in self:
            
            if move.name != '/' and not self._context.get('force_delete') and move.state == "posted"):                
                raise UserError(_("You cannot delete an entry which has been posted."))
            move.line_ids.unlink()
#       Prisme : call grandparent method class, otherwise with "super" the commented exception is called from super class            
        return models.Model.unlink(self)