# -*- coding: utf-8 -*-
{
    'name': 'Product Group',
    'version': '17.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Product Group categorization for better product management',
    'description': """
        Product Group Module
        ====================
        * Create and manage product groups
        * Assign product groups to products
        * Group by and pivot view support
        * Visible across sales, inventory, purchase, accounting
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['product', 'sale_management', 'purchase', 'stock', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_group_views.xml',
        'views/product_template_views.xml',
        'views/product_product_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
