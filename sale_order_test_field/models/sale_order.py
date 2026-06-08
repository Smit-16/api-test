# -*- coding: utf-8 -*-
from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    test = fields.Char(
        string='Test',
        help='Test field added to sale order'
    )
