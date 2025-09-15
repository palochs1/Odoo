from odoo import http, fields, _
from odoo.http import request
import base64
import logging

_logger = logging.getLogger(__name__)

class WebsiteDeliveryOrdersConfirm(http.Controller):

    @http.route(['/delivery-confirm/<int:picking_id>/<string:line_uid>/<string:trans_id>'], type='http', auth='public', website=True, csrf=False)
    def delivery_confirm_form(self, picking_id, **kw):
        """ แสดงฟอร์มยืนยันส่งของ (plain QWeb) """
        # token = kw.get('token') or ''
        line_uid = (kw.get('line_uid') or '').strip()
        Picking = request.env['stock.picking'].sudo()
        picking = Picking.browse(picking_id)
        trand_id = int(kw.get('trans_id', 0))

        if not picking.exists():
            return request.not_found()

        # ถ้ามี access_token ให้ตรวจสอบ
        # if hasattr(picking, 'access_token') and token:
        #     if picking.access_token != token:
        #         return request.not_found()

        return request.render('website_delivery_orders.delivery_confirm_page', {
            'trans_id': trand_id,
            'picking': picking,
            'line_uid': line_uid,
        })

    @http.route(['/delivery_confirm/submit'], type='http', auth='public', csrf=False)
    def delivery_confirm_form_submit(self, **post):
        line_uid = (post.get('line_uid') or '').strip()
        picking_id = int(post.get('picking_id', 0))
        trans_id = int(post.get('trans_id', 0))
        # token = post.get('token')
        status = (post.get('status') or '').strip()
        note_failed = (post.get('note_failed') or '').strip()
        latitude = post.get('latitude')
        longitude = post.get('longitude')
        move_ids = request.httprequest.form.getlist('move_id[]')
        move_qtys = request.httprequest.form.getlist('move_qty[]')
        check_image = request.httprequest.files.get('check_image')

        picking = request.env['stock.picking'].sudo().browse(picking_id)
        if not picking.exists():
            return request.not_found()

        picking_lines = request.env['pkp.transport.shipment.picking.line'].sudo().search([
            ('picking_id', '=', picking_id),
            ('shipment_id', '=', trans_id),
        ])

        for move_id, qty in zip(move_ids, move_qtys):
            move = request.env['stock.move'].browse(int(move_id))
            if move.exists():
                move.write({'quantity_done': float(qty)})

        img_b64 = False
        if check_image and getattr(check_image, 'read', None):
            img_b64 = base64.b64encode(check_image.read())

        picking.sudo().write({
            'order_success': (status == 'success'),
            'order_failed':  (status == 'failed'),
            'note_failed': note_failed  or False,
            'date_confirmed': fields.Datetime.now(),
            'latitude': latitude or False,
            'longitude': longitude or False,
            'check_image': img_b64 or False,
            # 'shipment_state': 'at_destination' 
        })

        if picking_lines:
            picking_lines.sudo().write({
                'state': 'at_destination'
            })

 
        if(status == 'success'):
            # picking.sudo()._action_done()
            # picking.move_ids_without_package.sudo().write({'quantity_done': 'product_uom_qty'})
            for move in picking.move_ids_without_package:
                move.write({'quantity_done': move.product_uom_qty})

            picking.sudo()._action_done()
            _logger.info(f"Delivery Order {picking.state} confirmed as SUCCESS by website.")    
         
        home_url = f"/picking/delivery-orders/{line_uid}/{trans_id}" if line_uid else "/picking/delivery-orders"

        html = html = """
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"/>
            <style>
                .pg-confirm {{ 
                max-width: 820px;
                margin: 56px auto;
                padding: 0 20px;
                text-align: center;
                font-family: 'Noto Sans Thai', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
                }}
                .pg-confirm .icon {{
                width: 120px; height: 120px;
                margin: 8px auto 18px;
                border-radius: 999px;
                display: grid; place-items: center;
                background: #22c55e;
                box-shadow: 0 10px 30px rgba(34,197,94,.25);
                }}
                .pg-confirm .icon svg {{ width: 68px; height: 68px; }}
                .pg-confirm h3 {{
                font-weight: 800;
                font-size: clamp(28px, 5vw, 48px);
                margin: 8px 0 6px;
                letter-spacing: .2px;
                color: #0f172a;
                }}
                .pg-confirm p {{
                color: #6b8792;
                font-size: clamp(16px, 2.4vw, 22px);
                margin: 0 0 28px;
                }}
                .pg-confirm .panel {{
                display: inline-block;
                background: #dff5e7;
                border-radius: 20px;
                padding: 20px 24px;
                margin-top: 6px;
                }}
                .pg-confirm .btn {{
                display: inline-block;
                padding: 12px 24px;
                border-radius: 12px;
                background: #e74d4d;
                color: #fff; text-decoration: none;
                font-weight: 800; font-size: 18px;
                box-shadow: 0 8px 18px rgba(231,77,77,.25);
                }}
                .pg-confirm .btn:active {{ transform: translateY(1px); }}
            </style>

            <div class="pg-confirm">
                <div class="icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5"
                        stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M20 6L9 17l-5-5" />
                </svg>
                </div>

                <h3>ขอบคุณค่ะ/ครับ</h3>
                <p>ระบบยืนยันการส่งของเรียบร้อยแล้ว</p>

                <a class="btn" href="{home_url}">กลับสู่หน้าหลัก</a> 
                
                </div>
            """.format(home_url=home_url)
        return request.make_response(html, headers=[('Content-Type', 'text/html; charset=utf-8')])
