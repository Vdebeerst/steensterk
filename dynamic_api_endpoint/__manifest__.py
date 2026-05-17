{
    'name': 'Dynamic API Endpoints & Webhooks',
    'version': '19.0.1.0.0',
    'category': 'Technical',
    'summary': 'Create dynamic REST API endpoints and webhooks for Odoo integration',
    'description': """
Dynamic API Endpoints & Webhooks
=================================
- Create dynamic REST API endpoints (GET/POST/PUT/DELETE) for any Odoo model
- Configure field-level access control per endpoint
- API key authentication
- Webhook triggers on create/write/unlink events
- Request/response logging
- Rate limiting support
    """,
    'author': 'Developers Pro',
    'company': 'Developers Pro',
    'depends': ['base', 'mail'],
    'data': [
        'security/api_security.xml',
        'security/ir.model.access.csv',
        'data/api_key_sequence.xml',
        'views/api_endpoint_views.xml',
        'views/api_webhook_views.xml',
        'views/api_log_views.xml',
        'views/api_key_views.xml',
        'views/menu_views.xml',
    ],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'price': 15.00,
    'currency': 'USD',
}
