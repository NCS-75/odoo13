from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
import operator
#Import logger
import logging
#Get the logger
_logger = logging.getLogger(__name__)

class hr_timesheet_sheet_prisme(models.Model):
    _name = "account.analytic.line"
    _inherit = "account.analytic.line"
    
    old = ""
    client = False
    project = False

    def getSortedList(self):
        sortedList = self.sorted(key=operator.attrgetter('partner_id.name', 'account_id.name', 'date', 'time_beginning'))
        finalList = []
        tmpList = []
        total_hours = 0.0
        net_hours = 0.0
        current_project = None
        current_client = None
        current_user = None
        current_month = None
        for i, timesheet in enumerate(sortedList):
            timesheet.updateClAPr()
            if timesheet.getProject() and tmpList:
                finalList.append({"total_hours":total_hours,"net_hours":net_hours,"project":current_project,"client":current_client,"user":current_user,"month":current_month,"timesheets":tmpList})
                tmpList = []
                total_hours = 0.0
                net_hours = 0.0
                current_project = None
                current_client = None
                current_user = None
                current_month = None
            total_hours += timesheet.unit_amount
            net_hours += timesheet.unit_amount-((timesheet.to_invoice.factor*timesheet.unit_amount)/100.0)
            if current_project is None:
                current_project = timesheet.getProject()
            if current_client is None:
                current_client = timesheet.getClient()
            if current_user is None:
                current_user = timesheet.user_id.partner_id.name
            if current_month is None:
                current_month = datetime.strptime(timesheet.date, "%Y-%m-%d").strftime("%Y-%m")
            tmpList.append(timesheet)
            if (i == (len(sortedList) - 1)):
                if (not current_project) or (not current_client):
                    current_project = timesheet.account_id.name
                    current_client = timesheet.partner_id.name
                finalList.append({"total_hours":total_hours,"net_hours":net_hours,"project":current_project,"client":current_client,"user":current_user,"month":current_month,"timesheets":tmpList})
        return finalList
    
    def updateClAPr(self):
        if self.account_id.name == hr_timesheet_sheet_prisme.old:
            hr_timesheet_sheet_prisme.client = ""
            hr_timesheet_sheet_prisme.project = ""
        else:
            hr_timesheet_sheet_prisme.client = self.partner_id.name
            hr_timesheet_sheet_prisme.project = self.account_id.name
            hr_timesheet_sheet_prisme.old = self.account_id.name
            
    def getClient(self):
        return hr_timesheet_sheet_prisme.client

    def getProject(self):
        return hr_timesheet_sheet_prisme.project
    
    def getHeaderList(self):
        sortedList = self.sorted(key=operator.attrgetter('partner_id.name', 'account_id.name', 'date', 'time_beginning'))
        oldProject = ""
        totalsList = []
        totalHours = 0
        totalProject = 0
        netHours = sortedList[0].sheet_id.period_hours
        date = sortedList[0].sheet_id.name
        user = sortedList[0].sheet_id.employee_id.name
        for i, timesheet in enumerate(sortedList):
            if (not oldProject) or ((timesheet.partner_id.name + " - " +timesheet.account_id.name) != oldProject):
                if oldProject:
                    totalsList.append([oldProject, totalProject])
                    totalHours += totalProject
                    totalProject = 0
                oldProject = timesheet.partner_id.name + " - " +timesheet.account_id.name
            totalProject += timesheet.unit_amount
            if (i == (len(sortedList) - 1)):
                totalsList.append([oldProject, totalProject])
                totalHours += totalProject
        return [user, date, totalsList, totalHours, netHours]

    @api.onchange('project_id')
    def update_partner(self):
        if self.project_id:
            self.partner_id = self.project_id.partner_id
            self.account_id = self.project_id.analytic_account_id
        else:
            self.partner_id = None
            self.account_id = None

    @api.model
    def create(self, values):
        self.check_if_one_task_in_project(values)
        return super(hr_timesheet_sheet_prisme, self).create(values)
 
    @api.multi
    def write(self, values):
        self.check_if_one_task_in_project(values)
        return super(hr_timesheet_sheet_prisme, self).write(values)
    
    def check_if_one_task_in_project(self, values):
        for timesheet in self:
            if 'project_id' in values:
                project_id = timesheet.env['project.project'].browse(values['project_id'])
            else:
                project_id = timesheet.project_id
            if project_id:
                if project_id.tasks:
                    if 'task_id' in values:
                        task_id = values['task_id']
                    else:
                        task_id = timesheet.task_id
                    if not task_id:
                        raise ValidationError(_("There is at least one task available for this project ! Please select one."))