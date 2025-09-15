from odoo import http, fields, _
from odoo.http import request
import base64
import logging

_logger = logging.getLogger(__name__)

class WebsiteProjectTask(http.Controller):

    @http.route(['/project/task/confirm/<int:task_id>/<string:line_uid>/<string:pro_id>'], type='http', auth='public', website=True, csrf=False)
    def project_task_confirm_form(self, task_id, line_uid, pro_id, **kw):
        Task = request.env['project.task'].sudo()
        Stage = request.env['project.task.type'].sudo()
        Project = request.env['project.project'].sudo()

        task = Task.sudo().browse(task_id)
        if not task.exists():
            return request.not_found()

        project = Project.sudo().browse(pro_id)
        if not project or not project.exists():
            project = task.project_id

        stages = Stage.sudo().search([('project_ids', 'in', project.id)], order='sequence, id')

        if task.stage_id and task.stage_id not in stages:
            stages |= task.stage_id

        return request.render('website_project.website_project_task_page_confirm', {
            'task': task,
            'project': project,
            'line_uid': (line_uid or '').strip(),
            'stages': stages,
        })


    @http.route(['/project/task/confirm/submit'], type='http', auth='public', csrf=False)
    def delivery_confirm_form_submit(self, **post):
        line_uid = (post.get('line_uid') or '').strip()
        task_id = int(post.get('task', 0))
        pro_id = (post.get('pro_id') or '')
        stage_id = int(post.get('stage_id', 0))

        Task = request.env['project.task'].sudo()
        task = Task.browse(task_id)
        if not task.exists() or not stage_id:
            return request.not_found()

        task.sudo().write({'stage_id': stage_id})
         
        home_url = f"/website/project/task/{line_uid}/{pro_id}"

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
