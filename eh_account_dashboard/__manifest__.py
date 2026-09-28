# -*- encoding: utf-8 -*-
##############################################################################
#
# ERP Heritage
# Copyright (C) 2026 (https://www.erpheritage.com.au/)
# All implementation work is original. The dashboard composes KPIs
# computed via the suite's existing SQL builder against standard
# Odoo accounting tables. No layout, naming, or template derives
# from any proprietary or third-party Odoo module.
#
##############################################################################
{
 'name': "Financial Dashboard",
 'summary': "Per-company KPI dashboard tying the ERP Heritage suite together. Cash position, receivables aging, payables aging, period P&L, plus optional tiles for pending approvals, active collections cases, and budget variance.",
 'description': """
Financial Dashboard for Odoo 19 Community
===========================================

The single pane of glass that summarises an SMB's financial state in
one screen. Composes KPIs from the suite's existing reporting engine
and surfaces them as styled cards with click-through to the
underlying detail.

Tiles
-----

Always present:

* Cash position. Sum of bank and cash journal closing balances at the
  selected as-of date.
* Receivables. Total open AR and total overdue, plus days overdue on
  the oldest unpaid item.
* Payables. Total open AP and total overdue.
* Period P&L. Revenue, expense, and net for the selected period.

Conditionally present (when the source module is installed):

* Pending approvals. Open approval requests in 'in_review' state for
  the current company. Pulled from eh_account_approval.
* Active collections cases. Open cases in non-resolved stages, with
  total overdue across all cases. Pulled from eh_account_collections.
* Budget variance. Active budgets with at least one line above the
  variance threshold. Pulled from eh_account_budget_pro.

Engineering principles
----------------------

* The dashboard model is a Model (not Transient) so the user can save
  bookmarks to the same record. Computed fields recompute on read so
  the values are always live.
* Every KPI computation is a single SQL pass against the relevant
  table; no nested loops, no per-row ORM access.
* Optional integrations check ir.module.module at compute time and
  return empty values when the source module is not installed. The
  view hides those tiles via 'invisible' attributes that read the
  installation status.

Search keywords
---------------

Accounting, Full Accounting, Full Accounting for Community, Odoo 19
Community accounting, accounting suite, accounting modules, financial
reporting, period close, accounts receivable, accounts payable, journal
entries, double entry bookkeeping.


    """,
 'author': "ERP Heritage",
 'website': "https://www.erpheritage.com.au/",
 'license': 'LGPL-3',
 'category': 'Accounting/Accounting',
 'version': '19.0.1.3.5',
 'depends': [
 'eh_account_base',
 'eh_account_dynamic_reports',
 'account',
 ],
 'data': [
 'security/ir.model.access.csv',
 'security/eh_isolation_rules.xml',
 'views/dashboard_views.xml',
 'data/menus.xml',
 ],
 'assets': {
 'web.assets_backend': [
 'eh_account_dashboard/static/src/dashboard/dashboard.scss',
 'eh_account_dashboard/static/src/dashboard/sparkline.js',
 'eh_account_dashboard/static/src/dashboard/kpi_tile.js',
 'eh_account_dashboard/static/src/dashboard/dashboard.js',
 'eh_account_dashboard/static/src/dashboard/dashboard.xml',
 ],
 },
 'images': ['static/description/banner.png'],
 'installable': True,
 'application': False,
 'auto_install': False,
}
