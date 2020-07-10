
{
'name': 'Prisme Reporting for Stock',
'version': '2020-07-10 09:30',
'category': 'Warehouse',
'summary': 'More fields for stock picking reports',
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
            'stock',
            'sale_stock',
            'sale_management',
            'purchase',
            'delivery',
],
'init_xml': [],
'data': [
               'view/stock_picking.xml',
               'report/report_prisme_picking.xml',
],
'installable': True,
'active': False,
'images': [
           'image/picking_report.jpg',
           ],
}
