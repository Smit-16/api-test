# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_group_id = fields.Many2one(
        'product.group',
        string='Product Group',
        index=True,
        tracking=True,
        help='Assign this product to a specific product group for better categorization'
    )
    product_group_code = fields.Char(related='product_group_id.code', string='Group Code', store=True, readonly=True)
