# -*- coding: utf-8 -*-
{
    'name': 'Payment Approval Workflow',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Add approval workflow for payment confirmation',
    'description': """
        Payment Approval Workflow
        =========================
        * Payments require approval after confirmation
        * Automatic posting after approval
        * Integration with Approvals app
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': ['account', 'approvals'],
    'data': [
        'security/ir.model.access.csv',
        'data/approval_category_data.xml',
        'views/account_payment_views.xml',
        'views/approval_request_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
