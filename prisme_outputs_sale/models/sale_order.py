###########################################################################
#
#    Prisme Solutions Informatique SA
#    Copyright (c) 2016 Prisme Solutions Informatique SA <http://prisme.ch>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#    You should have received a copy of the GNU Affero General Public Lic
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Project ID:    OERP-003-02    T502
#
##########################################################################
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class sale_order(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'
    

    print_totals = fields.Boolean('Print Totals',
                                              help='Show the totals on the ' + 
                                              'botom of the quotation/SO. ' + 
                                              'Used, for example, to offer 2 ' + 
                                              'choices to a customer and ' + 
                                              ' don\'t show a useless total.',
                                              default=True)
    print_vat = fields.Boolean('Print VAT',
                                            help='Show the VAT on the bottom ' + 
                                            ' on the Quotation/SO. Warning: ' + 
                                            'you cannot print VAT if you ' + 
                                             'don\'t print the totals.',
                                             default=True)
    footer_comment = fields.Text('Footer comment')
    header_comment = fields.Text('Header comment')

    @api.constrains('print_vat')
    def _check_printings(self):
        for sale_order in self:
            if not sale_order.print_totals:
                if sale_order.print_vat:
                    raise ValidationError('You can\'t print VAT if you don\'t print totals')
                
    # Bug fix - change default print button to custom prisme report
    def print_quotation(self):
        '''
        This function prints the sales order and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        return self.env['report'].get_action(self, 'sale.order.email.prisme')   
