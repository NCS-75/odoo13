# -*- coding: utf-8 -*-
#
#  File: __openerp__.py
#  Module: ons_productivity_sale_layout
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2013 Open-Net Ltd. All rights reserved.
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name' : 'Open-Net Productivity: sale and invoice layouts',
    'version' : '2019-09-20 15:15',
    'author' : 'Open Net SaRL',
    'category' : 'Sales Management',
    'summary': 'Layout management for Sales Orders and Invoices',
    'website': 'http://www.open-net.ch',
    'images' : [],
    'depends' : ['sale',
	'sale_management'],
    'data': [
        'views/layout_view.xml',
    ],
    'js': [
    ],
    'qweb' : [
    ],
    'css':[
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['images/icon.png','images/banner.png'],
    'license': '',
}
