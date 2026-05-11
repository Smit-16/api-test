# -*- coding: utf-8 -*-
{
    'name': 'Stock No Merge Transfer',
    'version': '17.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Create separate internal transfers for each receipt without merging',
    'description': """
        Stock No Merge Transfer
        =======================
        * Adds 'Not Allow Merge' field on Operation Types
        * Creates separate internal transfer for each receipt when enabled
        * Prevents merging quantities into existing transfers
        * Useful for 2-step inbound operations requiring separate tracking
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': ['stock'],
    'data': [
        'views/stock_picking_type_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
