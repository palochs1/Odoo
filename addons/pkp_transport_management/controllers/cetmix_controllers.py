###################################################################################
# 
#    Copyright (C) Cetmix OÜ
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

# import json

# from odoo import http
# from odoo.http import request
# from odoo.tools.safe_eval import safe_eval, time

# from odoo.addons.http_routing.models.ir_http import slugify
# from odoo.addons.web.controllers.main import ReportController


# class CxReportController(ReportController):
    # @http.route(
        # [
            # "/report/<converter>/<reportname>",
            # "/report/<converter>/<reportname>/<docids>",
        # ],
        # type="http",
        # auth="user",
        # website=True,
    # )
    # def report_routes(self, reportname, docids=None, converter=None, **data):
        # """
        # Overwrite method to open PDF report in new window
        # """
        # if converter == "pdf":
            # report = request.env["ir.actions.report"]._get_report_from_name(reportname)
            # context = dict(request.env.context)
            # if docids:
                # docids = [int(i) for i in docids.split(",")]
            # if data.get("options"):
                # data.update(json.loads(data.pop("options")))
            # if data.get("context"):
                # data["context"] = json.loads(data["context"])
                # context.update(data["context"])
            # filepart = "report"
            # if docids:
                # if len(docids) > 1:
                    # filepart = "{} (x{})".format(
                        # request.env["ir.model"]
                        # .sudo()
                        # .search([("model", "=", report.model)])
                        # .name,
                        # str(len(docids)),
                    # )
                # elif len(docids) == 1:
                    # obj = request.env[report.model].browse(docids)
                    # if report.print_report_name:
                        # filepart = safe_eval(
                            # report.print_report_name, {"object": obj, "time": time}
                        # )
            # pdf = report.with_context(context)._render_qweb_pdf(docids, data=data)[0]
            # pdfhttpheaders = [
                # ("Content-Type", "application/pdf"),
                # ("Content-Length", len(pdf)),
                # ("Content-Disposition", 'filename="%s.pdf"' % slugify(filepart)),
            # ]
            # res = request.make_response(pdf, headers=pdfhttpheaders)
        # else:
            # res = super().report_routes(
                # reportname, docids=docids, converter=converter, **data
            # )
        # return res




# from odoo import http
# from odoo.http import content_disposition, request
# import json

# class CustomReportController(http.Controller):

    # @http.route('/report/download', type='http', auth='user')
    # def report_download(self, data, token):
        # requestcontent = json.loads(data)
        # url, report_type = requestcontent[0], requestcontent[1]
        # response = self._get_report_response(url, report_type)
        # if 'Content-Disposition' in response.headers:
            # del response.headers['Content-Disposition']
        
        # filename = "report.pdf"
        # response.headers['Content-Disposition'] = content_disposition(filename)
        
        # return response
        

import base64
import copy
import datetime
import functools
import hashlib
import io
import itertools
import json
import logging
import operator
import os
import re
import sys
import tempfile
import unicodedata
from collections import OrderedDict, defaultdict

import babel.messages.pofile
import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from lxml import etree, html
from markupsafe import Markup
from werkzeug.urls import url_encode, url_decode, iri_to_uri

import odoo
import odoo.modules.registry
from odoo.api import call_kw
from odoo.addons.base.models.ir_qweb import render as qweb_render
from odoo.modules import get_resource_path, module
from odoo.tools import html_escape, pycompat, ustr, apply_inheritance_specs, lazy_property, osutil
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools.translate import _
from odoo.tools.misc import str2bool, xlsxwriter, file_open, file_path
from odoo.tools.safe_eval import safe_eval, time
from odoo import http
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception
from odoo.exceptions import AccessError, UserError, AccessDenied
from odoo.models import check_method_name
from odoo.service import db, security


class ReportController(http.Controller):

    #------------------------------------------------------
    # Report controllers
    #------------------------------------------------------
    @http.route([
        '/report/<converter>/<reportname>',
        '/report/<converter>/<reportname>/<docids>',
    ], type='http', auth='user', website=True)
    def report_routes(self, reportname, docids=None, converter=None, **data):
        report = request.env['ir.actions.report']._get_report_from_name(reportname)
        context = dict(request.env.context)

        if docids:
            docids = [int(i) for i in docids.split(',')]
        if data.get('options'):
            data.update(json.loads(data.pop('options')))
        if data.get('context'):
            data['context'] = json.loads(data['context'])
            context.update(data['context'])
        if report.model == 'ins.general.ledger' or report.model == 'ins.partner.ageing' or report.model == 'ins.partner.ledger' or report.model == 'ins.trial.balance':
            if not context.get("allowed_company_ids"):
                context.update({'allowed_company_ids':request.env.user.company_id.ids})
            if not context.get("active_model"):
                context.update({'active_model':report.model})
            if not context.get("active_id"):
                context.update({'active_id': docids[0]})
            if not context.get("active_ids"):
                context.update({'active_ids': docids})
            if not context.get("landscape"):
                context.update({'landscape': True})
            data.update({'context': context})
                
        if converter == 'html':
            html = report.with_context(context)._render_qweb_html(docids, data=data)[0]
            return request.make_response(html)
        elif converter == 'pdf':
            pdf = report.with_context(context)._render_qweb_pdf(docids, data=data)[0]
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
            return request.make_response(pdf, headers=pdfhttpheaders)
        elif converter == 'text':
            text = report.with_context(context)._render_qweb_text(docids, data=data)[0]
            texthttpheaders = [('Content-Type', 'text/plain'), ('Content-Length', len(text))]
            return request.make_response(text, headers=texthttpheaders)
        else:
            raise werkzeug.exceptions.HTTPException(description='Converter %s not implemented.' % converter)

    #------------------------------------------------------
    # Misc. route utils
    #------------------------------------------------------
    @http.route(['/report/barcode', '/report/barcode/<type>/<path:value>'], type='http', auth="public")
    def report_barcode(self, type, value, **kwargs):
        """Contoller able to render barcode images thanks to reportlab.
        Samples::

            <img t-att-src="'/report/barcode/QR/%s' % o.name"/>
            <img t-att-src="'/report/barcode/?type=%s&amp;value=%s&amp;width=%s&amp;height=%s' %
                ('QR', o.name, 200, 200)"/>

        :param type: Accepted types: 'Codabar', 'Code11', 'Code128', 'EAN13', 'EAN8', 'Extended39',
        'Extended93', 'FIM', 'I2of5', 'MSI', 'POSTNET', 'QR', 'Standard39', 'Standard93',
        'UPCA', 'USPS_4State'
        :param width: Pixel width of the barcode
        :param height: Pixel height of the barcode
        :param humanreadable: Accepted values: 0 (default) or 1. 1 will insert the readable value
        at the bottom of the output image
        :param quiet: Accepted values: 0 (default) or 1. 1 will display white
        margins on left and right.
        :param mask: The mask code to be used when rendering this QR-code.
                     Masks allow adding elements on top of the generated image,
                     such as the Swiss cross in the center of QR-bill codes.
        :param barLevel: QR code Error Correction Levels. Default is 'L'.
        ref: https://hg.reportlab.com/hg-public/reportlab/file/830157489e00/src/reportlab/graphics/barcode/qr.py#l101
        """
        try:
            barcode = request.env['ir.actions.report'].barcode(type, value, **kwargs)
        except (ValueError, AttributeError):
            raise werkzeug.exceptions.HTTPException(description='Cannot convert into barcode.')

        return request.make_response(barcode, headers=[('Content-Type', 'image/png')])

    @http.route(['/report/download'], type='http', auth="user")
    def report_download(self, data, context=None):
        """This function is used by 'action_manager_report.js' in order to trigger the download of
        a pdf/controller report.

        :param data: a javascript array JSON.stringified containg report internal url ([0]) and
        type [1]
        :returns: Response with an attachment header

        """
        requestcontent = json.loads(data)
        url, type = requestcontent[0], requestcontent[1]
        reportname = '???'
        try:
            if type in ['qweb-pdf', 'qweb-text']:
                converter = 'pdf' if type == 'qweb-pdf' else 'text'
                extension = 'pdf' if type == 'qweb-pdf' else 'txt'

                pattern = '/report/pdf/' if type == 'qweb-pdf' else '/report/text/'
                reportname = url.split(pattern)[1].split('?')[0]

                docids = None
                if '/' in reportname:
                    reportname, docids = reportname.split('/')

                if docids:
                    # Generic report:
                    response = self.report_routes(reportname, docids=docids, converter=converter, context=context)
                else:
                    # Particular report:
                    data = dict(url_decode(url.split('?')[1]).items())  # decoding the args represented in JSON
                    if 'context' in data:
                        context, data_context = json.loads(context or '{}'), json.loads(data.pop('context'))
                        context = json.dumps({**context, **data_context})
                    response = self.report_routes(reportname, converter=converter, context=context, **data)

                report = request.env['ir.actions.report']._get_report_from_name(reportname)
                filename = "%s.%s" % (report.name, extension)

                if docids:
                    ids = [int(x) for x in docids.split(",")]
                    obj = request.env[report.model].browse(ids)
                    if report.print_report_name and not len(obj) > 1:
                        report_name = safe_eval(report.print_report_name, {'object': obj, 'time': time})
                        filename = "%s.%s" % (report_name, extension)
                response.headers.add('Content-Disposition', content_disposition(filename))
                return response
            else:
                return
        except Exception as e:
            _logger.exception("Error while generating report %s", reportname)
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': "Odoo Server Error",
                'data': se
            }
            res = request.make_response(html_escape(json.dumps(error)))
            raise werkzeug.exceptions.InternalServerError(response=res) from e

    @http.route(['/report/check_wkhtmltopdf'], type='json', auth="user")
    def check_wkhtmltopdf(self):
        return request.env['ir.actions.report'].get_wkhtmltopdf_state()
