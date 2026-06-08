# -*- coding: utf-8 -*-
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    invoice_approval_enabled = fields.Boolean(
        string='Enable Invoice Approval Flow',
        default=False,
        help='Enable multi-level approval workflow for vendor bills'
    )
