{
    'name': 'WA Monthly Stock Analytic Transfer',
    'version': '19.0.1.3.0',
    'category': 'Accounting/Accounting',
    'summary': 'Automatically propose analytic distributions and create monthly stock transfers',
    'depends': ['wa_account_analytic_distribution', 'account', 'analytic'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_account_views.xml',
        'wizard/stock_transfer_wizard_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
}
