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
#    Project ID:    OERP-003-06 - T506
#
#    Modifications:
#
##########################################################################
{
    "name": "Prisme SO Lines",
    "version": "2019-09-20 15:15",
    "author": "Prisme Solutions Informatique SA",
    "category": "Generic Modules/Accounting",
    "summary": "sale orders lines list",
    "website": "https://www.prisme.ch",
    "depends": [
        'sale',
        'sale_stock',
        'sale_management',
        'ons_productivity_sale_layout',
    ],
    "demo": [],
    "data": [
        "view/view_so_lines.xml"
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
    "active": False
}
