# -*- coding: utf-8 -*-
from odoo import http ,fields
from odoo.http import request
from math import ceil
from datetime import datetime, time, timedelta
import pytz
import logging
_logger = logging.getLogger(__name__)

class WebsiteProject(http.Controller):

    @http.route(['/website/project/task/<string:line_uid>/<string:pro_id>'], type='http', auth='public', website=True, csrf=False)
    def website_project_task(self, line_uid, pro_id, **kwargs):
       
        try:
            page = int(kwargs.get('page') or 1)
        except Exception:
            page = 1
        q = (kwargs.get('q') or '').strip()
        limit = 20
        offset = (page - 1) * limit

        # --- หา user จาก line_uid ---
        Users = request.env['res.users'].sudo()
        user = Users.search([('line_uid', '=', line_uid)], limit=1)

        if not user:
            # ไม่พบผู้ใช้จาก line_uid ที่ส่งมา — แสดงหน้าเปล่าพร้อมข้อความ
            return request.render('website_project.website_project_task_page_html', {
                'pickings': request.env['project.task'],  # empty recordset
                'total': 0,
                'page': 1,
                'page_count': 1,
                'prev_page': False,
                'next_page': False,
                'q': q,
                'warning': "ไม่พบบัญชีผู้ใช้จาก LINE UID ที่ระบุ กรุณาลงทะเบียนก่อน หรือเปิดลิงก์จากใน LINE อีกครั้ง",
            })

        # task = request.env['project.task'].sudo().search([('project_id', '=', int(pro_id)), ('active', '=', True)])
        task = request.env['project.task'].sudo()

        # --- ดึง company_id จาก user ---
        user_id = user.id
        # company_id = user.company_id.id or request.website.company_id.id

        tz = pytz.timezone(user.tz or 'UTC')
        today_user = fields.Date.context_today(user)

        start_user = tz.localize(datetime.combine(today_user, time.min))
        end_user   = tz.localize(datetime.combine(today_user + timedelta(days=1), time.min))

        start_utc = start_user.astimezone(pytz.utc).replace(tzinfo=None)
        end_utc   = end_user.astimezone(pytz.utc).replace(tzinfo=None)


        # --- สร้าง domain เฉพาะ Delivery Orders ของ company นี้ ---
        # picking_all = request.env['pkp.transport.shipment'].sudo().search([('id','=',int(trans_id))])
        domain = [
            ('user_ids','in', user_id),
            ('project_id', '=', int(pro_id)),
            ('active', '=', True),
        ]
        # ถ้าต้องการให้เห็นเฉพาะของลูกค้าคนนี้ (ตาม partner ของ user) ให้ปลดคอมเมนต์บรรทัดนี้
        # if user.partner_id:
        #     domain.append(('partner_id', '=', user.partner_id.id))

        # --- เสริมค้นหาแบบ keyword ---
        if q:
            domain += ['|', '|',
                       ('name', 'ilike', q)]

        # picking_all = request.env['pkp.transport.shipment'].sudo().search([('id','=',int(trans_id))])

        # picking = request.env['stock.picking'].sudo().search([('id','in',picking_all.picking_ids.picking_id.ids)])
        # _logger.info(f"Delivery Orders domain: {picking_all} {picking} {picking_all.picking_ids.picking_id.ids}")
        
        # pickings = picking
        # _logger.info(f"Delivery Orders domain: {picking_all} {picking} {pickings} {picking_all.picking_ids.picking_id.ids}")
        


        # picking = request.env['stock.picking'].sudo()
        project_task = task
        total = project_task.search_count(domain)
        project_tasks = project_task.search(
            domain,
            limit=limit,
            offset=offset,
            order='date_deadline desc, id desc'
        )

        # project_task = task

        # total = picking.search_count(domain)
        

        # total = picking.search_count(domain)
        # pickings = picking.search(
        #     domain,
        #     limit=limit,
        #     offset=offset,
        #     order='scheduled_date desc, id desc'
        # )

        page_count = max(1, int(ceil(total / float(limit))))
        prev_page = page - 1 if page > 1 else False
        next_page = page + 1 if page < page_count else False

        return request.render('website_project.website_project_task_page_html', {
            'pro_id': pro_id,
            'project_task': project_tasks,
            'total': total,
            'page': page,
            'page_count': page_count,
            'prev_page': prev_page,
            'next_page': next_page,
            'q': q,
            'login_user': user,
            # 'company_id': company_id,
            'line_uid': line_uid,
        })

    @http.route('/liff/project', type='http', auth='public', website=True, csrf=False)
    def liff_delivery(self, **kw):
        # ดึง LIFF ID จาก System Parameter (หรือจะฮาร์ดโค้ดก็ได้)
        liff_id = request.env['ir.config_parameter'].sudo().get_param('liff_id_project') or ''
        return request.render('website_project.liff_project_page_plain', {
            'liff_id': liff_id,
        })
    
    @http.route(['/website/project/<string:line_uid>'], type='http', auth='public', website=True, csrf=False)
    def website_project(self, line_uid, **kwargs):
       
        try:
            page = int(kwargs.get('page') or 1)
        except Exception:
            page = 1
        q = (kwargs.get('q') or '').strip()
        limit = 20
        offset = (page - 1) * limit

        # --- หา user จาก line_uid ---
        Users = request.env['res.users'].sudo()
        user = Users.search([('line_uid', '=', line_uid)], limit=1)

        if not user:
            # ไม่พบผู้ใช้จาก line_uid ที่ส่งมา — แสดงหน้าเปล่าพร้อมข้อความ
            return request.render('website_project.website_project_page_html', {
                'project': request.env['project.project'],  # empty recordset
                'total': 0,
                'page': 1,
                'page_count': 1,
                'prev_page': False,
                'next_page': False,
                'q': q,
                'warning': "ไม่พบบัญชีผู้ใช้จาก LINE UID ที่ระบุ กรุณาลงทะเบียนก่อน หรือเปิดลิงก์จากใน LINE อีกครั้ง",
            })

        
        user_id = user.id
        company_id = user.company_id.id or request.website.company_id.id

        domain = [
            ('user_id', '=', user_id),
            ('company_id', '=', company_id),         
        ]


        if q:
            domain += ['|', '|',
                       ('name', 'ilike', q)]

        project = request.env['project.project'].sudo()
        total = project.search_count(domain)
        projects = project.search(
            domain,
            limit=limit,
            offset=offset,
            order='date_start desc, id desc'
        )

        page_count = max(1, int(ceil(total / float(limit))))
        prev_page = page - 1 if page > 1 else False
        next_page = page + 1 if page < page_count else False

        return request.render('website_project.prject_page_html', {
            'projects': projects,
            'total': total,
            'page': page,
            'page_count': page_count,
            'prev_page': prev_page,
            'next_page': next_page,
            'q': q,
            'login_user': user,
            'line_uid': line_uid,
        })