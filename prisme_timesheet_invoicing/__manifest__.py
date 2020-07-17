{
'name': 'Prisme Timesheet Invoicing',
'version': '2017-12-01 16:24',
'category': 'Human Resources',
'summary': '',
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
        'prisme_timesheet_activity'
        ],
'init_xml': [],
    'update_xml': [
        'view/hr_timesheet_invoice_factor.xml',
        'view/account_analytic_account.xml',
        'view/view_hr_timesheet_line.xml',
        'view/view_invoice.xml',
        'view/view_project_project.xml',
        'wizard/hr_timesheet_invoice_create_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
	'application': True,
}
