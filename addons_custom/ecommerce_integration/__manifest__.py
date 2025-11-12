# -*- coding: utf-8 -*-
{
    'name': 'E-commerce Integration',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Integration with E-commerce platforms',
    'description': """
        E-commerce Integration Module
        ==============================
        This module provides integration capabilities with various e-commerce platforms.
        
        Features:
        ---------
        * Ready for custom development
        * Extensible architecture
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'sale', 'stock', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/ecommerce_platform_data.xml',
        'data/ecommerce_order_status_data.xml',
        'views/shop_dashboard_action.xml',
        'views/ecommerce_product_views.xml',
        'views/ecommerce_order_views.xml',
        'views/ecommerce_stock_update_views.xml',
        'views/ecommerce_shop_views.xml',
        'views/ecommerce_platform_views.xml',
        'views/ecommerce_shop_menu.xml',
        'views/ecommerce_integration_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ecommerce_integration/static/src/css/ecommerce_shop.css',
            'ecommerce_integration/static/src/js/shop_management_dashboard.js',
            'ecommerce_integration/static/src/xml/shop_management_dashboard.xml',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
