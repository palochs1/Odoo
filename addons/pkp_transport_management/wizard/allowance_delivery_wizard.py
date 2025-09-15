from odoo import fields, models, api, _
from datetime import datetime

class AllowanceDeliveryWizard(models.TransientModel):
    _name = 'pkp.allowance.delivery.wizard'
    _description = 'Allowance Delivery Wizard'

    date = fields.Date(string='Date')
    license_plate_ids = fields.Many2many('fleet.vehicle', string='License Plates')

    def _get_domain(self):
        domain = [('delivery_date', '>=', datetime.combine(self.date, datetime.min.time())), ('delivery_date', '<=', datetime.combine(self.date, datetime.max.time()))]
        if self.license_plate_ids:
            domain.append(('license_plate_id', 'in', self.license_plate_ids.ids))
        return domain

    def print_report(self):
        data = {
            'domain': self._get_domain(),
            'date': self.date
        }
        return self.env.ref('pkp_transport_management.action_allowance_delivery_report').report_action(self, data=data)