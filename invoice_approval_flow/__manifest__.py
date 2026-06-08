# -*- coding: utf-8 -*-
{
    'name': 'Invoice Approval Flow',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Multi-level invoice approval workflow with edit control and audit trail',
    'description': """
        Invoice Approval Flow
        ======================
        * Multi-level approval system for vendor bills
        * Threshold-based CFO approval
        * Invoice locking after approval
        * Edit request management
        * Comprehensive audit trail
        * Email notifications
        * Approval dashboard
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['account', 'mail'],
    'data': [
        'security/invoice_approval_security.xml',
        'security/ir.model.access.csv',
        'data/mail_template_data.xml',
        'views/account_move_views.xml',
        'views/res_company_views.xml',
        'views/invoice_approval_config_views.xml',
        'views/invoice_edit_request_views.xml',
        'views/approval_dashboard_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
