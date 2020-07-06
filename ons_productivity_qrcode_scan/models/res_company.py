# -*- coding: utf-8 -*-
#
#  Copyright (c) 2020 - Open-Net Ltd. All rights reserved.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    qr_product_id = fields.Many2one('product.product', string='Product')
    qr_account_tax_id = fields.Many2one('account.tax', string="Tax")
