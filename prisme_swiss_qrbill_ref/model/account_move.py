# -*- coding: utf-8 -*-
###########################################################################
#
#    Prisme Solutions Informatique SA
#    Copyright (c) 2020 Prisme Solutions Informatique SA <http://prisme.ch>
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
#    Project ID :    
#    Phabricator :   
#
##########################################################################
from odoo import models
from odoo.tools.misc import mod10r

QR_REF_LENGTH = 27

class account_move(models.Model):
    _inherit = 'account.move'
    
    def _compute_qr_ref(self):
        for record in self:
            qr_reference = ''
            if record.invoice_partner_bank_id and record.type == 'out_invoice':
                if record.invoice_partner_bank_id._is_qr_iban():
                    invoice_number = ''
                    
                    # We get the invoice number and remove all non digit characters for qr_ref
                    try:
                        if record.name:
                            for character in record.name:
                                if character.isdigit():
                                    invoice_number += character
                    except:
                        None
                        
                    if invoice_number:
                        
                        issuer_number = record.invoice_partner_bank_id.l10n_ch_postal
                        
                        # we check if the invoice_issuer_number exists and contains only digits
                        if issuer_number and issuer_number.isdigit():
                            
                            # adding the issuer number at the beginning of the qr_reference and the invoice_internal_ref at the end. Padding with 0 in between so the length equals 26
                            qr_reference_no_check_digit = issuer_number + invoice_number.rjust(QR_REF_LENGTH - 1 - len(issuer_number), '0')
                            
                        else:
                            # creating the qr_reference with no invoice_issuer_number at the beginning. Padding with 0 so the length equals 26
                            qr_reference_no_check_digit = invoice_number.rjust(QR_REF_LENGTH - 1, '0')
                    
                        # Setting the qr_reference field with the qr_reference previously created and the check digit at the end
                        qr_reference = mod10r(qr_reference_no_check_digit)
            
            return qr_reference
            
    def _get_invoice_reference_odoo_invoice(self):
        self.ensure_one()
        reference = self._compute_qr_ref()
        if not reference:
            reference = self.name
        return reference