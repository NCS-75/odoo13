# -*- coding: utf-8 -*-
#######################################
# Prisme Solutions Informatique SA    #
#######################################
# Author: Hugo Buchs                  #
# Email:  hugo.buchs@prisme.ch        #
# Web:    www.prisme.ch               #
# Date:   09.05.2020                  #
#######################################
from odoo import models, fields, api
#Inherit invoice model to change it
class prisme_invoice(models.Model):
    _inherit = 'account.move'
    project_id = fields.Many2one('account.analytic.account', string='Analytic account')
    #account_id = fields.Many2one('account.account', string='Account',
    #    required=True, readonly=True, states={'draft': [('readonly', False)]},
    #    domain=[('deprecated', '=', False)], help="The partner account used for this invoice.")