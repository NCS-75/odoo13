{
'name': 'Prisme Invoicing Timesheet Report',
'version': '2017-12-01 16:24',
'category': 'Human Resources',
'summary': 'Report for invoiced timesheets',
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
        'prisme_invoicing_timesheet'
        ],
'init_xml': [],
    'update_xml': [
        'report/templates/account_invoice_detail.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
	'application': True,
}
