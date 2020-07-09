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
#    Project ID :    OERP-002-09
#    Phabricator :   T601
#
##########################################################################
{
    'name': 'Prisme Reporting for Accounting with QR-bill',
    'version': '2020-07-08 11:30',
    'category': 'Accounting & Finance',
    'summary': """QR-bill for payment slips in Switzerland""",
    'description'  : """
Adds the swiss QR-bill to Prisme invoices.
""",
    'author': 'Prisme Solutions Informatique SA',
    'website': 'https://www.prisme.ch',
    'depends': [
        'l10n_ch',
        'prisme_swiss_qrbill_ref',
        'prisme_outputs_accounting',
    ],
    'data': [
        'report/report_invoice.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
