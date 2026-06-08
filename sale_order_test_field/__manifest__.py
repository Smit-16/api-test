# -*- coding: utf-8 -*-
{
    'name': 'Sale Order Test Field',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Adds a test field to sale.order',
    'description': """
        This module adds a new test field to the sale.order model.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['sale'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
