# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, timedelta


class EnergyCertificate(models.Model):
    _name = 'energy.certificate'
    _description = 'Energy Certificate'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'issue_date desc'

    name = fields.Char(
        string='Certificate Number',
        required=True,
        copy=False,
        index=True,
        tracking=True
    )
    property_name = fields.Char(
        string='Property Name',
        required=True,
        tracking=True
    )
    property_address = fields.Text(
        string='Property Address',
        required=True
    )
    property_type = fields.Selection([
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
        ('mixed', 'Mixed Use')
    ], string='Property Type', required=True, default='residential', tracking=True)
    
    certificate_type = fields.Selection([
        ('construction', 'New Construction'),
        ('existing', 'Existing Building'),
        ('renovation', 'Post-Renovation')
    ], string='Certificate Type', required=True, default='existing', tracking=True)
    
    energy_class = fields.Selection([
        ('a_plus', 'A+'),
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'C'),
        ('d', 'D'),
        ('e', 'E'),
        ('f', 'F'),
        ('g', 'G')
    ], string='Energy Class', required=True, tracking=True)
    
    energy_consumption = fields.Float(
        string='Energy Consumption (kWh/m²/year)',
        help='Annual energy consumption per square meter',
        tracking=True
    )
    co2_emissions = fields.Float(
        string='CO2 Emissions (kg/m²/year)',
        help='Annual CO2 emissions per square meter',
        tracking=True
    )
    
    building_area = fields.Float(
        string='Building Area (m²)',
        required=True
    )
    
    issue_date = fields.Date(
        string='Issue Date',
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    expiry_date = fields.Date(
        string='Expiry Date',
        required=True,
        tracking=True
    )
    validity_period = fields.Integer(
        string='Validity Period (Years)',
        compute='_compute_validity_period',
        store=True
    )
    
    inspector_name = fields.Char(
        string='Inspector Name',
        required=True,
        tracking=True
    )
    inspector_license = fields.Char(
        string='Inspector License Number',
        tracking=True
    )
    inspector_contact = fields.Char(
        string='Inspector Contact'
    )
    
    issuing_authority = fields.Char(
        string='Issuing Authority',
        required=True
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('valid', 'Valid'),
        ('expiring', 'Expiring Soon'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)
    
    days_to_expiry = fields.Integer(
        string='Days to Expiry',
        compute='_compute_days_to_expiry',
        store=True
    )
    
    notes = fields.Text(string='Notes')
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Attachments',
        help='Attach certificate documents'
    )
    
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )
    
    @api.depends('issue_date', 'expiry_date')
    def _compute_validity_period(self):
        for record in self:
            if record.issue_date and record.expiry_date:
                delta = record.expiry_date - record.issue_date
                record.validity_period = delta.days // 365
            else:
                record.validity_period = 0
    
    @api.depends('expiry_date', 'state')
    def _compute_days_to_expiry(self):
        today = date.today()
        for record in self:
            if record.expiry_date and record.state not in ['expired', 'cancelled']:
                delta = record.expiry_date - today
                record.days_to_expiry = delta.days
            else:
                record.days_to_expiry = 0
    
    @api.constrains('issue_date', 'expiry_date')
    def _check_dates(self):
        for record in self:
            if record.expiry_date and record.issue_date:
                if record.expiry_date <= record.issue_date:
                    raise ValidationError('Expiry date must be after issue date!')
    
    @api.constrains('energy_consumption', 'co2_emissions', 'building_area')
    def _check_positive_values(self):
        for record in self:
            if record.energy_consumption < 0:
                raise ValidationError('Energy consumption cannot be negative!')
            if record.co2_emissions < 0:
                raise ValidationError('CO2 emissions cannot be negative!')
            if record.building_area <= 0:
                raise ValidationError('Building area must be greater than zero!')
    
    @api.onchange('issue_date')
    def _onchange_issue_date(self):
        if self.issue_date:
            self.expiry_date = self.issue_date + timedelta(days=3650)
    
    def action_validate(self):
        for record in self:
            record.state = 'valid'
            record.message_post(body='Certificate validated and activated.')
    
    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
            record.active = False
            record.message_post(body='Certificate cancelled.')
    
    def _cron_update_certificate_status(self):
        today = date.today()
        expiring_threshold = today + timedelta(days=90)
        
        expiring_certs = self.search([
            ('state', '=', 'valid'),
            ('expiry_date', '<=', expiring_threshold),
            ('expiry_date', '>', today)
        ])
        expiring_certs.write({'state': 'expiring'})
        
        expired_certs = self.search([
            ('state', 'in', ['valid', 'expiring']),
            ('expiry_date', '<=', today)
        ])
        expired_certs.write({'state': 'expired'})
        
        return True
    
    @api.model
    def create(self, vals):
        certificate = super(EnergyCertificate, self).create(vals)
        certificate.message_post(
            body=f'Energy Certificate created for {certificate.property_name}'
        )
        return certificate
    
    def write(self, vals):
        result = super(EnergyCertificate, self).write(vals)
        if 'energy_class' in vals or 'expiry_date' in vals:
            for record in self:
                record._cron_update_certificate_status()
        return result
    
    def name_get(self):
        result = []
        for record in self:
            name = f'{record.name} - {record.property_name}'
            result.append((record.id, name))
        return result
