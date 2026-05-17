# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Steensterk Ziggu API Module',
    'category': 'Base',
    'summary': 'Steensterk Ziggu Module',
    'description': "",
    'author': 'Wim Audenaert',
    'version': '19.0.9.9.9',
    'depends': [
        'base','project','project_enterprise'
    ],
    'data': [
        'security/ir.model.access.csv',
        "views/res_config_settings_view.xml",
        "views/res_partner_view.xml",
        "views/project_project_view.xml",
        "data/cron.xml",
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
    'license': 'OEEL-1',
}
