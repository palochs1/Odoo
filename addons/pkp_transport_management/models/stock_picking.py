from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_transportation = fields.Boolean(string='Transportation')
    transporter_id = fields.Many2one('pkp.transport.transporter', string='Transporter', tracking=True)
    shipment_id = fields.Many2one('pkp.transport.shipment', string='Transport Shipment', tracking=True)
    license_plate_id = fields.Many2one('fleet.vehicle', string='License Plate', related='shipment_id.license_plate_id')
    shipment_detail = fields.Text(string='Shipment Detail')
    delivery_place_id = fields.Many2one('pkp.delivery.place', string='Delivery Place', tracking=True)

    shipment_state = fields.Selection([
        ('in_transit', _('In Transit')),
        ('at_destination', _('At Destination')),
        ('cancel', _('Cancelled'))], string='Shipment Status', default='in_transit')