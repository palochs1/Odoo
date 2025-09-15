from odoo import api, fields, models, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    cd_code = fields.Char(string='CD Code')