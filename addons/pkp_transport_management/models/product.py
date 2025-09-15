from odoo import models, fields, api, _

class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Product Low Stock
    product_low_stock_min_quantity = fields.Float(string='Minimum Quantity')
    product_low_stock_reorder_min_quantity = fields.Float(string='Minimum Quantity', compute='_compute_reorder_min_quantity')

    @api.depends('orderpoint_ids', 'orderpoint_ids.product_min_qty')
    def _compute_reorder_min_quantity(self):
        for rec in self:
            if rec.orderpoint_ids:
                for product in rec.orderpoint_ids[0]:
                    rec.product_low_stock_reorder_min_quantity = product.product_min_qty
            else:
                rec.product_low_stock_reorder_min_quantity = 0.0

class ProductTemplate(models.Model):
    _inherit = "product.template"

    cd_code = fields.Char(string='CD Code')

    # Product Low Stock
    template_low_stock_min_quantity = fields.Float(string='Minimum Quantity')
    template_low_stock_reorder_min_quantity = fields.Float(string='Minimum Quantity', compute='_compute_reorder_min_quantity')

    @api.depends('product_variant_id.orderpoint_ids', 'product_variant_id.orderpoint_ids.product_min_qty')
    def _compute_reorder_min_quantity(self):
        for rec in self:
            if rec.product_variant_id.orderpoint_ids:
                for product in rec.product_variant_id.orderpoint_ids[0]:
                    rec.template_low_stock_reorder_min_quantity = product.product_min_qty
            else:
                rec.template_low_stock_reorder_min_quantity = 0.0