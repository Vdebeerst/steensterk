{
    'name': 'Analytic General Ledger',
    'version': '19.0.1.3.0',
    'category': 'Accounting/Accounting',
    'summary': 'Independent general ledger with analytic distribution detail lines',
    'license': 'LGPL-3',
    'depends': ['account_reports', 'analytic'],
    'data': ['data/analytic_ledger_report.xml'],
    'assets': {'web.assets_backend': ['steensterk_analytic_ledger/static/src/account_report/ledger_account_filter.xml']},
    'installable': True,
    'application': False,
}
