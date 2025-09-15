from odoo import fields, models, api, _
from datetime import datetime

class ReportAllowancePerson(models.AbstractModel):
    _name = 'report.pkp_transport_management.report_allowance_person'
    _description = 'Allowance Person Report'

    def func_employee_group_by(self, lines):
        line_vals = []
        employee_ids = lines.mapped('employee_id')
        for employee in employee_ids:
            cost_vals = []
            employee_total_amount = 0.0
            shipment_ids = lines.filtered(lambda x:x.employee_id.id == employee.id).sorted(key=lambda s:s.shipment_id).mapped('shipment_id')
            for shipment in shipment_ids:
                total_amount = 0.0
                for line in lines.filtered(lambda x:x.employee_id.id == employee.id and x.shipment_id.id == shipment.id):
                    total_amount += line.total_amount
                vals = {
                    'shipment_name': shipment.name,
                    'delivery_date': shipment.delivery_date,
                    'amount': total_amount
                }
                employee_total_amount += total_amount
                cost_vals.append(vals)
            employee_vals = {'name': employee.name, 'employee_total_amount': employee_total_amount, 'cost_lines': cost_vals}
            line_vals.append(employee_vals)
        return line_vals

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['pkp.transport.shipment.employee.cost.line'].search(data['domain'])
        return {
            'doc_ids': docids,
            'doc_model': 'pkp.transport.shipment.employee.cost.line',
            'docs': docs,
            'company': self.env.company,
            'start_date': datetime.strptime(data['start_date'], '%Y-%m-%d').strftime('%d/%m/%Y'),
            'end_date': datetime.strptime(data['end_date'], '%Y-%m-%d').strftime('%d/%m/%Y'),
            'func_employee_group_by': lambda x: self.func_employee_group_by(x),
        }