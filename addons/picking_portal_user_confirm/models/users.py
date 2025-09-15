# -*- coding: utf-8 -*-
import secrets
from odoo import api, fields, models, _
import logging
import requests

_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = 'res.users'

    # Public token & confirmation fields
    access_token = fields.Char('Security Token', copy=False, index=True)
    line_uid = fields.Char(string="Line Uid", copy=False, readonly=True)

    portal_confirm_link = fields.Char(string="Confirm URL", copy=False)
    type_users = fields.Selection([
        ('project', 'Project User'),    
        ('transport', 'Transport User'),
    ], string="Type User", default=None, copy=False, index=True)    

    def _portal_ensure_token(self):
        """Ensure each picking has an access_token (like portal.mixin behavior)."""
        for rec in self.sudo():
            if not rec.access_token:
                rec.access_token = secrets.token_urlsafe(24)

    def get_portal_url(self):
        """Return the public confirm URL path for this picking."""
        self.ensure_one()
        self._portal_ensure_token()
        return f"/user/confirm"
        # return f"/user/confirm/{self.access_token}"


    def action_generate_portal_link(self):
        for rec in self:
            rec._portal_ensure_token()
            base = rec.env['ir.config_parameter'].sudo().get_param('web.base.url') or ''
            path = rec.get_portal_url()
            db = rec.env.cr.dbname
            sep = '&' if '?' in path else '?'
            link = f"{base}{path}{sep}db={db}"
            rec.sudo().write({'portal_confirm_link': link})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {'title': 'Confirm link generated',
                       'message': 'ลิงก์ถูกสร้างและบันทึกในฟิลด์ Confirm URL แล้ว',
                       'type': 'success', 'sticky': False}
        }
    
    # @api.sudo.model_create_multi
    # def create(self, vals_list):
    #     raise ValueError('--------------------------------------------')
    #     records = super().create(vals_list)
    #     # เลือกเฉพาะเรคคอร์ดที่มีค่าครบเพื่อยิงหลัง commit
    #     to_send = records.filtered(lambda r: r.line_uid and r.type_users)
    #     if to_send:
    #         # ยิงหลัง commit เพื่อกัน rollback
    #         self.env.cr.postcommit.add(lambda: to_send._set_richmenu_call())
    #     return records
    
    # def write(self, vals):
    #     # เก็บค่าเดิมไว้เทียบการเปลี่ยนแปลง
    #     _logger.warning("245426437468655634354146657698")
    #     before = {rec.id: (rec.line_uid, rec.type_users) for rec in self}
    #     res = super().write(vals)

    #     # เฉพาะเคสที่ line_uid หรือ type_user เปลี่ยนจริง ๆ เท่านั้น
    #     if any(k in vals for k in ('line_uid', 'type_users')):
    #         changed = self.filtered(lambda r: before.get(r.id) != (r.line_uid, r.type_users))
    #         changed = changed.filtered(lambda r: r.line_uid and r.type_users)
    #         if changed:
    #             self.env.cr.postcommit.add(lambda: changed._set_richmenu_call())
    #     return res
    
    
    def _set_richmenu_call(self):
        """งานจริงในการยิง API (เรียกหลัง commit เท่านั้น)"""
        _logger.warning("...............................")
        ICP = self.env['ir.config_parameter'].sudo()
        token = ICP.get_param('line_token')
        if not token:
            _logger.warning("LINE token not configured; skip richmenu assign.")
            return
        headers = {
            'Authorization': f'Bearer {token}'
        }

        for rec in self:
            if not (rec.line_uid and rec.type_users):
                continue
            rm = (ICP.get_param('line_richmenu_project') if rec.type_users == 'project'
                  else ICP.get_param('line_richmenu_transport') if rec.type_users == 'transport'
                  else None)
            if not rm:
                _logger.warning("Richmenu id missing for type_user=%s; skip (rec id %s)", rec.type_user, rec.id)
                continue

            url = f"https://api.line.me/v2/bot/user/{rec.line_uid}/richmenu/{rm}"
            try:
                _logger.warning("----------------------")
                resp = requests.post(url, headers=headers, timeout=10)
                _logger.warning("===============================")
                if resp.status_code in (200, 204):
                    _logger.info("Set richmenu %s for user %s (%s) OK", rm, rec.id, rec.line_uid)
                else:
                    _logger.error("Set richmenu FAILED for user %s (%s): %s %s",
                                  rec.id, rec.line_uid, resp.status_code, resp.text)
            except Exception as e:
                _logger.exception("Exception setting richmenu for user %s (%s): %s",
                                  rec.id, rec.line_uid, e)

    