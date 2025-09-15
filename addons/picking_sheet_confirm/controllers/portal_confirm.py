# -*- coding: utf-8 -*-
from odoo import http, fields, _
from odoo.http import request
import base64



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

        user = request.env['res.users'].sudo().browse(user_id)

        user.sudo().write({
            'line_uid': line_uid,
        })
        html = """
                <div style="max-width:720px;margin:24px auto;font-family:Arial,sans-serif">
                  <h3>ขอบคุณค่ะ/ครับ</h3>
                  <p>ระบบบันทึกการยืนยันรับของเรียบร้อยแล้ว</p>
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
            move = request.env['stock.move'].browse(int(move_id))
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

        # 👉 ส่ง HTML ตรงๆ (ไม่ render ผ่าน website.layout)
        html = """
        <div style="max-width:720px;margin:24px auto;font-family:Arial,sans-serif">
          <h3>ขอบคุณค่ะ/ครับ</h3>
          <p>ระบบบันทึกการยืนยันรับของเรียบร้อยแล้ว</p>
        </div>
        """
        return request.make_response(html, headers=[('Content-Type', 'text/html; charset=utf-8')])


    @http.route(['/picking/user/confirm/done'], type='http', auth='public')
    def picking_confirm_done_user(self, **kw):
        return request.render('picking_portal_user_confirm.picking_portal_thanks', {})