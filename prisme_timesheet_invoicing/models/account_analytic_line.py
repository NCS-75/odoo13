import itertools
import time
from datetime import datetime
from odoo import models, fields, api, _
from openerp.tools.translate import _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import logging
_logger = logging.getLogger(__name__)

class prisme_account_analytic_line(models.Model):
    _inherit = 'account.analytic.line'
    _order = "date ASC, time_beginning ASC"

    invoice_id = fields.Many2one('account.move', 'Invoice', ondelete="set null", copy=False)
    to_invoice = fields.Many2one('hr_timesheet_invoice.factor', 'Invoiceable', help="It allows to set the discount while making invoice, keep empty if the activities should not be invoiced.")
    
    account_partner = fields.Many2one(related='account_id.partner_id', relation='res.partner', string='Partner Id', store=True)
    
    def invoice_cost_create(self, dados, data=None):
        invoice_obj = self.env['account.move']
        invoice_line_obj = self.env['account.move.line']
        analytic_line_obj = self.env['account.analytic.line']
        invoices = []
        if data is None:
            data = {}

        # use key (partner/account, company, currency)
        # creates one invoice per key
        invoice_grouping = {}

        currency_id = False

        # prepare for iteration on journal and accounts
        for line in self.browse(dados):

            key = (line.account_id.id,
                   line.account_id.company_id.id,
                   line.account_id.pricelist_id.currency_id.id)
            invoice_grouping.setdefault(key, []).append(line)

        for (key_id, company_id, currency_id), analytic_lines in invoice_grouping.items():
            # key_id is an account.analytic.account
            account = analytic_lines[0].account_id
            partner = account.partner_id.id  # will be the same for every line

            if (not partner) or not (currency_id):
                raise ValidationError(_('Contract incomplete. Please fill in the Customer and Pricelist fields for %s.') % (account.name))
                # raise osv.except_osv(_('Error!'), _('Contract incomplete. Please fill in the Customer and Pricelist fields for %s.') % (account.name))

            curr_invoice = self._prepare_cost_invoice(partner, company_id, currency_id, analytic_lines)
            partner= self.env['res.partner'].browse(partner)
            invoice_context = dict(self._context,
                                   lang=partner.lang,
                                   force_company=company_id,  # set force_company in context so the correct product properties are selected (eg. income account)
                                   company_id=company_id)  # set company_id in context, so the correct default journal will be selected
            last_invoice = invoice_obj.create(curr_invoice)

            invoices.append(last_invoice.id)

            # use key (product, uom, user, invoiceable, analytic account, journal type)
            # creates one invoice line per key
            invoice_lines_grouping = {}
            for analytic_line in analytic_lines:
                account = analytic_line.account_id

                if not analytic_line.to_invoice:
                    raise ValidationError(_('Trying to invoice non invoiceable line for %s.') % (analytic_line.product_id.name))
                    # raise osv.except_osv(_('Error!'), _('Trying to invoice non invoiceable line for %s.') % (analytic_line.product_id.name))

                key = (analytic_line.product_id.id,
                       analytic_line.product_uom_id.id,
                       analytic_line.user_id.id,
                       analytic_line.to_invoice,
                       analytic_line.account_id)
                    #    analytic_line.journal_id.type)
                # We want to retrieve the data in the partner language for the invoice creation
                analytic_line = analytic_line_obj.browse([line.id for line in analytic_line])
                invoice_lines_grouping.setdefault(key, []).append(analytic_line)

            # finally creates the invoice line
            for (product_id, uom, user_id, factor_id, account), lines_to_invoice in invoice_lines_grouping.items():
                if product_id:
                    if uom:
                        curr_invoice_line = self._prepare_cost_invoice_line(last_invoice.id,
                            product_id, uom, user_id, factor_id, account, lines_to_invoice, data)

                        invoice_line_obj.create(curr_invoice_line)
                    else:
                        raise ValidationError(_("Please define Unit of Measure!"))
                        # raise osv.except_osv(_('Warning!'), _("Please define Unit of Measure!"))
                else:
                    raise ValidationError(_("Please define a product!"))
                    # raise osv.except_osv(_('Warning!'), _("Please define a product!"))

            for l in analytic_lines:
                # l.write({'invoice_id': last_invoice.id})

                l.invoice_id = last_invoice

                last_invoice.compute_taxes()                
            # invoice_obj.button_reset_taxes(cr, uid, [last_invoice], context)
        return invoices
    

    def _prepare_cost_invoice_line(self, invoice_id, product_id, uom, user_id, factor_id, account, analytic_lines, data):

        product_obj = self.env['product.product']
        uom_context = dict(self._context or {}, uom=uom)

        total_price = sum(l.amount for l in analytic_lines)
        total_qty = sum(l.unit_amount for l in analytic_lines)

        if product_id:
            for obj_product in self.env['product.product'].browse(product_id):
                if account.pricelist_id:
                    pl = account.pricelist_id.id
                    prices = account.pricelist_id.price_get(product_id, total_qty or 1.0, account.partner_id.id)
                    price = prices[account.pricelist_id.id]             
                elif analytic_lines[0].partner_id.property_product_pricelist:
                    pl = analytic_lines[0].partner_id.property_product_pricelist
                    prices = pl.price_get(product_id, 1, analytic_lines[0].partner_id)
                    price = prices[pl.id]
                else:
                    price= obj_product.lst_price
                name= obj_product.name
            unit_price = price
            name = name
        else:
            # expenses, using price from amount field
            unit_price = total_price*-1.0 / total_qty
             
        curr_invoice_line = {
            'price_unit': unit_price,
            'quantity': total_qty,
            'product_id': product_id,
            'discount': factor_id.factor,
            'invoice_id': invoice_id,
            'note': '',
            'name': name,
            'uom_id': uom,
            'account_analytic_id': account.id,
        }

        if product_id:
            product = product_obj.browse(product_id)
            if product.default_code:
                factor_name = "[" + product.default_code + "] "
            factor_name += product.name
            if factor_id.customer_name:
                factor_name += ' - ' + factor_id.customer_name
            if user_id:
                res_user_obj = self.env['res.users']
                factor_name += " - " + res_user_obj.browse(user_id).name
            general_account = product.property_account_income_id or product.categ_id.property_account_income_categ_id
            if not general_account:
                raise ValidationError(_("Please define income account for product '%s'.") % product.name)
                # raise osv.except_osv(_('Error!'), _("Configuration Error!") + '\n' + _("Please define income account for product '%s'.") % product.name)
            taxes = product.taxes_id or general_account.tax_ids or False
            
            invoice_id = self.env['account.move'].browse(invoice_id)
            if not taxes:
                taxes = []
            fp_taxes = invoice_id.fiscal_position_id.map_tax(taxes, product, invoice_id.partner_id).ids
            curr_invoice_line.update({
                'invoice_line_tax_ids': [(6, 0, fp_taxes)],
                'name': factor_name,
                # 'invoice_line_tax_ids': [(6, 0, tax)],
                'account_id': general_account.id,
            })

            note = []
            # start prisme modification
            alreadyadded=False
            for line in analytic_lines:
                # Get user
                cr = self.env.cr
                cr.execute("select p.name from res_partner p, res_users u where p.id=u.partner_id and u.id="+str(user_id))
                usr=cr.fetchall()
                # set invoice_line_note
                details = []
                if not(alreadyadded):
                    details.append("- "+usr[0][0])
                alreadyadded=True
            # end prisme modification
                if data.get('date', False):
                    details.append(line['date'])
                if data.get('time', False):
                    if line['product_uom_id']:
                        details.append("%s %s" % (line.unit_amount, line.product_uom_id.name))
                    else:
                        details.append("%s" % (line['unit_amount'], ))
                if data.get('name', False):
                    details.append(line['name'])
                if details:
                    note.append(u' - '.join(map(lambda x: unicode(x) or '', details)))

            if note:
                self._cr.execute("SELECT column_name FROM information_schema.columns WHERE table_name='account_invoice_line' and column_name='note'")
                field= self._cr.fetchone()
                if field!=None and field[0]!=None:
                    curr_invoice_line['note'] += "\n" + ("\n".join(map(lambda x: unicode(x) or '', note)))
                else:
                    curr_invoice_line['name'] += "\n" + ("\n".join(map(lambda x: unicode(x) or '', note)))
        return curr_invoice_line
    
    def _prepare_cost_invoice(self, partner, company_id, currency_id, analytic_lines):
        """ returns values used to create main invoice from analytic lines"""
        account_payment_term_obj = self.env['account.payment.term']
        invoice_name = analytic_lines[0].account_id.name
        project_id = analytic_lines[0].account_id.id
        
        partner= self.env['res.partner'].browse(partner)
        date_due = False
        if partner.property_payment_term_id:
            pterm_list = account_payment_term_obj.with_context(currency_id=currency_id).compute(value=1, date_ref=time.strftime('%Y-%m-%d'))
            if pterm_list:
                # pterm_list = [line[0] for line in pterm_list
                # pterm_list.sort()
                # date_due = pterm_list[-1]
                date_due = max(line[0] for line in pterm_list[0])
        return {
            'name': "%s - %s" % (time.strftime('%d/%m/%Y'), invoice_name),
            'partner_id': partner.id,
            'company_id': company_id,
            'payment_term_id': partner.property_payment_term_id.id or False,
            'account_id': partner.property_account_receivable_id.id,
            'currency_id': currency_id,
            # 'date_due': date_due,
            'fiscal_position_id': partner.property_account_position_id.id,
            'project_id':project_id
        }
    
    @api.multi
    def write(self, vals):
        for record in self:
            self._check_sheet(record, vals)
        return self._write(vals)
            
    #Check the timesheet, to allow the "Task", "Internal description" and "Reference" field to be modified anytime.
    #Also prevents modification of a timesheet if it has been invoiced.
    def _check_sheet(self, record, vals):
        #If the timesheet is confirmed
        if record.sheet_id and record.sheet_id.state not in ('draft', 'new'):
            #If only the "Task" field and/or the "Internal description" field and/or the "Reference" field are being modified, do nothing
            if (vals.has_key('task_id') and vals.has_key('internal_description') and vals.has_key('ref')) and len(vals.keys())==3:
                return
            elif ((vals.has_key('task_id') and vals.has_key('internal_description')) or (vals.has_key('task_id') and vals.has_key('ref')) or (vals.has_key('ref') and vals.has_key('internal_description'))) and len(vals.keys())==2:
                return
            elif (vals.has_key('task_id') or vals.has_key('internal_description') or vals.has_key('ref')) and len(vals.keys())==1:
                return
            #Otherwise raise the error here
            raise UserError(_('You cannot modify an entry in a confirmed timesheet.'))
        else:
            if record.invoice_id:
                #Else check if timesheet has already been invoiced
                ###If only the "Task" field and/or the "Internal description" field and/or the "Reference" field are being modified, do nothing
                ###Else show an error
                if ( not vals.has_key('invoice_id')):
                    if (vals.has_key('task_id') and vals.has_key('internal_description') and vals.has_key('ref')) and len(vals.keys())==3:
                        return
                    elif ((vals.has_key('task_id') and vals.has_key('internal_description')) or (vals.has_key('task_id') and vals.has_key('ref')) or (vals.has_key('ref') and vals.has_key('internal_description'))) and len(vals.keys())==2:
                        return
                    elif (vals.has_key('task_id') or vals.has_key('internal_description') or vals.has_key('ref')) and len(vals.keys())==1:
                        return
                    else:
                        raise ValidationError(_('You cannot modify an invoiced analytic line!'))
                elif vals['invoice_id' ] == False:
                    if (vals.has_key('task_id') and vals.has_key('internal_description') and vals.has_key('ref')) and len(vals.keys())==4:
                        return
                    elif ((vals.has_key('task_id') and vals.has_key('internal_description')) or (vals.has_key('task_id') and vals.has_key('ref')) or (vals.has_key('ref') and vals.has_key('internal_description'))) and len(vals.keys())==3:
                        return
                    elif (vals.has_key('task_id') or vals.has_key('internal_description') or vals.has_key('ref')) and len(vals.keys())==2:
                        return
                    else:
                        raise ValidationError(_('You cannot modify an invoiced analytic line!'))
            return True
    
    
    
    

