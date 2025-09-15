from odoo import fields, models, api, _
from datetime import datetime

class ReportTransport(models.AbstractModel):
    _name = 'report.pkp_transport_management.report_transport'
    _description = 'Transport Report'

    def func_date_format(self, date=None):
        year_thai = int(date.strftime('%Y')) + 543
        date_format = date.strftime('{}/{}/{}'.format('%d', '%m', year_thai))
        return date_format
    
    def func_get_invoice(self, picking_id):
        invoice = False
        order_name = picking_id.group_id.name if picking_id.group_id else picking_id.origin
        order_id = self.env['sale.order'].search([('name', '=', order_name)])
        invoices = order_id.order_line.invoice_lines.move_id.filtered(lambda x: x.picking_id.id == picking_id.id)
        invoice = invoices[0] if invoices else False
        return invoice
    
    def func_get_invoice_quantity(self, picking_id):
        quantity = 0.0
        order_name = picking_id.group_id.name if picking_id.group_id else picking_id.origin
        order_id = self.env['sale.order'].search([('name', '=', order_name)])
        invoices = order_id.order_line.invoice_lines.move_id.filtered(lambda x: x.picking_id.id == picking_id.id)
        if invoices and invoices[0].move_summary_line_ids:
            quantity = invoices[0].move_summary_line_ids.filtered(lambda x:x.sequence == 1)[0].quantity
        return quantity

    def func_get_invoice_secondary_quantity(self, picking_id):
        quantity = 0.0
        order_name = picking_id.group_id.name if picking_id.group_id else picking_id.origin
        order_id = self.env['sale.order'].search([('name', '=', order_name)])
        invoices = order_id.order_line.invoice_lines.move_id.filtered(lambda x: x.picking_id.id == picking_id.id)
        if invoices and invoices[0].move_summary_line_ids:
            quantity = invoices[0].move_summary_line_ids.filtered(lambda x:x.sequence == 2)[0].quantity
        return quantity

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['pkp.transport.shipment'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'pkp.transport.shipment',
            'docs': docs,
            'func_date_format': lambda x: self.func_date_format(x),
            'func_get_invoice': lambda x: self.func_get_invoice(x),
            'func_get_invoice_quantity': lambda x: self.func_get_invoice_quantity(x),
            'func_get_invoice_secondary_quantity': lambda x: self.func_get_invoice_secondary_quantity(x)
        }