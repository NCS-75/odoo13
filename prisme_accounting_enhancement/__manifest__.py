
{
"name": "Prisme Accounting Enhancement",
"version": "2020-06-18 16:00",
"category": "Finance",
'summary' : "amount discount, rounding subtotal",
"author": "Prisme Solutions Informatique SA",
"website": "http://www.prisme.ch",
"depends": [
    "analytic",
    "product",
    "sale_management",
    "stock",
    "account_accountant",
    "prisme_so_enhancement",
    "account_analytic_default"
 ],
"data": [
    "data/migration.sql",
    "views/account_move_line_view.xml",
    "views/account_move_view.xml",
],
"installable": True,
"active": False,
"images": [
           "images/product_analytic_acc.jpg",
           "images/chart_analytic_acc_filter.jpg",
           "images/invoice_line_disc_type.jpg",
           "images/invoice_rounding.jpg",
           ],
}
