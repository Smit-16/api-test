# -*- coding: utf-8 -*-
from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    not_allow_merge = fields.Boolean(
        string='Not Allow Merge',
        default=False,
        help="If enabled, system will create separate transfers for each receipt "
             "instead of merging quantities into existing transfers."
    )
