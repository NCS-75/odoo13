# -*- coding: utf-8 -*-
# © 2020 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name' : 'Scan your QR-Factures (QR-invoices) easily',
    'version' : '1.0',
    'author' : 'Open Net Sàrl',
    'category' : 'Accounting',
    'website': 'https://www.open-net.ch',
    'license': 'AGPL-3',
    'description' : """
**Features list :**
    * Allows you to scan swiss QR code from swiss invoice (paper) and autofill informations in account invoice (odoo).
""",
    'depends' : [
        'l10n_ch'
    ],
    'data': [
        'wizard/qr_code_scan_to_invoice.xml',
        'views/view_res_partner.xml',
        'views/view_res_company.xml'

    ],
    'installable': True,
    'auto_install': True,
    'images': [
        'static/description/QR_ready.png'
    ]
}
