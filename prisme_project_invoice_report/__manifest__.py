# -*- coding: utf-8 -*-
{
    'name': 'Prisme Project invoice generator',
    'version': '2019-09-14 00:00',
    'category': 'Tools',
    'summary': "Adds a button to each project to print the financial view for this project",
    'description': """
        Adds a button to each project to print the financial view for this project.
    """,
    'author': 'Prisme Solutions Informatique SA',
    'website': 'https://www.prisme.ch',
    'depends': [
      'project',
      'contacts',
      'account',
      'prisme_project_enhancement'
    ],
    'qweb': [
      
    ],
    'data': [
      'views/views.xml',
      'report/report.xml'
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