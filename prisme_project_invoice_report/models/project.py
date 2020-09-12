# -*- coding: utf-8 -*-
#######################################
# Prisme Solutions Informatique SA    #
#######################################
# Author: Hugo Buchs                  #
# Email:  hugo.buchs@prisme.ch        #
# Web:    www.prisme.ch               #
# Date:   14.09.2019                  #
#######################################
from odoo import models, fields, api
from operator import itemgetter
from datetime import datetime
#Import logger
import logging
#Get the logger
_logger = logging.getLogger(__name__)

#New wizard model added to select options
class prisme_project_print_financial_view_wizard(models.TransientModel):
    _name = "wizard.project.print.financial.view"
    
    #Field used to chose if the non-invoiced timesheets must be displayed
    print_lines_not_invoiced = fields.Boolean(string='Print lines not invoiced')
    #Field used to specify the maximum date for non-invoiced timesheets
    print_lines_not_invoiced_up_to = fields.Date(string='Print lines not invoiced up to')
    #Field used to chose if invoice lines must be grouped by financial account
    group_by_financial_account = fields.Boolean(string='Group by financial account')

    #Called when the "Print financial view button is clicked on the project"
    def print_financial_view(self):
        project_id = self.env['project.project'].browse(self.env.context.get('record_id'))
        return project_id.print_project_financial_view(self.print_lines_not_invoiced, self.print_lines_not_invoiced_up_to, self.group_by_financial_account)

#The project model is modified to allow to print the report
class prisme_project_print_financial_view(models.Model):
    _inherit = "project.project"

    #Field used to chose if the non-invoiced timesheets must be displayed
    #It is not displayed but is needed to pass the value to the report
    print_lines_not_invoiced = fields.Boolean()
    #Same but for specifying the maximum date for non-invoiced timesheet
    print_lines_not_invoiced_up_to = fields.Date(string='Print lines not invoiced up to')
    #Same but for choosing if invoice lines must be grouped by financial account
    group_by_financial_account = fields.Boolean()
    
    #Called from the wizard to print the report
    def print_project_financial_view(self, print_lines_not_invoiced, print_lines_not_invoiced_up_to, group_by_financial_account):
        #Save the value from the wizard
        self.write({'print_lines_not_invoiced': print_lines_not_invoiced, 'print_lines_not_invoiced_up_to': print_lines_not_invoiced_up_to, 'group_by_financial_account':group_by_financial_account})
        #Print the report, cheap hack so that the wizard closes after printing finished, also gives a better rendering
        return self.env.ref('prisme_project_invoice_report.report_project_invoice').report_action(self)

#A new model is created to handle the invoice report printing
class prisme_project_financial_view_report(models.AbstractModel):
    _name = 'report.prisme_project_invoice_report.template_project_invoice'
    #Called in self.env['report'].get_action
    @api.model
    def _get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('prisme_project_invoice_report.template_project_invoice')
        #This is the project
        docs = self.env[report.model].browse(docids)
        #Setup render informations
        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': docs,
        }
        
        #Following code is to get the necessary data to print the report
        
        #Represent the tasks that will be printed
        tasks = []
        #Total project advances
        total_project = 0.0
        #Total project balance
        balance_project = 0.0
        #Project start date
        start_date = datetime.max
        #Project end date
        end_date = datetime.min
        #Hack to allow printing report for archived projects
        if docs.active == True:
            project_tasks = docs.tasks
        else:
            project_tasks = self.env['project.task'].search([['project_id','=',docs.id],['active','=',False]])
        #Maximum date
        if docs.print_lines_not_invoiced_up_to:
            date_report = docs.print_lines_not_invoiced_up_to
        else:
            date_report = datetime.today()
        if not docs.group_by_financial_account:
            #Loop over tasks
            for task in project_tasks:
                invoice_lines_final = []
                invoice_lines_done = {}
                #Task balance
                balance = task.ammount+task.balance_previous_command
                #Task total used money
                use = task.balance_previous_command
                #Add to total project advance
                total_project += balance
                #If this is a "Prestations" task
                if ((not (task.name.lower().find(u'hébergement') >= 0)) and (not (task.name.lower().find(u'déplacement') >= 0))):
                    #Get all invoice lines linked to the timesheets in the tasks
                    for timesheet in task.timesheet_ids:
                        if (timesheet.to_invoice.code != "G"):
                            for invoice_line in timesheet.invoice_id.invoice_line_ids:
                                if (invoice_line.account_analytic_id == timesheet.account_id) and (invoice_line.product_id == timesheet.product_id) and (invoice_line.account_id == task.account_id):
                                    if invoice_line in invoice_lines_done:
                                        invoice_lines_done[invoice_line][1].append(timesheet.id)
                                    else:
                                        #Invoicing type for the timesheet is saved
                                        invoice_lines_done[invoice_line] = [timesheet.to_invoice, [timesheet.id]]
                                    break
                    #Loop over invoice lines sorted by date
                    for invoice_line in sorted(invoice_lines_done.keys(), key=lambda r: datetime.strptime(r.invoice_id.date_invoice, "%Y-%m-%d")):                    
                        #Invoice line start date
                        invoice_line_date_min = None
                        #Invoice line end date
                        invoice_line_date_max = None
                        quantity = 0
                        #Compute start and end date by checking latest and earliest date in timesheets linking to the invoice line
                        for timesheet_id in invoice_lines_done[invoice_line][1]:
                            timesheet = self.env['account.analytic.line'].browse(timesheet_id)
                            quantity += abs(timesheet.unit_amount)
                            timesheet_date = datetime.strptime(timesheet.date, "%Y-%m-%d")
                            if invoice_line_date_min is not None:
                                if timesheet_date < invoice_line_date_min:
                                    invoice_line_date_min = timesheet_date
                            else:
                                invoice_line_date_min = timesheet_date
                            if invoice_line_date_max is not None:
                                if timesheet_date > invoice_line_date_max:
                                    invoice_line_date_max = timesheet_date
                            else:
                                invoice_line_date_max = timesheet_date
                        #Compute price depending on invoicing type
                        if invoice_lines_done[invoice_line][0].code == "F":
                            price = (quantity)*invoice_line.price_unit
                        else:
                            if quantity <= invoice_line.quantity:
                                price = invoice_line.price_subtotal/invoice_line.quantity*quantity
                            else:
                                price = invoice_line.price_subtotal
                            
                        #Compute balance and use
                        balance -= price
                        use -= price
    
                        #If the invoice line has a default code, this means that the name is the employee name and the default code is the designation
                        if invoice_line.product_id.default_code:
                            designation = invoice_line.product_id.default_code
                            employee = invoice_line.product_id.name
                        #Otherwise the name is the real designation
                        else:
                            designation = invoice_line.product_id.name
                            employee = ''
                        #Recompute start and end date using the minimum and maximum dates of the invoice line
                        if invoice_line_date_max > end_date:
                            end_date = invoice_line_date_max
                        if invoice_line_date_min < start_date:
                            start_date = invoice_line_date_min
                        #Format the final date for the invoice line
                        if invoice_line_date_min == invoice_line_date_max:
                            invoice_line_date = invoice_line_date_min.strftime("%d.%m.%Y")
                        elif invoice_line_date_min.strftime("%m") == invoice_line_date_max.strftime("%m"):
                            invoice_line_date = invoice_line_date_min.strftime("%d")+"-"+invoice_line_date_max.strftime("%d.%m.%Y")
                        else:
                            invoice_line_date = invoice_line_date_min.strftime("%d.%m")+"-"+invoice_line_date_max.strftime("%d.%m.%Y")
                        #Add the invoice lines to the data
                        invoice_lines_final.append({'invoice':'FA'+str(invoice_line.invoice_id.number),
                                                    'date':invoice_line_date,
                                                    'designation':designation,
                                                    'quantity':quantity,
                                                    'rate':invoice_line.price_unit,
                                                    'advance':-price,
                                                    'employee':employee
                        })
                    #This part is to print timesheet lines that are not invoiced
                    if docs.print_lines_not_invoiced:
                        #Add lines without invoices
                        timesheet_lines_articles_not_invoiced = []
                        #First timesheets are aggregated by product
                        for timesheet in task.timesheet_ids:
                            if not timesheet.invoice_id:
                                if timesheet.product_id.id not in timesheet_lines_articles_not_invoiced:
                                        timesheet_lines_articles_not_invoiced.append(timesheet.product_id.id)
                        #Then a line is outputted for each product
                        for product_id in timesheet_lines_articles_not_invoiced:
                                quantity = 0
                                #If the product has a default code, this means that the name is the employee name and the default code is the designation
                                product = self.env['product.product'].browse(product_id)
                                if product.default_code:
                                    designation = product.default_code
                                    employee = product.name
                                #Otherwise the name is the real designation
                                else:
                                    designation = product.name
                                    employee = ''
                                #Invoice line start date
                                invoice_line_date_min = None
                                #Invoice line end date
                                invoice_line_date_max = None
                                #Valid timesheet count
                                valid_timesheet_count = 0
                                #Start and end dates and quantity are computed using the timesheets
                                for timesheet in task.timesheet_ids:
                                    if not timesheet.invoice_id:
                                        if timesheet.product_id.id == product_id:
                                            #Do not take in account the free lines and timesheets later than specified in wizard
                                            if (timesheet.to_invoice.code == "G") or (timesheet.date > docs.print_lines_not_invoiced_up_to):
                                                continue
                                            else:
                                                #Add this timesheet to the valid ones
                                                valid_timesheet_count+=1
                                            #Sum the quantity
                                            quantity += abs(timesheet.unit_amount)
                                            #Compute start and end date by checking latest and earliest date
                                            timesheet_date = timesheet.date
                                            if invoice_line_date_min is not None:
                                                if timesheet_date < invoice_line_date_min:
                                                    invoice_line_date_min = timesheet_date
                                            else:
                                                invoice_line_date_min = timesheet_date
                                            if invoice_line_date_max is not None:
                                                if timesheet_date > invoice_line_date_max:
                                                    invoice_line_date_max = timesheet_date
                                            else:
                                                invoice_line_date_max = timesheet_date
                                #If no valid timesheets for this product, skip
                                if valid_timesheet_count == 0:
                                    continue
                                #Compute price depending on invoicing type
                                pl = docs.analytic_account_id.pricelist_id
                                price = pl.price_get(product_id, quantity, partner=docs.analytic_account_id.partner_id)#[pl.id]   
                                #Compute advance
                                advance = price*quantity
                                #Compute balance and use
                                balance -= advance
                                use -= advance
                                #Compute start and end dates for the task
                                if invoice_line_date_max > end_date:
                                    end_date = invoice_line_date_max
                                if invoice_line_date_min < start_date:
                                    start_date = invoice_line_date_min
                                #Formatting the start and end dates
                                if invoice_line_date_min == invoice_line_date_max:
                                    invoice_line_date = invoice_line_date_min.strftime("%d.%m.%Y")
                                elif invoice_line_date_min.strftime("%m") == invoice_line_date_max.strftime("%m"):
                                    invoice_line_date = invoice_line_date_min.strftime("%d")+"-"+invoice_line_date_max.strftime("%d.%m.%Y")
                                else:
                                    invoice_line_date = invoice_line_date_min.strftime("%d.%m")+"-"+invoice_line_date_max.strftime("%d.%m.%Y")         
                                #Add the line to report
                                invoice_lines_final.append({'invoice':'',
                                                            'date':invoice_line_date,
                                                            'designation':designation,
                                                            'quantity':quantity,
                                                            'rate':price,
                                                            'advance':-advance,
                                                            'employee':employee
                                })
                
                #If the task is a standard one
                else:
                    #Loop over the invoices for the project ordered by invoice date
                    invoices = self.env['account.invoice'].search([['project_id.id', '=', docs.analytic_account_id.id]])
                    for invoice in sorted(invoices, key=lambda r: datetime.strptime(r.date_invoice, "%Y-%m-%d")):
                        #Loop over the invoice lines
                        for invoice_line in invoice.invoice_line_ids:
                            #If the invoice line is part of the task
                            if invoice_line.account_id == task.account_id:
                                #Compute date
                                date = datetime.strptime(invoice.date_invoice, "%Y-%m-%d")
                                if date > end_date:
                                    end_date = date
                                if date < start_date:
                                    start_date = date
                                date = date.strftime("%d.%m.%Y")
                                #Compute price, using the invoicing type
                                if docs.analytic_account_id.to_invoice.code == "F":
                                    price = invoice_line.quantity*invoice_line.price_unit                        
                                else:
                                    price = invoice_line.price_subtotal
                                #Compute balance and use
                                balance -= price
                                use -= price
                                #Add the invoice lines to the data
                                invoice_lines_final.append({'invoice':'FA'+str(invoice_line.invoice_id.number),
                                                            'date':date,
                                                            'designation':invoice_line.product_id.name,
                                                            'quantity':invoice_line.quantity,
                                                            'rate':invoice_line.price_unit,
                                                            'advance':-price,
                                                            'employee':''
                                })
                balance_project += balance
                #Add the task to the data
                tasks.append({'designation':task.name,
                             'advance':task.ammount,
                             'balance_previous_command':task.balance_previous_command,
                             'invoice_lines':invoice_lines_final,
                              'balance':balance,
                              'use':use
                })
        else:
            task_groups = {}
            for task in project_tasks:
                financial_account = (str(task.account_id.code) + " " + task.account_id.name)
                if financial_account in task_groups:
                    task_groups[financial_account].append(task)
                else:
                    task_groups[financial_account] = [task]
            #Loop over tasks groups
            for financial_account in task_groups:
                amount = 0
                balance_previous_command = 0
                invoice_lines_final = []
                #Task balance
                balance = 0
                #Task total used money
                use = 0
        #Invoice lines done
                invoice_lines_done = {}
                for task in task_groups[financial_account]:
                    amount += task.ammount
                    balance_previous_command += task.balance_previous_command
                    #Task balance
                    balance += (task.ammount+task.balance_previous_command)
                    #Task total used money
                    use += (task.balance_previous_command)
                    #Add to total project advance
                    total_project += (task.ammount+task.balance_previous_command)
                    #If this is a "Prestations" task
                    if ((not (task.name.lower().find(u'hébergement') >= 0)) and (not (task.name.lower().find(u'déplacement') >= 0))):
                        #Get all invoice lines linked to the timesheets in the tasks
                        for timesheet in task.timesheet_ids:
                            if (timesheet.to_invoice.code != "G"):
                                for invoice_line in timesheet.invoice_id.invoice_line_ids:
                                    if (invoice_line.account_analytic_id == timesheet.account_id) and (invoice_line.product_id == timesheet.product_id) and (invoice_line.account_id == task.account_id):
                                        if invoice_line in invoice_lines_done:
                                            invoice_lines_done[invoice_line][1].append(timesheet.id)
                                        else:
                                            #Invoicing type for the timesheet is saved
                                            invoice_lines_done[invoice_line] = [timesheet.to_invoice, [timesheet.id]]
                                        break
                        #This part is to print timesheet lines that are not invoiced
                        if docs.print_lines_not_invoiced:
                            #Add lines without invoices
                            timesheet_lines_articles_not_invoiced = []
                            #First timesheets are aggregated by product
                            for timesheet in task.timesheet_ids:
                                if not timesheet.invoice_id:
                                    if timesheet.product_id.id not in timesheet_lines_articles_not_invoiced:
                                            timesheet_lines_articles_not_invoiced.append(timesheet.product_id.id)
                            #Then a line is outputted for each product
                            for product_id in timesheet_lines_articles_not_invoiced:
                                    quantity = 0
                                    #If the product has a default code, this means that the name is the employee name and the default code is the designation
                                    product = self.env['product.product'].browse(product_id)
                                    if product.default_code:
                                        designation = product.default_code
                                        employee = product.name
                                    #Otherwise the name is the real designation
                                    else:
                                        designation = product.name
                                        employee = ''
                                    #Invoice line start date
                                    invoice_line_date_min = None
                                    #Invoice line end date
                                    invoice_line_date_max = None
                                    #Valid timesheet count
                                    valid_timesheet_count = 0
                                    #Start and end dates and quantity are computed using the timesheets
                                    for timesheet in task.timesheet_ids:
                                        if not timesheet.invoice_id:
                                            if timesheet.product_id.id == product_id:
                                                #Do not take in account the free lines and timesheets later than specified in wizard
                                                if (timesheet.to_invoice.code == "G") or (datetime.strptime(timesheet.date, "%Y-%m-%d") > datetime.strptime(docs.print_lines_not_invoiced_up_to, "%Y-%m-%d")):
                                                    continue
                                                else:
                                                    #Add this timesheet to the valid ones
                                                    valid_timesheet_count+=1
                                                #Sum the quantity
                                                quantity += abs(timesheet.unit_amount)
                                                #Compute start and end date by checking latest and earliest date
                                                timesheet_date = datetime.strptime(timesheet.date, "%Y-%m-%d")
                                                if invoice_line_date_min is not None:
                                                    if timesheet_date < invoice_line_date_min:
                                                        invoice_line_date_min = timesheet_date
                                                else:
                                                    invoice_line_date_min = timesheet_date
                                                if invoice_line_date_max is not None:
                                                    if timesheet_date > invoice_line_date_max:
                                                        invoice_line_date_max = timesheet_date
                                                else:
                                                    invoice_line_date_max = timesheet_date
                                    #If no valid timesheets for this product, skip
                                    if valid_timesheet_count == 0:
                                        continue
                                    #Compute price depending on invoicing type
                                    pl = docs.analytic_account_id.pricelist_id
                                    price = pl.price_get(product_id, quantity, partner=docs.analytic_account_id.partner_id)[pl.id]   
                                    #Compute advance
                                    advance = price*quantity
                                    #Compute balance and use
                                    balance -= advance
                                    use -= advance
                                    #Compute start and end dates for the task
                                    if invoice_line_date_max > end_date:
                                        end_date = invoice_line_date_max
                                    if invoice_line_date_min < start_date:
                                        start_date = invoice_line_date_min
                                    #Formatting the start and end dates
                                    if invoice_line_date_min == invoice_line_date_max:
                                        invoice_line_date = invoice_line_date_min.strftime("%d.%m.%Y")
                                    elif invoice_line_date_min.strftime("%m") == invoice_line_date_max.strftime("%m"):
                                        invoice_line_date = invoice_line_date_min.strftime("%d")+"-"+invoice_line_date_max.strftime("%d.%m.%Y")
                                    else:
                                        invoice_line_date = invoice_line_date_min.strftime("%d.%m")+"-"+invoice_line_date_max.strftime("%d.%m.%Y")         
                                    #Add the line to report
                                    invoice_lines_final.append({'invoice':'',
                                                                'date':invoice_line_date,
                                                                'sort':invoice_line_date_min.strftime("%d.%m.%Y"),
                                                                'designation':designation,
                                                                'quantity':quantity,
                                                                'rate':price,
                                                                'advance':-advance,
                                                                'employee':employee
                                    })
                 
                    #If the task is a standard one
                    else:
                        #Loop over the invoices for the project ordered by invoice date
                        invoices = self.env['account.invoice'].search([['project_id.id', '=', docs.analytic_account_id.id]])
                        for invoice in sorted(invoices, key=lambda r: datetime.strptime(r.date_invoice, "%Y-%m-%d")):
                            #Loop over the invoice lines
                            for invoice_line in invoice.invoice_line_ids:
                                #If the invoice line is part of the task
                                if invoice_line.account_id == task.account_id:
                                    #Compute date
                                    date = datetime.strptime(invoice.date_invoice, "%Y-%m-%d")
                                    if date > end_date:
                                        end_date = date
                                    if date < start_date:
                                        start_date = date
                                    date = date.strftime("%d.%m.%Y")
                                    #Compute price, using the invoicing type
                                    if docs.analytic_account_id.to_invoice.code == "F":
                                        price = invoice_line.quantity*invoice_line.price_unit                        
                                    else:
                                        price = invoice_line.price_subtotal
                                    #Compute balance and use
                                    balance -= price
                                    use -= price
                                    #Add the invoice lines to the data
                                    invoice_lines_final.append({'invoice':'FA'+str(invoice_line.invoice_id.number),
                                                                'date':date,
                                                                'sort':date,
                                                                'designation':invoice_line.product_id.name,
                                                                'quantity':invoice_line.quantity,
                                                                'rate':invoice_line.price_unit,
                                                                'advance':-price,
                                                                'employee':''
                                    })

                #Loop over invoice lines sorted by date
                for invoice_line in sorted(invoice_lines_done.keys(), key=lambda r: datetime.strptime(r.invoice_id.date_invoice, "%Y-%m-%d")):                    
                            #Invoice line start date
                            invoice_line_date_min = None
                            #Invoice line end date
                            invoice_line_date_max = None
                            quantity = 0
                            #Compute start and end date by checking latest and earliest date in timesheets linking to the invoice line
                            for timesheet_id in invoice_lines_done[invoice_line][1]:
                                timesheet = self.env['account.analytic.line'].browse(timesheet_id)
                                quantity += abs(timesheet.unit_amount)
                                timesheet_date = datetime.strptime(timesheet.date, "%Y-%m-%d")
                                if invoice_line_date_min is not None:
                                    if timesheet_date < invoice_line_date_min:
                                        invoice_line_date_min = timesheet_date
                                else:
                                    invoice_line_date_min = timesheet_date
                                if invoice_line_date_max is not None:
                                    if timesheet_date > invoice_line_date_max:
                                        invoice_line_date_max = timesheet_date
                                else:
                                    invoice_line_date_max = timesheet_date
                            #Compute price depending on invoicing type
                            if invoice_lines_done[invoice_line][0].code == "F":
                                price = (quantity)*invoice_line.price_unit
                            else:
                                if quantity <= invoice_line.quantity:
                                    price = invoice_line.price_subtotal/invoice_line.quantity*quantity
                                else:
                                    price = invoice_line.price_subtotal
                                
                            #Compute balance and use
                            balance -= price
                            use -= price
        
                            #If the invoice line has a default code, this means that the name is the employee name and the default code is the designation
                            if invoice_line.product_id.default_code:
                                designation = invoice_line.product_id.default_code
                                employee = invoice_line.product_id.name
                            #Otherwise the name is the real designation
                            else:
                                designation = invoice_line.product_id.name
                                employee = ''
                            #Recompute start and end date using the minimum and maximum dates of the invoice line
                            if invoice_line_date_max > end_date:
                                end_date = invoice_line_date_max
                            if invoice_line_date_min < start_date:
                                start_date = invoice_line_date_min
                            #Format the final date for the invoice line
                            if invoice_line_date_min == invoice_line_date_max:
                                invoice_line_date = invoice_line_date_min.strftime("%d.%m.%Y")
                            elif invoice_line_date_min.strftime("%m") == invoice_line_date_max.strftime("%m"):
                                invoice_line_date = invoice_line_date_min.strftime("%d")+"-"+invoice_line_date_max.strftime("%d.%m.%Y")
                            else:
                                invoice_line_date = invoice_line_date_min.strftime("%d.%m")+"-"+invoice_line_date_max.strftime("%d.%m.%Y")
                            #Add the invoice lines to the data
                            invoice_lines_final.append({'invoice':'FA'+str(invoice_line.invoice_id.number),
                                                        'date':invoice_line_date,
                                                        'sort':invoice_line_date_min.strftime("%Y%m%d"),
                                                        'designation':designation,
                                                        'quantity':quantity,
                                                        'rate':invoice_line.price_unit,
                                                        'advance':-price,
                                                        'employee':employee
                            })
                   
                balance_project += balance
                invoice_lines_final = sorted(invoice_lines_final, key=lambda k: k['sort'])
                #Add the task to the data
                tasks.append({'designation':financial_account,
                             'advance':amount,
                             'balance_previous_command':balance_previous_command,
                             'invoice_lines':invoice_lines_final,
                              'balance':balance,
                              'use':use
                })
        if ((start_date == datetime.max) or (end_date == datetime.min)):
            start_date = None
            end_date = None
        #Finalize data
        data = {'date_report':date_report,
                'project_name': docs.name,
                'start_date': start_date,
                'end_date': end_date,
                'total_project': total_project,
                'balance_project': balance_project,
                'tasks':tasks}
        #Add data to docargs
        docargs['datas'] = data
        #Send report render order
        return docargs