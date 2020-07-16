# -*- coding: utf-8 -*-
#######################################
# Prisme Solutions Informatique SA    #
#######################################
# Author: Hugo Buchs                  #
# Email:  hugo.buchs@prisme.ch        #
# Web:    www.prisme.ch               #
# Date:   23.05.2020                  #
#######################################
{
    'name': 'Prisme Timesheet Activity',
    'version': '2019-05-09 00:00',
    'category': 'Tools',
    'summary': "Adds a list and form view for timesheet activities",
    'description': """
        This module adds a list and form view for timesheet activities.
    """,
    'author': 'Prisme Solutions Informatique SA',
    'website': 'https://www.prisme.ch',
    'depends': [
      'hr_timesheet',
      'hr_timesheet_attendance',
      'analytic',
      'account',
      'account_accountant',
      'mail',
      'sale_management'
    ],
    'data': [
        'views/view_timesheet_activity.xml',
        'security/ir.model.access.csv',
        'security/hr_timesheet_sheet_security.xml',
        'data/hr_timesheet_sheet_data.xml',
        'views/hr_timesheet_sheet_views.xml',
        'views/hr_department_views.xml',
        'views/hr_timesheet_sheet_config_settings_views.xml',
        'views/hr_employee.xml',
        'data/hr_timesheet_sheet_timesheet_grid_data.xml'
    ],
    'demo': [
    ],
    'css': [
    ],
    'images': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
