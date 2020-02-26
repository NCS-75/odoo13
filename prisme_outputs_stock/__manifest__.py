
{
'name': 'Prisme Reporting for Stock',
'version': '2020-02-21 10:45',
'category': 'Warehouse',
'summary': 'More fields for stock picking reports',
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
            'stock',
            'sale_stock',
            'purchase',
],
'init_xml': [],
'update_xml': [
               'view/stock_picking.xml',
               'report/report_prisme_picking.xml',
], 
'demo_xml': [],
'test': [],
'installable': True,
'active': False,
'images': [
           'image/picking_report.jpg',
           ],
}
