# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.exceptions import AccessError


class StockLot(models.Model):
    _inherit = 'stock.lot'

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        """Override copy method to restrict duplication."""
        if not self.env.user.has_group('base.group_system'):
            raise AccessError(
                'Only users with Administration/Settings access rights '
                'can duplicate Lot/Serial Numbers.'
            )
        return super(StockLot, self).copy(default=default)
