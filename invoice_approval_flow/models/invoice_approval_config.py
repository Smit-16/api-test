# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class InvoiceApprovalConfig(models.Model):
    _name = 'invoice.approval.config'
    _description = 'Invoice Approval Configuration'
    _rec_name = 'company_id'

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company, ondelete='cascade')
    approval_enabled = fields.Boolean(string='Enable Approval Flow', default=True)
    
    first_approver_ids = fields.Many2many('res.users', 'invoice_first_approver_rel', 'config_id', 'user_id', string='First Level Approvers', domain=[('share', '=', False)])
    
    cfo_approval_threshold = fields.Monetary(string='CFO Approval Threshold', default=5000000.0, currency_field='currency_id', help='Invoice amount above this value requires CFO approval')
    cfo_approver_ids = fields.Many2many('res.users', 'invoice_cfo_approver_rel', 'config_id', 'user_id', string='CFO Approvers', domain=[('share', '=', False)])
    
    auto_post_after_approval = fields.Boolean(string='Auto Post After Approval', default=False, help='Automatically post invoice after final approval')
    
    edit_request_approver_ids = fields.Many2many('res.users', 'invoice_edit_approver_rel', 'config_id', 'user_id', string='Edit Request Approvers', domain=[('share', '=', False)])
    
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    
    _sql_constraints = [
        ('company_unique', 'unique(company_id)', 'Only one configuration per company is allowed!')
    ]
    
    @api.constrains('cfo_approval_threshold')
    def _check_threshold(self):
        for config in self:
            if config.cfo_approval_threshold < 0:
                raise ValidationError(_('CFO approval threshold must be positive.'))
