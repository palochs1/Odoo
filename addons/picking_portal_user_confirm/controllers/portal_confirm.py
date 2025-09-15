# -*- coding: utf-8 -*-
from odoo import http, fields, _
from odoo.http import request
import base64
import logging

_logger = logging.getLogger(__name__)



class PickingUserPortalConfirm(http.Controller):



    # @http.route(['/user/confirm/<string:token>'], type='http', auth='public', csrf=False)
    @http.route(['/user/confirm'], type='http', auth='public', csrf=False)
    def user_confirm_view(self, **kw):
        users = request.env['res.users'].sudo().search([])
        # if not users or users.access_token != token:
        #     return request.not_found()
        values = {
            'users': users,
        }
        return request.render('picking_portal_user_confirm.user_portal_page_headless', values)

    @http.route(['/user/confirm/submit'], type='http', auth='public', csrf=False)
    def user_confirm_submit(self, **post):
        # picking_id = int(post.get('picking_id', 0))
        # token = post.get('token')
        user_id = int(post.get('user_id', 0))
        line_uid = post.get('line_uid')
        type_users = post.get('type_users')

        
        user = request.env['res.users'].sudo().browse(user_id)
        user.sudo().write({
            'line_uid': line_uid,
            'type_users': type_users,
        })

        _logger.warning(".............111..................")
        user.sudo()._set_richmenu_call()
        _logger.warning("..............222.................")
        html = """
                <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"/>
                <style>
                  /* กันชนชื่อ class ไม่ชนของ Odoo */
                  .pg-confirm { 
                    max-width: 820px;
                    margin: 56px auto;
                    padding: 0 20px;
                    text-align: center;
                    font-family: 'Noto Sans Thai', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
                  }
                  .pg-confirm .icon {
                    width: 120px; height: 120px;
                    margin: 8px auto 18px;
                    border-radius: 999px;
                    display: grid; place-items: center;
                    background: #22c55e;           /* เขียวสำเร็จ */
                    box-shadow: 0 10px 30px rgba(34,197,94,.25);
                  }
                  .pg-confirm .icon svg { width: 68px; height: 68px; }
                  .pg-confirm h3 {
                    font-weight: 800;
                    font-size: clamp(28px, 5vw, 48px);
                    margin: 8px 0 6px;
                    letter-spacing: .2px;
                    color: #0f172a;
                  }
                  .pg-confirm p {
                    color: #6b8792;
                    font-size: clamp(16px, 2.4vw, 22px);
                    margin: 0 0 28px;
                  }
                  .pg-confirm .panel {
                    display: inline-block;
                    background: #dff5e7;           /* เขียวอ่อนพื้น */
                    border-radius: 20px;
                    padding: 20px 24px;
                    margin-top: 6px;
                  }
                  .pg-confirm .btn {
                    display: inline-block;
                    padding: 12px 24px;
                    border-radius: 12px;
                    background: #e74d4d;           /* สีแดงแบรนด์ */
                    color: #fff; text-decoration: none;
                    font-weight: 800; font-size: 18px;
                    box-shadow: 0 8px 18px rgba(231,77,77,.25);
                  }
                  .pg-confirm .btn:active { transform: translateY(1px); }
                </style>
                
                <div class="pg-confirm">
                  <div class="icon" aria-hidden="true">
                    <!-- วงกลมเขียว + เครื่องหมายถูก -->
                    <svg viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5"
                         stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                      <path d="M20 6L9 17l-5-5" />
                    </svg>
                  </div>
                
                  <h3>ขอบคุณค่ะ/ครับ</h3>
                  <p>ระบบบันทึกการลงทะเบียนเรียบร้อยแล้ว</p>
                </div>
                """
        return request.make_response(html, headers=[('Content-Type', 'text/html; charset=utf-8')])



    @http.route(['/picking/user/confirm/<int:picking_id>/<string:token>'],
                type='http', auth='public', csrf=False)
                # type='http', auth='public', website=True, csrf=False)
    def picking_confirm_view_user(self, picking_id, token, **kw):
        picking = request.env['stock.picking'].sudo().browse(picking_id)
        if not picking or picking.access_token != token:
            return request.not_found()
        stock_moves = request.env['stock.move'].sudo().search([('picking_id', '=', picking.id)])

        values = {
            'picking': picking,
            'token': token,
            'stock_moves': stock_moves,
        }
        # return request.render('picking_portal_confirm_btn.picking_portal_page', values)
        return request.render('picking_portal_user_confirm.picking_portal_page_headless', values)

    # ปุ่ม submit (headless)
    @http.route(['/picking/user/confirm/submit'], type='http', auth='public', csrf=False)
    def picking_confirm_submit_user(self, **post):
        picking_id = int(post.get('picking_id', 0))
        token = post.get('token')
        customer_name = (post.get('customer_name') or '').strip()
        note = (post.get('note') or '').strip()
        latitude = post.get('latitude')
        longitude = post.get('longitude')
        move_ids = request.httprequest.form.getlist('move_id[]')
        move_qtys = request.httprequest.form.getlist('move_qty[]')
        check_image = request.httprequest.files.get('check_image')

        picking = request.env['stock.picking'].sudo().browse(picking_id)
        if not picking or picking.access_token != token:
            return request.not_found()


        for move_id, qty in zip(move_ids, move_qtys):
            move = request.env['stock.move'].sudo().browse(int(move_id))
            if move.exists():
                move.write({'quantity_done': float(qty)})

        img_b64 = False
        if check_image and getattr(check_image, 'read', None):
            img_b64 = base64.b64encode(check_image.read())

        picking.sudo().write({
            'portal_confirmed': True,
            'portal_confirmed_by': customer_name or 'Customer',
            'portal_confirmed_note': note or False,
            'portal_confirmed_datetime': fields.Datetime.now(),
            'latitude': latitude or False,
            'longitude': longitude or False,
            'check_image': img_b64 or False,
        })

        home_url = "/picking/user/confirm/{}/{}".format(picking.id, token)
        # home_url = ""
        # # 👉 ส่ง HTML ตรงๆ (ไม่ render ผ่าน website.layout)
        html = """
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


    @http.route(['/picking/user/confirm/done'], type='http', auth='public')
    def picking_confirm_done_user(self, **kw):
        return request.render('picking_portal_user_confirm.picking_portal_thanks', {})