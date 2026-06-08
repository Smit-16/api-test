# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('first_approved', 'First Approved'),
        ('pending_cfo', 'Pending CFO Approval'),
        ('fully_approved', 'Fully Approved'),
    ], string='Approval Status', default='draft', tracking=True, copy=False)
    
    first_approver_id = fields.Many2one('res.users', string='First Approver', readonly=True, copy=False, tracking=True)
    first_approval_date = fields.Datetime(string='First Approval Date', readonly=True, copy=False, tracking=True)
    
    cfo_approver_id = fields.Many2one('res.users', string='CFO Approver', readonly=True, copy=False, tracking=True)
    cfo_approval_date = fields.Datetime(string='CFO Approval Date', readonly=True, copy=False, tracking=True)
    
    is_locked = fields.Boolean(string='Locked for Editing', default=False, copy=False, tracking=True)
    approval_required = fields.Boolean(string='Approval Required', compute='_compute_approval_required', store=True)
    cfo_approval_required = fields.Boolean(string='CFO Approval Required', compute='_compute_cfo_approval_required', store=True)
    
    can_first_approve = fields.Boolean(compute='_compute_approval_rights')
    can_cfo_approve = fields.Boolean(compute='_compute_approval_rights')
    can_request_edit = fields.Boolean(compute='_compute_approval_rights')
    
    edit_request_ids = fields.One2many('invoice.edit.request', 'invoice_id', string='Edit Requests')
    pending_edit_request = fields.Boolean(compute='_compute_pending_edit_request', string='Has Pending Edit Request')
    
    @api.depends('company_id')
    def _compute_approval_required(self):
        for move in self:
            if move.move_type in ['in_invoice', 'in_refund'] and move.company_id:
                config = self.env['invoice.approval.config'].search([
                    ('company_id', '=', move.company_id.id)
                ], limit=1)
                move.approval_required = config.approval_enabled if config else False
            else:
                move.approval_required = False
    
    @api.depends('amount_total', 'company_id', 'approval_required')
    def _compute_cfo_approval_required(self):
        for move in self:
            if move.approval_required and move.move_type in ['in_invoice', 'in_refund']:
                config = self.env['invoice.approval.config'].search([
                    ('company_id', '=', move.company_id.id)
                ], limit=1)
                if config:
                    move.cfo_approval_required = move.amount_total > config.cfo_approval_threshold
                else:
                    move.cfo_approval_required = False
            else:
                move.cfo_approval_required = False
    
    @api.depends('approval_state', 'company_id')
    def _compute_approval_rights(self):
        for move in self:
            config = self.env['invoice.approval.config'].search([
                ('company_id', '=', move.company_id.id)
            ], limit=1)
            
            if config:
                move.can_first_approve = self.env.user in config.first_approver_ids and move.approval_state == 'draft'
                move.can_cfo_approve = self.env.user in config.cfo_approver_ids and move.approval_state == 'pending_cfo'
                move.can_request_edit = move.is_locked and not move.pending_edit_request
            else:
                move.can_first_approve = False
                move.can_cfo_approve = False
                move.can_request_edit = False
    
    @api.depends('edit_request_ids.state')
    def _compute_pending_edit_request(self):
        for move in self:
            move.pending_edit_request = any(req.state == 'pending' for req in move.edit_request_ids)
    
    def write(self, vals):
        for move in self:
            if move.is_locked and not self.env.context.get('force_write'):
                restricted_fields = ['partner_id', 'invoice_date', 'invoice_line_ids', 'amount_total']
                if any(field in vals for field in restricted_fields):
                    raise UserError(_('This invoice is locked. Please submit an edit request to modify it.'))
        
        if 'invoice_line_ids' in vals or 'partner_id' in vals:
            for move in self:
                if move.approval_state in ['first_approved', 'pending_cfo', 'fully_approved']:
                    if not self.env.context.get('skip_approval_reset'):
                        vals['approval_state'] = 'draft'
                        vals['first_approver_id'] = False
                        vals['first_approval_date'] = False
                        vals['cfo_approver_id'] = False
                        vals['cfo_approval_date'] = False
                        vals['is_locked'] = False
                        move.message_post(body=_('Invoice modified. Approval process has been reset.'))
        
        return super(AccountMove, self).write(vals)
    
    def action_first_approve(self):
        self.ensure_one()
        if not self.can_first_approve:
            raise UserError(_('You are not authorized to approve this invoice.'))
        
        if self.approval_state != 'draft':
            raise UserError(_('Invoice must be in draft state for first approval.'))
        
        self.write({
            'first_approver_id': self.env.user.id,
            'first_approval_date': fields.Datetime.now(),
            'approval_state': 'pending_cfo' if self.cfo_approval_required else 'fully_approved',
            'is_locked': True,
        })
        
        body = _('First approval completed by %s') % self.env.user.name
        self.message_post(body=body, subject='Invoice First Approved')
        
        if self.cfo_approval_required:
            self._notify_cfo_approvers()
        else:
            self._notify_fully_approved()
        
        return True
    
    def action_cfo_approve(self):
        self.ensure_one()
        if not self.can_cfo_approve:
            raise UserError(_('You are not authorized for CFO approval.'))
        
        if self.approval_state != 'pending_cfo':
            raise UserError(_('Invoice must be pending CFO approval.'))
        
        self.write({
            'cfo_approver_id': self.env.user.id,
            'cfo_approval_date': fields.Datetime.now(),
            'approval_state': 'fully_approved',
        })
        
        body = _('CFO approval completed by %s') % self.env.user.name
        self.message_post(body=body, subject='Invoice CFO Approved')
        
        self._notify_fully_approved()
        
        config = self.env['invoice.approval.config'].search([('company_id', '=', self.company_id.id)], limit=1)
        if config and config.auto_post_after_approval:
            self.action_post()
        
        return True
    
    def action_request_edit(self):
        self.ensure_one()
        return {
            'name': _('Request Edit'),
            'type': 'ir.actions.act_window',
            'res_model': 'invoice.edit.request',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_invoice_id': self.id},
        }
    
    def action_post(self):
        for move in self:
            if move.approval_required and move.move_type in ['in_invoice', 'in_refund']:
                if move.approval_state not in ['first_approved', 'fully_approved']:
                    raise UserError(_('Invoice must be approved before posting. Current status: %s') % dict(move._fields['approval_state'].selection).get(move.approval_state))
                
                if move.cfo_approval_required and move.approval_state != 'fully_approved':
                    raise UserError(_('This invoice requires CFO approval before posting.'))
        
        return super(AccountMove, self).action_post()
    
    def _notify_cfo_approvers(self):
        config = self.env['invoice.approval.config'].search([('company_id', '=', self.company_id.id)], limit=1)
        if config and config.cfo_approver_ids:
            template = self.env.ref('invoice_approval_flow.email_template_cfo_approval_request', raise_if_not_found=False)
            if template:
                for approver in config.cfo_approver_ids:
                    template.with_context(approver=approver).send_mail(self.id, force_send=True)
    
    def _notify_fully_approved(self):
        template = self.env.ref('invoice_approval_flow.email_template_invoice_approved', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
