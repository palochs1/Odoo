# -*- coding: utf-8 -*-
import secrets
from odoo import api, fields, models, _
import logging
import requests
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    order_success = fields.Boolean(string="ส่งเสร็จสิ้น", copy=False, store=True)    
    order_failed = fields.Boolean(string="ส่งไม่สำเร็จ", copy=False, store=True)
    date_confirmed = fields.Datetime(string="Date Confirm At", copy=False, store=True)
    latitude = fields.Char(string="Latitude", copy=False, store=True)
    longitude = fields.Char(string="Longitude", copy=False, store=True)
    
    note_failed = fields.Text(string="หมายเหตุ", copy=False, store=True)   

    check_image = fields.Binary(string="Image Confirm", copy=False, readonly=True)