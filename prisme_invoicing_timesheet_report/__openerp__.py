{
'name': 'Prisme Timesheet Enhancement',
'version': '2017-12-01 16:24',
'category': 'Human Resources',
'summary': 'start / end time, reports',
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
        'prisme_invoicing_timesheet'
        ],
'init_xml': [],
    'update_xml': [
        #'report/templates/hr_timesheet_sheet_check.xml',
        #'report/templates/account_analytic_line.xml',
        'report/templates/account_invoice_detail.xml',
        'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
	'application': True,
}
