from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    new_total = fields.Float(
        string='New Total',
        compute='_compute_new_total',
        store=True, # Set to True to store the computed value in the database, allowing search/grouping
        help="Computed total amount for the sale order (e.g., amount_total * 1.05)"
    )

    @api.depends('amount_total')
    def _compute_new_total(self):
        for order in self:
            # The requirement mentioned 'total_amount'. In standard Odoo 'sale.order',
            # the field representing the total amount is 'amount_total'.
            # We'll compute new_total as amount_total multiplied by a factor (e.g., 1.05).
            order.new_total = order.amount_total * 1.05
