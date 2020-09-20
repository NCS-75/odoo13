from odoo import api, fields, models, _
from odoo.exceptions import UserError

INTEGRITY_HASH_LINE_FIELDS = ('debit', 'credit', 'account_id', 'partner_id')

class account_move_line(models.Model):
    _inherit = "account.move.line"
   
    # Field copied to remove the '%' in the label        
    discount = fields.Float(string='Discount (percent)', digits='Discount', default=0.0)
    #New field for discount in amount
    discount_amount = fields.Float(string='Discount (amount)', digits=(16, 2), default=0.0)
    
    origin_price_unit = fields.Float(string='Origin price unit', default=0.0)
    
    @api.onchange('discount')
    def _check_discount_percent(self):
        """Checks if discount field is set between 0 and 100, and raises an error otherwise."""
        for record in self:
            discount_value = record['discount']
            if discount_value:
                error = ''
                if (discount_value < 0.0):
                    error = _("A discount in percent cannot be negative !")
                elif (discount_value > 100.0):
                    error = _("A discount in percent cannot be bigger than 100 !")
                
                if error:
                    self._display_error(error)
 
    @api.onchange('discount_amount', 'discount', 'price_unit')
    def _check_discount_amount(self):
        """Checks if discount_amount field isn't bigger than the price_unit (with discount percent applied) and raises an error otherwise."""
        for record in self:
            discount_value = record['discount']
            discount_amount_value = record['discount_amount']
            price_unit_value = record['price_unit']
            
            price_unit_processed = price_unit_value
            
            if discount_value:
                price_unit_processed = price_unit_value * (1 - (discount_value / 100))
            
            if discount_amount_value and price_unit_processed:
                error = ''
        
                if (discount_amount_value < 0.0):
                    error = _("A discount in amount cannot be negative !")
                elif (discount_amount_value > price_unit_processed and discount_amount_value > 0):
                    error = _("A discount in amount cannot be bigger than the price !")
                if error:
                    self._display_error(error)
    
    def _display_error(self, message):
        """Displays a user error with the given message."""
        raise UserError(message)

    # Overriding method to add the discount_amount inside the @api.onchange
    @api.onchange('quantity', 'discount', 'discount_amount', 'price_unit', 'tax_ids')
    def _onchange_price_subtotal(self):
        super(account_move_line, self)._onchange_price_subtotal()
        
    # Copy of the original method located in account module to add the discount_amount in the method parameters and the _get_price_total_and_subtotal_model call 
    def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None, partner=None, taxes=None, move_type=None, discount_amount=None):
        self.ensure_one()
        return self._get_price_total_and_subtotal_model(
            price_unit=price_unit or self.price_unit,
            quantity=quantity or self.quantity,
            discount=discount or self.discount,
            currency=currency or self.currency_id,
            product=product or self.product_id,
            partner=partner or self.partner_id,
            taxes=taxes or self.tax_ids,
            move_type=move_type or self.move_id.type,
            discount_amount=discount_amount or self.discount_amount, ### PSI modification here
        )
    
    # Copy of the original method located in account module to add the discount_amount in the method parameters and
    # to add it in the price computation.
    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type, discount_amount=None):
        ''' This method is used to compute 'price_total' & 'price_subtotal'.

        :param price_unit:  The current price unit.
        :param quantity:    The current quantity.
        :param discount:    The current discount.
        :param currency:    The line's currency.
        :param product:     The line's product.
        :param partner:     The line's partner.
        :param taxes:       The applied taxes.
        :param move_type:   The type of the move.
        :return:            A dictionary containing 'price_subtotal' & 'price_total'.
        '''
        res = {}

        
        ### PSI modification : also subtracting the discount amount to the price unit
        price_unit_wo_discount = 0
        
        if not discount_amount:
            discount_amount = self['discount_amount']
            
        if discount_amount:
            price_unit_wo_discount = (price_unit * quantity) - discount_amount
            
        ### End of PSI modification
        
        # Compute 'price_subtotal'.
        price_unit_wo_discount -= price_unit_wo_discount * (1 - (discount / 100.0))
            
        subtotal = price_unit_wo_discount

        # Compute 'price_total'.
        if taxes:
            factor = None
            if self.move_id and self.move_id.rounding_on_subtotal:
                factor = self.move_id.rounding_on_subtotal
            
            taxes_res = taxes._origin.compute_all(price_unit_wo_discount,
                quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'), prisme_rounding=factor)
            res['price_subtotal'] = self._prisme_round_amount(taxes_res['total_excluded']) ### PSI modification : rounding price_subtotal
            res['price_total'] = self._prisme_round_amount(taxes_res['total_included']) ### PSI modification : rounding price_total
        else:
            res['price_total'] = res['price_subtotal'] = self._prisme_round_amount(subtotal) ### PSI modifiation : rounding subtotal
        #In case of multi currency, round before it's use for computing debit credit
        if currency:
            res = {k: currency.round(v) for k, v in res.items()}
        return res
    
    # Copy of the original method located in account module to add the discount_amount in the method parameters and the _get_fields_onchange_balance_model call
    def _get_fields_onchange_balance(self, quantity=None, discount=None, balance=None, move_type=None, currency=None, taxes=None, price_subtotal=None, discount_amount=None):
        self.ensure_one()
        return self._get_fields_onchange_balance_model(
            quantity=quantity or self.quantity,
            discount=discount or self.discount,
            balance=balance or self.balance,
            move_type=move_type or self.move_id.type,
            currency=currency or self.currency_id or self.move_id.currency_id,
            taxes=taxes or self.tax_ids,
            price_subtotal=price_subtotal or self.price_subtotal,
            discount_amount=discount_amount or self.discount_amount, ### PSI modification here
        )
    
    # Copy of the original method located in account module to add the discount_amount in the method parameters and
    # to add it in the price computation.
    @api.model
    def _get_fields_onchange_balance_model(self, quantity, discount, balance, move_type, currency, taxes, price_subtotal, discount_amount=None):
        
        if move_type in self.move_id.get_outbound_types():
            sign = 1
        elif move_type in self.move_id.get_inbound_types():
            sign = -1
        else:
            sign = 1
        balance *= sign
        
        # Avoid rounding issue when dealing with price included taxes. For example, when the price_unit is 2300.0 and
        # a 5.5% price included tax is applied on it, a balance of 2300.0 / 1.055 = 2180.094 ~ 2180.09 is computed.
        # However, when triggering the inverse, 2180.09 + (2180.09 * 0.055) = 2180.09 + 119.90 = 2299.99 is computed.
        # To avoid that, set the price_subtotal at the balance if the difference between them looks like a rounding
        # issue.
        if currency.is_zero(balance - price_subtotal):
            return {}

        taxes = taxes.flatten_taxes_hierarchy()
        if taxes and any(tax.price_include for tax in taxes):
            # Inverse taxes. E.g:
            #
            # Price Unit    | Taxes         | Originator Tax    |Price Subtotal     | Price Total
            # -----------------------------------------------------------------------------------
            # 110           | 10% incl, 5%  |                   | 100               | 115
            # 10            |               | 10% incl          | 10                | 10
            # 5             |               | 5%                | 5                 | 5
            #
            # When setting the balance to -200, the expected result is:
            #
            # Price Unit    | Taxes         | Originator Tax    |Price Subtotal     | Price Total
            # -----------------------------------------------------------------------------------
            # 220           | 10% incl, 5%  |                   | 200               | 230
            # 20            |               | 10% incl          | 20                | 20
            # 10            |               | 5%                | 10                | 10
            factor = None
            if self.move_id and self.move_id.rounding_on_subtotal:
                factor = self.move_id.rounding_on_subtotal
                
            taxes_res = taxes._origin.compute_all(balance, currency=currency, handle_price_include=False, prisme_rounding=factor)
            for tax_res in taxes_res['taxes']:
                tax = self.env['account.tax'].browse(tax_res['id'])
                if tax.price_include:
                    balance += self._prisme_round_amount(tax_res['amount']) ### PSI modification : rounding tax amount
        
        ### PSI modifications : subtracting the discount_amount to the balance and adding the discount_amount to the vals dictionary
        vals = {}
        
        if not discount_amount:
            discount_amount = self['discount_amount']
        
        if discount_amount:
            balance -= discount_amount * sign
            vals['discount_amount'] = discount_amount
        
        discount_factor = 1 - (discount / 100.0)
        if balance and discount_factor:
            # discount != 100%
            vals['quantity'] = quantity or 1.0
            vals['price_unit'] = balance / discount_factor / (quantity or 1.0)
            
        elif balance and not discount_factor:
            # discount == 100%
            vals['quantity'] = quantity or 1.0
            vals['discount'] = 0.0
            vals['price_unit'] = balance / (quantity or 1.0)
            
        elif not discount_factor:
            None ### Original function sets vals as empty here. We don't want that since the discount_amount is added to the vals dictionary but we need to keep the condition.
        else:
            # balance is 0, so unit price is 0 as well
            vals['price_unit'] = 0.0
        ### End of PSI modifications
        return vals
    
    # Copy of the original method located in account module to support the discount_amount
    def write(self, vals):
        # OVERRIDE
        def field_will_change(line, field_name):
            if field_name not in vals:
                return False
            field = line._fields[field_name]
            if field.type == 'many2one':
                return line[field_name].id != vals[field_name]
            if field.type in ('one2many', 'many2many'):
                current_ids = set(line[field_name].ids)
                after_write_ids = set(r['id'] for r in line.resolve_2many_commands(field_name, vals[field_name], fields=['id']))
                return current_ids != after_write_ids
            if field.type == 'monetary' and line[field.currency_field]:
                return not line[field.currency_field].is_zero(line[field_name] - vals[field_name])
            return line[field_name] != vals[field_name]

        ACCOUNTING_FIELDS = ('debit', 'credit', 'amount_currency')
        BUSINESS_FIELDS = ('price_unit', 'quantity', 'discount', 'discount_amount', 'tax_ids') ### PSI modification : added discount_amount here
        PROTECTED_FIELDS_TAX_LOCK_DATE = ['debit', 'credit', 'tax_line_id', 'tax_ids', 'tag_ids']
        PROTECTED_FIELDS_LOCK_DATE = PROTECTED_FIELDS_TAX_LOCK_DATE + ['account_id', 'journal_id', 'amount_currency', 'currency_id', 'partner_id']
        PROTECTED_FIELDS_RECONCILIATION = ('account_id', 'date', 'debit', 'credit', 'amount_currency', 'currency_id')

        account_to_write = self.env['account.account'].browse(vals['account_id']) if 'account_id' in vals else None

        # Check writing a deprecated account.
        if account_to_write and account_to_write.deprecated:
            raise UserError(_('You cannot use a deprecated account.'))

        # when making a reconciliation on an existing liquidity journal item, mark the payment as reconciled
        for line in self:
            if line.parent_state == 'posted':
                if line.move_id.restrict_mode_hash_table and set(vals).intersection(INTEGRITY_HASH_LINE_FIELDS):
                    raise UserError(_("You cannot edit the following fields due to restrict mode being activated on the journal: %s.") % ', '.join(INTEGRITY_HASH_LINE_FIELDS))
                if any(key in vals for key in ('tax_ids', 'tax_line_ids')):
                    raise UserError(_('You cannot modify the taxes related to a posted journal item, you should reset the journal entry to draft to do so.'))
            if 'statement_line_id' in vals and line.payment_id:
                # In case of an internal transfer, there are 2 liquidity move lines to match with a bank statement
                if all(line.statement_id for line in line.payment_id.move_line_ids.filtered(
                        lambda r: r.id != line.id and r.account_id.internal_type == 'liquidity')):
                    line.payment_id.state = 'reconciled'

            # Check the lock date.
            if any(self.env['account.move']._field_will_change(line, vals, field_name) for field_name in PROTECTED_FIELDS_LOCK_DATE):
                line.move_id._check_fiscalyear_lock_date()

            # Check the tax lock date.
            if any(self.env['account.move']._field_will_change(line, vals, field_name) for field_name in PROTECTED_FIELDS_TAX_LOCK_DATE):
                line._check_tax_lock_date()

            # Check the reconciliation.
            if any(self.env['account.move']._field_will_change(line, vals, field_name) for field_name in PROTECTED_FIELDS_RECONCILIATION):
                line._check_reconciliation()

            # Check switching receivable / payable accounts.
            if account_to_write:
                account_type = line.account_id.user_type_id.type
                if line.move_id.is_sale_document(include_receipts=True):
                    if (account_type == 'receivable' and account_to_write.user_type_id.type != account_type) \
                            or (account_type != 'receivable' and account_to_write.user_type_id.type == 'receivable'):
                        raise UserError(_("You can only set an account having the receivable type on payment terms lines for customer invoice."))
                if line.move_id.is_purchase_document(include_receipts=True):
                    if (account_type == 'payable' and account_to_write.user_type_id.type != account_type) \
                            or (account_type != 'payable' and account_to_write.user_type_id.type == 'payable'):
                        raise UserError(_("You can only set an account having the payable type on payment terms lines for vendor bill."))

        result = True
        for line in self:
            cleaned_vals = line.move_id._cleanup_write_orm_values(line, vals)
            if not cleaned_vals:
                continue

            result |= super(account_move_line, line).write(cleaned_vals)

            if not line.move_id.is_invoice(include_receipts=True):
                continue

            # Ensure consistency between accounting & business fields.
            # As we can't express such synchronization as computed fields without cycling, we need to do it both
            # in onchange and in create/write. So, if something changed in accounting [resp. business] fields,
            # business [resp. accounting] fields are recomputed.
            if any(field in cleaned_vals for field in ACCOUNTING_FIELDS):
                balance = line.currency_id and line.amount_currency or line.debit - line.credit
                price_subtotal = line._get_price_total_and_subtotal().get('price_subtotal', 0.0)
                to_write = line._get_fields_onchange_balance(
                    balance=balance,
                    price_subtotal=price_subtotal,
                )
                to_write.update(line._get_price_total_and_subtotal(
                    price_unit=to_write.get('price_unit', line.price_unit),
                    quantity=to_write.get('quantity', line.quantity),
                    discount=to_write.get('discount', line.discount),
                    discount_amount=to_write.get('discount_amount', line.discount_amount), ### PSI modification : added discount_amount here
                ))
                result |= super(account_move_line, line).write(to_write)
            elif any(field in cleaned_vals for field in BUSINESS_FIELDS):
                to_write = line._get_price_total_and_subtotal()
                to_write.update(line._get_fields_onchange_subtotal(
                    price_subtotal=to_write['price_subtotal'],
                ))
                result |= super(account_move_line, line).write(to_write)

        # Check total_debit == total_credit in the related moves.
        if self._context.get('check_move_validity', True):
            self.mapped('move_id')._check_balanced()

        return result
    
    # Copy of the original method located in account module to support the discount_amount
    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        ACCOUNTING_FIELDS = ('debit', 'credit', 'amount_currency')
        BUSINESS_FIELDS = ('price_unit', 'quantity', 'discount', 'discount_amount', 'tax_ids') ### PSI modification : added discount_amount here

        for vals in vals_list:
            move = self.env['account.move'].browse(vals['move_id'])
            vals.setdefault('company_currency_id', move.company_id.currency_id.id) # important to bypass the ORM limitation where monetary fields are not rounded; more info in the commit message

            if move.is_invoice(include_receipts=True):
                currency = move.currency_id
                partner = self.env['res.partner'].browse(vals.get('partner_id'))
                taxes = self.resolve_2many_commands('tax_ids', vals.get('tax_ids', []), fields=['id'])
                tax_ids = set(tax['id'] for tax in taxes)
                taxes = self.env['account.tax'].browse(tax_ids)

                # Ensure consistency between accounting & business fields.
                # As we can't express such synchronization as computed fields without cycling, we need to do it both
                # in onchange and in create/write. So, if something changed in accounting [resp. business] fields,
                # business [resp. accounting] fields are recomputed.
                if any(vals.get(field) for field in ACCOUNTING_FIELDS):
                    if vals.get('currency_id'):
                        balance = vals.get('amount_currency', 0.0)
                    else:
                        balance = vals.get('debit', 0.0) - vals.get('credit', 0.0)
                    price_subtotal = self._get_price_total_and_subtotal_model(
                        vals.get('price_unit', 0.0),
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        currency,
                        self.env['product.product'].browse(vals.get('product_id')),
                        partner,
                        taxes,
                        move.type,
                        vals.get('discount_amount', 0.0), ### PSI modification : added discount_amount here
                    ).get('price_subtotal', 0.0)
                    vals.update(self._get_fields_onchange_balance_model(
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        balance,
                        move.type,
                        currency,
                        taxes,
                        price_subtotal,
                        vals.get('discount_amount', 0.0), ### PSI modification : added discount_amount here
                    ))
                    vals.update(self._get_price_total_and_subtotal_model(
                        vals.get('price_unit', 0.0),
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        currency,
                        self.env['product.product'].browse(vals.get('product_id')),
                        partner,
                        taxes,
                        move.type,
                        vals.get('discount_amount', 0.0), ### PSI modification : added discount_amount here
                    ))
                elif any(vals.get(field) for field in BUSINESS_FIELDS):
                    vals.update(self._get_price_total_and_subtotal_model(
                        vals.get('price_unit', 0.0),
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        currency,
                        self.env['product.product'].browse(vals.get('product_id')),
                        partner,
                        taxes,
                        move.type,
                        vals.get('discount_amount', 0.0), ### PSI modification : added discount_amount here
                    ))
                    vals.update(self._get_fields_onchange_subtotal_model(
                        vals['price_subtotal'],
                        move.type,
                        currency,
                        move.company_id,
                        move.date,
                    ))

            # Ensure consistency between taxes & tax exigibility fields.
            if 'tax_exigible' in vals:
                continue
            if vals.get('tax_repartition_line_id'):
                repartition_line = self.env['account.tax.repartition.line'].browse(vals['tax_repartition_line_id'])
                tax = repartition_line.invoice_tax_id or repartition_line.refund_tax_id
                vals['tax_exigible'] = tax.tax_exigibility == 'on_invoice'
            elif vals.get('tax_ids'):
                tax_ids = [v['id'] for v in self.resolve_2many_commands('tax_ids', vals['tax_ids'], fields=['id'])]
                taxes = self.env['account.tax'].browse(tax_ids).flatten_taxes_hierarchy()
                vals['tax_exigible'] = not any(tax.tax_exigibility == 'on_payment' for tax in taxes)
                
        lines = super(account_move_line, self).create(vals_list)
        
        ### PSI modifications : 
        for line in lines:
            real_price_unit = 0.0
            
            # Price unit is always computed 0.01 or 0.02 CHF bigger or smaller than the SO price unit, even though the taxes are correctly computed with the difference
            # So we get the SO price unit passed in res
            if line.origin_price_unit:
                real_price_unit = line.origin_price_unit
                            
            # The price unit is recomputed from subtotal, tax and discount when the line is saved, but the discount_amount is never taken into account
            # That means the price unit saved will always be the price unit subtracted by the discount_amount but it shouldn't be.
            # The fix here is to add the discount_amount to the price unit once the lines are saved. This is a workaround but there should be a better solution. 
            elif line.discount_amount:
                real_price_unit = line.price_unit + line.discount_amount
            
            if real_price_unit:
                line.write({'price_unit' : real_price_unit})
        ## End of PSI modifications

        moves = lines.mapped('move_id')
        if self._context.get('check_move_validity', True):
            moves._check_balanced()
        moves._check_fiscalyear_lock_date()
        lines._check_tax_lock_date()

        return lines
    
    def _prisme_round_amount(self, amount):
        new_amount = amount
        if self.move_id and self.move_id.rounding_on_subtotal:
            factor = self.move_id.rounding_on_subtotal
            new_amount = round(amount / factor) * factor
        
        return new_amount