# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_group_id = fields.Many2one(
        'product.group',
        related='product_template_id.product_group_id',
        string='Product Group',
        store=True,
        readonly=False,
        index=True
    )
