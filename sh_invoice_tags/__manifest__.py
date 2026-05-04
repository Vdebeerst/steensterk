# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

{
    'name': 'Invoice Tags | Bill Tags | Credit Tags | Debit Note Tags',
    'author': 'Softhealer Technologies',
    'website': 'https://www.softhealer.com',
    'license': 'OPL-1',
    'support': 'support@softhealer.com',
    'version': '0.0.1',
    'category': 'Accounting',
    'summary': """
Invoicing Tags Module, Debit Note Tag App, Credit Note Tags,
Bill Tags, Refund Tags, Journal Items Tag, Journal Entry Tags,
Invoice Analytics Odoo
""",
    'description': """
This module enables the feature to create accounting tags
(invoice, bill, credit note, debit note, refund, journal entry,
journal item) tags. You can change the color of tags as per need.
You can filter invoice records using particular tags.
You can search the records using tags also.
""",
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'security/sh_invoice_tags_groups.xml',
        'views/sh_invoice_tags_views.xml',
        'views/account_move_views.xml',
        'wizard/sh_update_mass_tag_wizard_views.xml',
        'views/res_config_settings_views.xml',
    ],
    "images": ["static/description/background.png", ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': '13',
    'currency': 'EUR',
}
