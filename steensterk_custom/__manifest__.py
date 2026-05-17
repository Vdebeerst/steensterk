# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Steensterk Custom Module',
    'category': 'Base',
    'summary': 'Steensterk Custom Module',
    'description': "",
    'author': 'Wim Audenaert',
    'version': '19.0.9.9.9',
    'depends': [
        'base','project','project_enterprise'
    ],
    'data': [
        'security/ir.model.access.csv',
        "views/project_task_view.xml",
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
    'license': 'OEEL-1',
}
