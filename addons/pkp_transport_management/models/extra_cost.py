from odoo import models, fields, api, _

class TransportExtraCost(models.Model):
    _name = 'pkp.transport.extra.cost'
    _description = 'Transport Extra Cost'

    name = fields.Char(string='Name')
    line_ids = fields.One2many('pkp.transport.extra.cost.line', 'extra_cost_id', string='Extra Cost Lines')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one("res.currency", string='Currency', default=lambda self: self.env.user.company_id.currency_id)
    extra_cost_total_amount = fields.Monetary(string="Total Amount", currency_field='currency_id', compute="_compute_extra_cost_total_amount")

    _sql_constraints = [
        ('name_company_uniq', 'unique (name,company_id)', 'The name of the extra cost must be unique per company !')
    ]

    @api.depends('line_ids', 'line_ids.price_subtotal')
    def _compute_extra_cost_total_amount(self):
        for rec in self:
            rec.extra_cost_total_amount = 0.0
            if rec.line_ids:
                rec.extra_cost_total_amount = sum(rec.line_ids.mapped('price_subtotal'))

class TransportExtraCostLines(models.Model):
    _name = 'pkp.transport.extra.cost.line'
    _description = 'Transport Extra Cost Lines'

    extra_cost_id = fields.Many2one('pkp.transport.extra.cost', string='Extra Cost Template')
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Text(string='Description')
    quantity = fields.Float(string='Quantity', default=1.0, digits='Product Unit of Measure')
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    price_subtotal = fields.Monetary(string='Subtotal', currency_field='currency_id', compute='_compute_amount', store=True)
    currency_id = fields.Many2one("res.currency", string='Currency', default=lambda self: self.env.user.company_id.currency_id)
    cost_type = fields.Selection([
        ('shipping', _('Shipping')),
        ('parking', _('Parking')),
        ('expressway', _('Expressway')),
        ('phone', _('Phone')),
        ('other', _('Other'))], string='Cost Type')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if not self.product_id:
            return
        self.name = self.product_id.name
        self.price_unit = self.quantity = 0.0
        self.product_uom_id = self.product_id.uom_id
    
    @api.depends('quantity', 'price_unit')
    def _compute_amount(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit