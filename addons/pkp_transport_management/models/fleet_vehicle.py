from odoo import api, fields, models, _

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    transporter_id = fields.Many2one('pkp.transport.transporter', string='Transporter', tracking=True)