from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class DeliveryPlace(models.Model):
    _name = 'pkp.delivery.place'
    _description = 'Delivery Places'

    name = fields.Char(string='Name')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the place must be unique!'),
    ]