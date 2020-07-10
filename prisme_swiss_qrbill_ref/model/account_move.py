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
#    Project ID :    OERP-002-10
#    Phabricator :   T738
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
            # First we check if this is an outgoing invoice and if a bank account has been provided
            if record.type == 'out_invoice' and record.invoice_partner_bank_id:
                
                # We need to generate the QR reference only if the bank account has a QR IBAN
                if record.invoice_partner_bank_id._is_qr_iban():
                    
                    # If an ISR reference has been generated, we use it as our QR reference since it's the same structure and data.
                    # Used for "compatibility" between ISR and QR.
                    if record.l10n_ch_isr_number:
                        qr_reference = record.l10n_ch_isr_number
                    
                    # Otherwise we generate the QR reference with the same structure as ISR -> ISR subscription number as first digits and invoice number as last digits.
                    else:
                        invoice_number = ''
                        
                        # We get the invoice number and get only digital characters
                        if record.name:
                            for character in record.name:
                                if character.isdigit():
                                    invoice_number += character
                        
                        # If the invoice number actually had digital characters, we proceed to the QR reference generation
                        if invoice_number:
                            
                            issuer_number = record.invoice_partner_bank_id.l10n_ch_postal
                            
                            # We check if the invoice_issuer_number exists and contains only digits
                            if issuer_number and issuer_number.isdigit():
                                
                                # Adding the issuer number at the beginning of the qr_reference and the invoice_internal_ref at the end. Padding with 0 in between so the length equals 26
                                qr_reference_no_check_digit = issuer_number + invoice_number.rjust(QR_REF_LENGTH - 1 - len(issuer_number), '0')
                                
                            else:
                                # Creating the qr_reference with no invoice_issuer_number at the beginning. Padding with 0 so the length equals 26
                                qr_reference_no_check_digit = invoice_number.rjust(QR_REF_LENGTH - 1, '0')
                        
                            # Adding the check digit to the end of the QR reference
                            qr_reference = mod10r(qr_reference_no_check_digit)
            
            return qr_reference
    
    def _get_invoice_reference_odoo_invoice(self):
        """Returns the result of _compute_qr_ref if a value has been returned, or calls super otherwise."""
        
        reference = self._compute_qr_ref()
        if not reference:
            reference = super(account_move)._get_invoice_reference_odoo_invoice()
        return reference