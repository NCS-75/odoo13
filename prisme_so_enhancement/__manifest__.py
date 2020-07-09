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
#    Project ID:    OERP-003-03 - T503
#
#    Modifications:
#
##########################################################################
{
'name': 'Prisme Sales Order Enhancement',
'version': '2020-06-19 10:30',
'category': 'Sales',
'summary': 'ammount discount, rounding on subtotal, partial refusal',
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
    'sale',
	'ons_productivity_sale_layout',
    'sale_margin',
    'stock',
 ],
'data': [
    'views/sale_order_view.xml',
    #'views/sale_report_view.xml',
    'report/report_saleorder_document_template.xml',
	],
	'installable': True,
	'application': True,
	'auto_install': False,
}
