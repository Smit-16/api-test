# -*- coding: utf-8 -*-
{
    'name': 'Energy Certificate',
    'version': '17.0.1.0.0',
    'category': 'Real Estate',
    'summary': 'Manage energy certificates for buildings and properties',
    'description': """
        Energy Certificate Management
        ==============================
        * Track energy certificates for properties
        * Energy efficiency classifications (A+ to G)
        * Expiry date monitoring and alerts
        * Certificate type management
        * Inspector and issuer tracking
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'mail'],
    'data': [
        'security/energy_certificate_security.xml',
        'security/ir.model.access.csv',
        'data/energy_certificate_data.xml',
        'views/energy_certificate_views.xml',
        'views/energy_certificate_menus.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
