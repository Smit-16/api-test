# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductGroup(models.Model):
    _name = 'product.group'
    _description = 'Product Group'
    _order = 'name'

    name = fields.Char(string='Group Name', required=True, index=True)
    code = fields.Char(string='Code', index=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    parent_id = fields.Many2one('product.group', string='Parent Group', index=True, ondelete='cascade')
    child_ids = fields.One2many('product.group', 'parent_id', string='Child Groups')
    product_count = fields.Integer(string='Product Count', compute='_compute_product_count', store=True)
    color = fields.Integer(string='Color Index')

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Product Group name must be unique!'),
    ]

    @api.depends('name')
    def _compute_product_count(self):
        for group in self:
            group.product_count = self.env['product.template'].search_count([('product_group_id', '=', group.id)])

    def name_get(self):
        result = []
        for record in self:
            if record.code:
                name = f'[{record.code}] {record.name}'
            else:
                name = record.name
            result.append((record.id, name))
        return result

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('code', operator, name)]
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
