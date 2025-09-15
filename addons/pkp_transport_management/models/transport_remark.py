# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import pycompat
from tempfile import TemporaryFile
from datetime import datetime, timedelta, date
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from collections import Counter
from odoo.tools.misc import file_open, unquote, ustr, SKIPPED_ELEMENT_TYPES
from xlrd import open_workbook
import xlrd
import datetime
import calendar
import collections
import base64
import copy
import io
import os
import csv
import sys
from re import sub
from decimal import Decimal


class TransportRemark(models.Model):
    _name = "transport.remark"
    _description = "Transport Remark"
    
    name = fields.Char(string="Name", required=True,)
    code = fields.Char(string="Code", required=False,)
