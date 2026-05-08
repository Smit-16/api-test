from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    new_total = fields.Float(
        string='New Total (10% extra)',
        compute='_compute_new_total',
        store=True,  # Set to True to store the computed value in the database
        readonly=True,
        help="A computed total based on the sale order's total amount, with an additional 10%."
    )

    @api.depends('amount_total')
    def _compute_new_total(self):
        for order in self:
            # Example computation: original total_amount + 10% of total_amount
            order.new_total = order.amount_total * 1.10
