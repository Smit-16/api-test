# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class InvoiceEditRequest(models.Model):
    _name = 'invoice.edit.request'
    _description = 'Invoice Edit Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Request Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    invoice_id = fields.Many2one('account.move', string='Invoice', required=True, ondelete='cascade', domain=[('move_type', 'in', ['in_invoice', 'in_refund'])])
    requester_id = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user, readonly=True)
    request_date = fields.Datetime(string='Request Date', default=fields.Datetime.now, readonly=True)
    reason = fields.Text(string='Reason for Edit', required=True, tracking=True)
    
    state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='pending', tracking=True)
    
    approver_id = fields.Many2one('res.users', string='Approved/Rejected By', readonly=True, tracking=True)
    approval_date = fields.Datetime(string='Approval Date', readonly=True, tracking=True)
    approval_notes = fields.Text(string='Approval Notes', tracking=True)
    
    can_approve = fields.Boolean(compute='_compute_can_approve')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('invoice.edit.request') or _('New')
        
        request = super(InvoiceEditRequest, self).create(vals)
        request._notify_approvers()
        return request
    
    @api.depends('state')
    def _compute_can_approve(self):
        for request in self:
            config = self.env['invoice.approval.config'].search([
                ('company_id', '=', request.invoice_id.company_id.id)
            ], limit=1)
            request.can_approve = config and self.env.user in config.edit_request_approver_ids and request.state == 'pending'
    
    def action_approve(self):
        self.ensure_one()
        if not self.can_approve:
            raise UserError(_('You are not authorized to approve this edit request.'))
        
        self.write({
            'state': 'approved',
            'approver_id': self.env.user.id,
            'approval_date': fields.Datetime.now(),
        })
        
        self.invoice_id.with_context(force_write=True).write({'is_locked': False})
        
        self.message_post(body=_('Edit request approved by %s') % self.env.user.name, subject='Edit Request Approved')
        self._notify_requester()
        
        return True
    
    def action_reject(self):
        self.ensure_one()
        if not self.can_approve:
            raise UserError(_('You are not authorized to reject this edit request.'))
        
        return {
            'name': _('Reject Edit Request'),
            'type': 'ir.actions.act_window',
            'res_model': 'invoice.edit.request.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_request_id': self.id},
        }
    
    def _notify_approvers(self):
        config = self.env['invoice.approval.config'].search([
            ('company_id', '=', self.invoice_id.company_id.id)
        ], limit=1)
        if config and config.edit_request_approver_ids:
            template = self.env.ref('invoice_approval_flow.email_template_edit_request', raise_if_not_found=False)
            if template:
                for approver in config.edit_request_approver_ids:
                    template.with_context(approver=approver).send_mail(self.id, force_send=True)
    
    def _notify_requester(self):
        template = self.env.ref('invoice_approval_flow.email_template_edit_request_response', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
