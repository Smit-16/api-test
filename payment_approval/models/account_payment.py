# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    approval_request_id = fields.Many2one(
        'approval.request',
        string='Approval Request',
        readonly=True,
        copy=False
    )
    approval_state = fields.Selection(
        related='approval_request_id.request_status',
        string='Approval Status',
        store=True
    )
    require_approval = fields.Boolean(
        string='Require Approval',
        default=True,
        help='If checked, payment will require approval before posting'
    )

    def action_post(self):
        for payment in self:
            if payment.require_approval and not payment.approval_request_id:
                payment._create_approval_request()
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Approval Required'),
                        'message': _('An approval request has been created. The payment will be posted after approval.'),
                        'type': 'info',
                        'sticky': False,
                    }
                }
            elif payment.require_approval and payment.approval_state != 'approved':
                raise UserError(_('Payment must be approved before posting.'))
        return super(AccountPayment, self).action_post()

    def _create_approval_request(self):
        self.ensure_one()
        category = self.env.ref('payment_approval.approval_category_payment', raise_if_not_found=False)
        if not category:
            category = self.env['approval.category'].search([('name', '=', 'Payment Approval')], limit=1)
        if not category:
            raise UserError(_('Payment Approval category not found. Please check module installation.'))

        approval_request = self.env['approval.request'].create({
            'name': _('Payment Approval: %s') % self.name,
            'category_id': category.id,
            'request_owner_id': self.env.user.id,
            'amount': self.amount,
            'reason': _('Payment to %s for amount %s %s') % (
                self.partner_id.name,
                self.amount,
                self.currency_id.name
            ),
            'payment_id': self.id,
        })
        self.approval_request_id = approval_request.id
        approval_request.action_confirm()
        return approval_request

    def action_view_approval_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Approval Request'),
            'res_model': 'approval.request',
            'res_id': self.approval_request_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
