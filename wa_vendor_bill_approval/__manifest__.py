{
    "name": "Vendor Bill Approval",
    "summary": "Configurable multi-level approval for vendor bills",
    "version": "19.0.1.1.0",
    "category": "Accounting/Accounting",
    "author": "Wim Audenaert",
    "license": "LGPL-3",
    "depends": ["account", "mail", "approvals"],
    "data": [
        "security/vendor_bill_approval_security.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/account_move_views.xml",
        "views/vendor_bill_approval_dashboard_views.xml",
        "wizards/vendor_bill_reject_wizard_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "wa_vendor_bill_approval/static/src/js/approval_dashboard_card.js",
            "wa_vendor_bill_approval/static/src/scss/approval_dashboard_card.scss",
        ],
    },
    "installable": True,
    "application": False,
}