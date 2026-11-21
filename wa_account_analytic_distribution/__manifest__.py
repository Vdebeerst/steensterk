{
    'name': 'WA Account Analytic Distribution',
    'version': '19.0.1.0.1',
    'category': 'Accounting/Accounting',
    'summary': 'Company-specific analytic distribution on accounts with journal item update wizard',
    'depends': ['account', 'analytic'],
    'data': ['security/ir.model.access.csv', 'views/account_account_views.xml', 'wizard/analytic_distribution_wizard_views.xml'],
    'license': 'LGPL-3',
    'installable': True,
}
