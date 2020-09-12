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
#Inherit task model to change it
class prisme_task(models.Model):
    _inherit = 'project.task'
    ammount = fields.Float(string='Amount', digits=(102,2))
    balance_previous_command = fields.Float(string='Balance previous command', digits=(102,2))
    account_id = fields.Many2one('account.account', string='Account')