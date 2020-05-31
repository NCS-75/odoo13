# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
#######################################
# Prisme Solutions Informatique SA    #
#######################################
# Author: Hugo Buchs                  #
# Email:  hugo.buchs@prisme.ch        #
# Web:    www.prisme.ch               #
# Date:   09.05.2020                  #
#######################################
{
    'name': 'Prisme Project Enhancement One',
    'version': '2019-05-09 00:00',
    'category': 'Tools',
    'summary': "Adds an 'amount', a 'balance_previous_command' and an 'account' field to the Tasks of the Projects application. It also adds a 'project_id' field to the invoices.",
    'description': """
        This module adds an 'amount', a 'balance_previous_command' and an 'account' field to the Tasks of the Projects application.
        It also adds a 'project_id' field to the invoices.
    """,
    'author': 'Prisme Solutions Informatique SA',
    'website': 'https://www.prisme.ch',
    'depends': [
      'project',
      'account',
      'account_accountant'
    ],
    'data': [
        'views/views.xml'
    ],
    'demo': [
    ],
    'css': [
    ],
    'images': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}