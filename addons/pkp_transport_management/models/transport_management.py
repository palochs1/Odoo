from odoo import models, fields, api, _

class Transporter(models.Model):
    _name = 'pkp.transport.transporter'
    _description = 'Transporter'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'avatar.mixin']

    name = fields.Char(default='New', copy=False, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Contact Name', tracking=True)
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    country_code = fields.Char(related='country_id.code', string="Country Code")
    email = fields.Char()
    phone = fields.Char()
    mobile = fields.Char()
    currency_id = fields.Many2one("res.currency", string='Currency', default=lambda self: self.env.user.company_id.currency_id)
    charge_amount = fields.Monetary(string='Transport Charge', currency_field='currency_id', default=0.0, tracking=True)
    fleet_count = fields.Integer(compute='_compute_fleet_count', string='Fleet Count')
    fleet_ids = fields.Many2many('fleet.vehicle', string='Fleets', compute='_compute_fleet_count')

    _sql_constraints = [
        ('name_company_uniq', 'unique (name,company_id)', 'The name of the transporter must be unique per company !')
    ]

    def _compute_fleet_count(self):
        for rec in self:
            fleet_ids = rec.env['fleet.vehicle'].search([('transporter_id', '=', rec.id)])
            rec.fleet_count = len(fleet_ids)
            rec.fleet_ids = fleet_ids
    
    def action_view_fleet(self):
        res = self.env['ir.actions.act_window']._for_xml_id('fleet.fleet_vehicle_action')
        res['domain'] = [('id', 'in', self.fleet_ids.ids)]
        res['context'] = {
            'default_res_model': 'fleet.vehicle',
            'default_res_id': self.fleet_ids[0].id,
            'create': False,
            'edit': False,
        }
        return res

    @api.depends('name', 'image_1920')
    def _compute_avatar_1920(self):
        super()._compute_avatar_1920()

    @api.depends('name', 'image_1024')
    def _compute_avatar_1024(self):
        super()._compute_avatar_1024()

    @api.depends('name', 'image_512')
    def _compute_avatar_512(self):
        super()._compute_avatar_512()

    @api.depends('name', 'image_256')
    def _compute_avatar_256(self):
        super()._compute_avatar_256()

    @api.depends('name', 'image_128')
    def _compute_avatar_128(self):
        super()._compute_avatar_128()
    
    @api.onchange('email')
    def _onchange_email(self):
        if not self.image_1920 and self._context.get('gravatar_image') and self.email:
            self.image_1920 = self._get_gravatar_image(self.email)

class TransportShipment(models.Model):
    _name = 'pkp.transport.shipment'
    _description = 'Transport Shipments'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    EDIT_STATES = {
        'draft': [('readonly', False)],
        'arranging': [('readonly', False)],
        'in_transit': [('readonly', False)],
        'arrived': [('readonly', False)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    name = fields.Char(string='Shipment No.', default='New', copy=False, states=EDIT_STATES)
    state = fields.Selection([
        ('draft', _('Draft')),
        ('arranging', _('Arranging')),
        ('in_transit', _('In Transit')),
        ('arrived', _('Arrived')),
        ('done', _('Done')),
        ('cancel', _('Cancelled'))], string='Status', default='draft', readonly=True, tracking=True)
    transporter_id = fields.Many2one('pkp.transport.transporter', string='Transporter', tracking=True, states=EDIT_STATES)
    license_plate_id = fields.Many2one('fleet.vehicle', string='License Plate', tracking=True, states=EDIT_STATES)
    driver_id = fields.Many2one('res.partner', string='Driver', states=EDIT_STATES)
    delivery_date = fields.Datetime(string='Delivery Date', index=True, default=fields.Datetime.now, states=EDIT_STATES)
    close_date = fields.Datetime(string='Closed Date', states=EDIT_STATES)
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user, states=EDIT_STATES)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, states=EDIT_STATES)
    currency_id = fields.Many2one("res.currency", string='Currency', default=lambda self: self.env.user.company_id.currency_id, states=EDIT_STATES)
    picking_ids = fields.One2many('pkp.transport.shipment.picking.line', 'shipment_id', string='Picking Order Lines', states=EDIT_STATES)
    extra_cost_ids = fields.One2many('pkp.transport.shipment.extra.cost.line', 'shipment_id', string='Extra Cost Lines', states=EDIT_STATES)
    extra_cost_total_amount = fields.Monetary(string="Total Amount", currency_field='currency_id', compute="_compute_extra_cost_total_amount", states=EDIT_STATES)
    extra_cost_id = fields.Many2one('pkp.transport.extra.cost', string='Extra Cost Template', states=EDIT_STATES)

    remark = fields.Text('Remark', states=EDIT_STATES)
    gas_amount = fields.Monetary(string='Gas Amount', default=0.0, currency_field='currency_id', states=EDIT_STATES)
    liter = fields.Float(string='Liter (L.)', default=0.0, states=EDIT_STATES)
    mileage = fields.Float(string='Mile (Km.)', default=0.0, states=EDIT_STATES)
    gas_date = fields.Date(string='Date', states=EDIT_STATES)
    employee_cost_ids = fields.One2many('pkp.transport.shipment.employee.cost.line', 'shipment_id', string='Employee Cost Lines', states=EDIT_STATES)
    employee_cost_total_amount = fields.Monetary(string='Total Amount', currency_field='currency_id', compute='_compute_employee_cost_total_amount', states=EDIT_STATES)
    invoice_ids = fields.Many2many('account.move', 'transport_shipment_match_account_move_rel', string='Invoices', states=EDIT_STATES)

    # CUSTOM
    mileage_start = fields.Float(string='Mile Start', default=0.0, states=EDIT_STATES)
    mileage_end = fields.Float(string='Mile End', default=0.0, states=EDIT_STATES)
    reference_all = fields.Text('Reference', states=EDIT_STATES)
    # CUSTOM

    @api.depends('extra_cost_ids', 'extra_cost_ids.price_subtotal')
    def _compute_extra_cost_total_amount(self):
        for rec in self:
            rec.extra_cost_total_amount = 0.0
            if rec.extra_cost_ids:
                rec.extra_cost_total_amount = sum(rec.extra_cost_ids.mapped('price_subtotal'))

    @api.model
    def create(self, vals):
        company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
        date = fields.Date.today()
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].with_company(company_id).next_by_code('pkp.transport.shipment', sequence_date=date) or '/'
        return super(TransportShipment, self).create(vals)
    
    @api.depends('employee_cost_ids', 'employee_cost_ids.total_amount')
    def _compute_employee_cost_total_amount(self):
        for rec in self:
            rec.employee_cost_total_amount = 0.0
            if rec.employee_cost_ids:
                rec.employee_cost_total_amount = sum(rec.employee_cost_ids.mapped('total_amount'))
    
    @api.onchange('license_plate_id')
    def _onchange_license_plate_id(self):
        if not self.license_plate_id:
            return
        self.driver_id = self.license_plate_id.driver_id.id if self.license_plate_id.driver_id else False
    
    def _prepare_extra_cost_vals(self, line):
        return {
            'product_id': line.product_id.id,
            'name': line.name,
            'cost_type': line.cost_type,
            'quantity': line.quantity,
            'price_unit': line.price_unit,
            'product_uom_id': line.product_uom_id.id,
            'price_subtotal': line.price_subtotal
        }

    @api.onchange('extra_cost_id')
    def _onchange_extra_cost_id(self):
        if not self.extra_cost_id:
            return

        line_ids = [(5, 0, 0)]
        for line in self.extra_cost_id.line_ids:
            vals = self._prepare_extra_cost_vals(line)
            line_ids.append((0, 0, vals))
        self.write({'extra_cost_ids': line_ids})
    
    def action_arrang(self):
        self.write({'state': 'arranging'})

    def action_start(self):
        self.write({'state': 'in_transit'})
    
    def action_end(self):
        self.write({'state': 'arrived'})
    
    def action_close(self):
        self.write({'state': 'done', 'close_date': fields.Datetime.today()})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_draft(self):
        self.write({'state': 'draft'})
    
    def _get_allowance_delivery_report_base_filename(self):
        self.ensure_one()
        return 'Allowance Deliveries'
    
    def _get_transport_report_base_filename(self):
        self.ensure_one()
        return 'Transport_{}'.format(self.name)

class TransportShipmentPickingLines(models.Model):
    _name = 'pkp.transport.shipment.picking.line'
    _description = 'Transport Shipment Picking Lines'

    shipment_id = fields.Many2one('pkp.transport.shipment', string='Shipment')
    sequence = fields.Integer(string='Sequence', default=1)
    picking_id = fields.Many2one('stock.picking', string='Picking')
    origin = fields.Char(string='Source Document', related='picking_id.origin', store=True)
    partner_id = fields.Many2one('res.partner', string='Destination', related='picking_id.partner_id', store=True)
    delivery_place_id = fields.Many2one('pkp.delivery.place', string='Delivery Place', related='picking_id.delivery_place_id', store=True)
    remark = fields.Text(string='Remark')
    state = fields.Selection([
        ('in_transit', _('In Transit')),
        ('at_destination', _('At Destination')),
        ('cancel', _('Cancelled'))], string='Status', default='in_transit')


    transport_remark = fields.Many2one('transport.remark', string='Transport Remark')

    @api.model_create_multi
    def create(self, vals_list):
        lines = super(TransportShipmentPickingLines, self).create(vals_list)
        for line in lines:
            line.picking_id.write({'shipment_state':line.state})

    def write(self, vals):
        # picking_in = self.env['stock.picking'].search([('','',)])
        lines = super(TransportShipmentPickingLines, self).write(vals)
        self.picking_id.write({'shipment_state':self.state})

        return lines

class TransportShipmentExtraCostLine(models.Model):
    _name = 'pkp.transport.shipment.extra.cost.line'
    _description = 'Transport Shipment Extra Cost Lines'

    shipment_id = fields.Many2one('pkp.transport.shipment', string='Shipment')
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

class TransportShipmentEmployeeCostLine(models.Model):
    _name = 'pkp.transport.shipment.employee.cost.line'
    _description = 'Transport Shipment Employee Cost Lines'

    shipment_id = fields.Many2one('pkp.transport.shipment', string='Shipment')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    allowance_amount = fields.Monetary(string='Allowance Amount', default=0.0, currency_field='currency_id')
    additional_amount = fields.Monetary(string='Additional Amount', default=0.0, currency_field='currency_id')
    transport_amount = fields.Monetary(string='Transport Amount', default=0.0, currency_field='currency_id')
    total_amount = fields.Monetary(string='Total', currency_field='currency_id', default=0.0, compute='_compute_total_amount', store=True)
    currency_id = fields.Many2one("res.currency", string='Currency', default=lambda self: self.env.user.company_id.currency_id)

    @api.depends('allowance_amount', 'additional_amount', 'transport_amount')
    def _compute_total_amount(self):
        for line in self:
            line.total_amount = line.allowance_amount + line.additional_amount + line.transport_amount

    def _get_allowance_person_report_base_filename(self):
        self.ensure_one()
        return 'Allowance Persons'