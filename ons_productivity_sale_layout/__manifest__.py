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
#    Project ID:    NEX001-010-001 - T257
#
##########################################################################
{
    'name' : 'Open-Net Productivity: sale and invoice layouts',
    'version' : '2019-09-20 15:15',
    'author' : 'Open Net SaRL',
    'category' : 'Sales Management',
    'summary': 'Layout management for Sales Orders and Invoices',
    'website': 'http://www.open-net.ch',
    'images' : [],
    'depends' : ['sale_management'],
    'data': [
        'views/sale_order_view.xml',
        'views/account_move_view.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['images/icon.png','images/banner.png'],
    'license': '',
}
