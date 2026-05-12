# -*- coding: utf-8 -*-
{
    'name': 'Duplicate Button Restriction',
    'version': '17.0.1.0.0',
    'category': 'Technical',
    'summary': 'Restrict duplicate button for Apps and Lot/Serial Numbers',
    'description': """
        Duplicate Button Restriction
        ============================
        * Restricts duplicate button for Installation Apps (ir.module.module)
        * Restricts duplicate button for Lot/Serial Numbers (stock.lot)
        * Only users with Administration/Settings access can duplicate
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': ['base', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/ir_module_views.xml',
        'views/stock_lot_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
