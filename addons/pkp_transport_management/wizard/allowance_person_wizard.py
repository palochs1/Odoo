from odoo import fields, models, api, _
from datetime import datetime

class AllowancePersonWizard(models.TransientModel):
    _name = 'pkp.allowance.person.wizard'
    _description = 'Allowance Person Wizard'

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    employee_ids = fields.Many2many('hr.employee', string="Employees")

    def _get_domain(self):
        domain = [('shipment_id.delivery_date', '>=', datetime.combine(self.start_date, datetime.min.time())), ('shipment_id.delivery_date', '<=', datetime.combine(self.end_date, datetime.max.time()))]
        if self.employee_ids:
            domain.append(('employee_id', 'in', self.employee_ids.ids))
        return domain

    def print_report(self):
        data = {
            'domain': self._get_domain(),
            'start_date': self.start_date,
            'end_date': self.end_date,
            'employee_ids': self.employee_ids.ids if self.employee_ids else False
        }
        return self.env.ref('pkp_transport_management.action_allowance_person_report').report_action(self, data=data)