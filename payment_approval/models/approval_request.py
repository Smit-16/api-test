# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    payment_id = fields.Many2one(
        'account.payment',
        string='Payment',
        readonly=True
    )

    def action_approve(self, approver=None):
        res = super(ApprovalRequest, self).action_approve(approver=approver)
        for request in self:
            if request.request_status == 'approved' and request.payment_id:
                if request.payment_id.state == 'draft':
                    request.payment_id.with_context(skip_approval=True).action_post()
        return res

    def action_refuse(self, approver=None):
        res = super(ApprovalRequest, self).action_refuse(approver=approver)
        for request in self:
            if request.payment_id and request.payment_id.state == 'draft':
                request.payment_id.message_post(
                    body='Payment approval request was refused.',
                    message_type='notification'
                )
        return res
