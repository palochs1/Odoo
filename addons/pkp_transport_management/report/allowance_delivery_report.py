from odoo import fields, models, api, _
from datetime import datetime

class ReportAllowanceDelivery(models.AbstractModel):
    _name = 'report.pkp_transport_management.report_allowance_delivery'
    _description = 'Allowance Delivery Report'

    def func_license_plate_group_by(self, lines):
        line_vals = []
        license_plate_ids = lines.mapped('license_plate_id')
        for license_plate in license_plate_ids:
            shipment_vals = []
            shipment_ids = lines.filtered(lambda x:x.license_plate_id.id == license_plate.id).sorted(key=lambda s:s.id)
            for shipment in shipment_ids:
                employee_vals = []
                total_allowance_amount = 0.0
                total_additional_amount = 0.0
                total_transport_amount = 0.0
                total_amount = 0.0
                for cost_line in shipment.employee_cost_ids:
                    vals = {
                        'employee_name': cost_line.employee_id.name,
                        'allowance_amount': cost_line.allowance_amount,
                        'additional_amount': cost_line.additional_amount,
                        'transport_amount': cost_line.transport_amount,
                        'total_amount': cost_line.total_amount
                    }
                    total_allowance_amount += cost_line.allowance_amount
                    total_additional_amount += cost_line.additional_amount
                    total_transport_amount += cost_line.transport_amount
                    total_amount += cost_line.total_amount
                    employee_vals.append(vals)
                shipment_vals = {
                    'delivery_date': datetime.strptime(shipment.delivery_date.strftime("%Y-%m-%d"), '%Y-%m-%d').strftime('%d/%m/%Y'),
                    'name': shipment.name, 
                    'license_plate': shipment.license_plate_id.license_plate or '',
                    'total_allowance_amount': total_allowance_amount,
                    'total_additional_amount': total_additional_amount,
                    'total_transport_amount': total_transport_amount,
                    'total_amount': total_amount,
                    'employee_cost_lines': employee_vals}
                line_vals.append(shipment_vals)
        return line_vals

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['pkp.transport.shipment'].search(data['domain'])
        return {
            'doc_ids': docids,
            'doc_model': 'pkp.transport.shipment',
            'docs': docs,
            'company': self.env.company,
            'date': datetime.strptime(data['date'], '%Y-%m-%d').strftime('%d/%m/%Y'),
            'func_license_plate_group_by': lambda x: self.func_license_plate_group_by(x),
        }