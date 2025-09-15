from odoo import api, fields, models, tools, _

class ProductCategory(models.Model):
    _inherit = 'product.category'

    code = fields.Char(string='Code')