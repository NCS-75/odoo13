from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class prisme_account_analytic_line(models.Model):
    _inherit = 'account.analytic.line'
    _order="date ASC, user_id ASC, time_beginning ASC"
    
    time_beginning =  fields.Float("Beginning")
    time_end = fields.Float("End")
    internal_description = fields.Text("Internal Description")
    working_month = fields.Char(compute='_get_month', store=True)
    sheet_id_computed = fields.Many2one('hr_timesheet_sheet.sheet', string='Sheet Computed', compute='_compute_sheet', index=True, ondelete='cascade',
        search='_search_sheet')
    sheet_id = fields.Many2one('hr_timesheet_sheet.sheet', compute='_compute_sheet', string='Sheet', store=True)
    general_account_id = fields.Many2one('account.account', related='product_id.property_account_expense_id', readonly=True, store=True)
    
    #Update partner and analytic account
    @api.onchange('project_id')
    def _onchange_project(self):
        if self.project_id and self.project_id.partner_id:
            self.partner_id = self.project_id.partner_id
        else:
            self.partner_id = None

        if self.project_id and self.project_id.analytic_account_id:
            self.account_id = self.project_id.analytic_account_id
        else:
            self.account_id = None

    @api.depends('date')
    def _get_month(self):
        for line in self:
            date = line.date
            month = date.strftime('%Y-%m')
            line.working_month = month

    #Update product associated to employee
    @api.onchange('user_id')
    def getEmployeeProduct(self):
        emp_obj = self.env['hr.employee']
        emp = emp_obj.search([('user_id', '=', self.user_id.id or self.env.uid)], limit=1)
        if emp:
            if emp.product_id:
                self.product_id = emp.product_id.id
				#Make sure amount is updated
                self.on_change_unit_amount()
    
    @api.onchange('time_beginning', 'time_end')
    def onchange_times(self):
        self.unit_amount = self.time_end - self.time_beginning
        
    @api.constrains('time_beginning')
    def _check_beginning(self):
        for hr_line in self:
            beginning = hr_line.time_beginning
            if not (beginning >= 0 and beginning <= 24):
                raise ValidationError(_("Beginning time must be between 00:00 and 24:00"))
    
    @api.constrains('time_end')
    def _check_end(self):
        for hr_line in self:
            end = hr_line.time_end
            if not (end >= 0 and end <= 24):
                raise ValidationError(_("End time must be between 00:00 and 24:00"))

    @api.constrains('time_beginning', 'time_end')
    def _check_beginning_end(self):
        for hr_line in self:
            beginning = hr_line.time_beginning
            end = hr_line.time_end
            if not (beginning <= end or end == 0):
                raise ValidationError(_("End time must not be before beginning time"))

    @api.depends('date', 'user_id', 'project_id', 'sheet_id_computed.date_to', 'sheet_id_computed.date_from', 'sheet_id_computed.employee_id')
    def _compute_sheet(self):
        """Links the timesheet line to the corresponding sheet
        """
        for ts_line in self:
            if not ts_line.project_id:
                continue
            sheets = self.env['hr_timesheet_sheet.sheet'].search(
                [('date_to', '>=', ts_line.date), ('date_from', '<=', ts_line.date),
                 ('employee_id.user_id.id', '=', ts_line.user_id.id),
                 ('state', 'in', ['draft', 'new'])])
            if sheets:
                # [0] because only one sheet possible for an employee between 2 dates
                ts_line.sheet_id_computed = sheets[0]
                ts_line.sheet_id = sheets[0]

    def _search_sheet(self, operator, value):
        if operator == 'in':
            ids = []
            for ts in self.env['hr_timesheet_sheet.sheet'].browse(value):
                self._cr.execute("""
                        SELECT l.id
                            FROM account_analytic_line l
                        WHERE %(date_to)s >= l.date
                            AND %(date_from)s <= l.date
                            AND %(user_id)s = l.user_id
                        GROUP BY l.id""", {'date_from': ts.date_from,
                                           'date_to': ts.date_to,
                                           'user_id': ts.employee_id.user_id.id, })
                ids.extend([row[0] for row in self._cr.fetchall()])
            return [('id', 'in', ids)]
        else:
            return []

    def write(self, values):
        self._check_state()
        self._check_if_one_task_in_project(values)
        return super(prisme_account_analytic_line, self).write(values)

    def unlink(self):
        self._check_state()
        return super(prisme_account_analytic_line, self).unlink()

    def _check_state(self):
        for line in self:
            if line.sheet_id and line.sheet_id.state not in ('draft', 'new'):
                raise UserError(_('You cannot modify an entry in a confirmed timesheet.'))
        return True
    
    def _check_if_one_task_in_project(self, values):
        for line in self:
            if 'project_id' in values:
                project_id = line.env['project.project'].browse(values['project_id'])
            else:
                project_id = line.project_id
            if project_id:
                if project_id.tasks:
                    if 'task_id' in values:
                        task_id = values['task_id']
                    else:
                        task_id = line.task_id
                    if not task_id:
                        raise ValidationError(_("There is at least one task available for this project ! Please select one."))