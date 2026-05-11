# -*- coding: utf-8 -*-
from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _should_bypass_reservation(self, move=None):
        """Override to control transfer merging behavior."""
        result = super(StockMove, self)._should_bypass_reservation(move=move)
        if move and move.picking_type_id.not_allow_merge:
            return True
        return result

    def _search_picking_for_assignation_domain(self):
        """Override to prevent merging when not_allow_merge is enabled."""
        domain = super(StockMove, self)._search_picking_for_assignation_domain()
        if self.picking_type_id.not_allow_merge:
            domain = [('id', '=', False)]
        return domain

    def _assign_picking(self):
        """Override to force new picking creation when not_allow_merge is enabled."""
        moves_with_no_merge = self.filtered(
            lambda m: m.picking_type_id.not_allow_merge and not m.picking_id
        )
        moves_standard = self - moves_with_no_merge
        
        if moves_standard:
            super(StockMove, moves_standard)._assign_picking()
        
        if moves_with_no_merge:
            for move in moves_with_no_merge:
                picking = self.env['stock.picking'].create(
                    move._get_new_picking_values()
                )
                move.write({'picking_id': picking.id})
        
        return True

    def _get_new_picking_values(self):
        """Get values for creating a new picking."""
        values = super(StockMove, self)._get_new_picking_values()
        if self.picking_type_id.not_allow_merge:
            origin = self.origin or self.group_id.name if self.group_id else False
            if origin:
                values['origin'] = origin
        return values
