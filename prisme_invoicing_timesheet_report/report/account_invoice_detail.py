from odoo import models, fields, api, _
from operator import itemgetter, attrgetter
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class account_invoice_detail(models.Model):
    _name = "account.move"
    _inherit = "account.move"
    
    account_invoice_detail_total = 0
    account_invoice_detail_amount = 0
    
    def getSortedList(self, oid):
        cr = self.env.cr
        cr.execute("select acc.name, ptr.name, line.date, line.name, line.unit_amount, prd.default_code, tmpl.list_price,fact.factor,fact.name,prd.id,acc.pricelist_id,acc.partner_id from account_analytic_line line, account_analytic_account acc, res_users usr, res_partner ptr, product_product prd, product_template tmpl,hr_timesheet_invoice_factor fact where fact.id=line.to_invoice and prd.product_tmpl_id=tmpl.id and line.product_id=prd.id and usr.partner_id=ptr.id and line.user_id=usr.id and acc.id=line.account_id and line.move_id is null and line.invoice_id="+str(oid)+" order by date, line.time_beginning")
        res = cr.fetchall()
        sortedList = []
        sortedList = sorted(res,key=itemgetter(0,1,5,8,2))  
        
        
        for row in sortedList:
            row_list = list(row)
            row_list[2] = datetime.strptime(row_list[2], '%Y-%m-%d').strftime('%d.%m.%Y')
            row = tuple(row_list)
            
        for idx, row in enumerate(sortedList):
            row_list = list(row)
            row_list[2] = datetime.strptime(row_list[2], '%Y-%m-%d').strftime('%d.%m.%Y')
            sortedList[idx] = row_list
        return sortedList
    
    def getAndResetTotal(self):
        act_total = account_invoice_detail.account_invoice_detail_total
        account_invoice_detail.account_invoice_detail_total = 0
        return "{0:.2f}".format(act_total)
    
    def getAndResetAmount(self):
        act_amount = account_invoice_detail.account_invoice_detail_amount
        account_invoice_detail.account_invoice_detail_amount = 0
        return "{0:.2f}".format(act_amount)
    
    def getprice(self,pricelist_id, product_id, partner_id, quantity):
        #context =  {'date':False,}
        price = 0
        pl = self.env['product.pricelist'].browse(pricelist_id)
        price = pl.price_get(product_id, quantity, partner=partner_id)[pl.id]
        return price
    
    def addToTotal(self, l_total):
        account_invoice_detail.account_invoice_detail_total = account_invoice_detail.account_invoice_detail_total + l_total
        
    def addToAmount(self, l_amount):
        account_invoice_detail.account_invoice_detail_amount = account_invoice_detail.account_invoice_detail_amount + l_amount
        
    def display_address(self, address_record, without_company=False):
        # FIXME handle `without_company`
        return address_record.contact_address
    
        # This method return the address block.
    # The first value is the address object.
    # The second value is the options to pass to the QWeb method.
    def get_contact(self, value, options=False):
        if not value:
            _logger.info("No value !")
            return ""
        
        
        try:
            # Try to use the QWeb function (should works)
            _logger.info("Get QWeb !")
            return self._get_contact_qweb(value, options)
        except Exception as e:
            #print("Failed to generate address with QWeb method: " + str(e))
            # Otherwise use the older version (from Odoo 7)
            try:
                _logger.info("Get Display !")
                return self._get_contact_display_address(value)
            except Exception as e:
                _logger.info("Massive failure bro !"+str(e))
                print("Failed to generate address with RML method: " + str(e))
    
    # This method return the address block.
    # The first value is the address object.
    def _get_contact_display_address(self, value):
        # Please use get_contact(self, value, options)
        # https://github.com/odoo/odoo/blob/7.0/addons/sale/report/sale_order.rml#L119
        
        contact_str = ""
        # No need to show the company name twice
        
        if isinstance(value.parent_name, str) and not value.is_company:
            contact_str += value.parent_name + "\n"
        if value.parent_name != value.name:
            if value.title:
                contact_str += value.title.name + " "
            contact_str += value.name + "\n"
        # Call _display_address and let it handle the company name (without_company=False)
        contact_str += value._display_address(True)
        
        return contact_str
        
    # This method return the address block.
    # The first value is the address object.
    # The second value is the options to pass to the QWeb method.
    def _get_contact_qweb(self, value, options):
        raise Exception("Disabled, Move Contact under Company in address")
        # Please use get_contact(self, value, options)
        # https://github.com/odoo/odoo/blob/10.0/addons/sale/report/sale_report_templates.xml#L12
        
        # Get env var from self or the value
        env = self.env if hasattr(self, 'env') else value.env
        
        # Call the QWeb widget. The function returns the HTML for a QWeb report
        contact_str = env['ir.qweb.field.contact'].value_to_html(value, options)
        
        # Transform <br/> and <br> (HTML New Line) to \n (New Line character) with Regex (re)
        contact_str = re.sub('<br\s*/?>', '\n', contact_str.strip())
        
        # ET.fromstring(contact_str) => Parse XML (HTML) to ETree Object
        # ET.tostring(..., method='text') => Stringify ETree Object to Plain text (remove tags)
        # This line remove every tags in contact_str
        contact_str = ET.tostring(ET.fromstring(contact_str), method='text')
        
        # This line use Regex (re) to replace multiple new line (empty or whitespaced) to one new line
        # "\s*(\n|\r)+\s*":
        # - "\s*" => Zero or more Whitespace (space, tab, ...)
        # - "(\n|\r)+" One or more new line (\n) or carriage return (\r)
        contact_str = re.sub('\s*(\n|\r)+\s*', '\n', contact_str.strip())
        return contact_str