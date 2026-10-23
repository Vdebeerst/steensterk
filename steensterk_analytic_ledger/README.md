# Analytic General Ledger — Odoo 19 Enterprise

Independent account.report based on the standard General Ledger handler. Adds display-only analytic lines for each `account.move.line.analytic_distribution` entry and an Analytic Amount column. Does not modify posted entries or the standard General Ledger report.

## Install

Copy this directory to an Odoo 19 custom addons path, update the Apps list, install **Analytic General Ledger**. Open **Analytic General Ledger** from the top-level menu. Requires Enterprise `account_reports`.

## Testing in staging (required)

1. Verify the report loads and displays standard account lines and opening balances.
2. Expand a journal item with two analytic plans, a 60/40 distribution and a combined analytic key.
3. Confirm debit/credit/balance totals are unchanged, and analytic values appear only in Analytic Amount.
4. Check individual expand, unfold all, load more, PDF and XLSX exports.
5. Check negative amounts, refunds, multi-company and foreign currency if relevant.

## Scope and limitations

- Analytic values are calculated from the original journal item balance in its company currency, not from the report's currency-converted amount. In multi-company reports with differing company currencies, analytic amounts require an additional conversion implementation.
- The standard General Ledger CSV exporter is disabled because it bypasses report display lines. PDF and XLSX use the normal reporting pipeline.
- Report handler interfaces are internal Odoo Enterprise APIs; test after upgrades.
- This is a first implementation based on the supplied Odoo 19 GL XML and Python handler; it has not been executed against a running Odoo 19 instance.

## Grootboekrekeningenfilter (19.0.1.1.0)
De filter Grootboekrekeningen staat bovenaan het rapport en ondersteunt meerdere rekeningen.
Zonder selectie worden alle rekeningen getoond. De selectie wordt toegepast op de SQL-rapportquery, inclusief openingssaldo en exports.
Na module-upgrade de browserassets herladen (Ctrl+F5). Test eerst in staging.

## Analytische boekingsdatum (19.0.1.2.0)
Iedere analytische onderregel neemt de datumkolom van de oorspronkelijke boekingslijn over, met behoud van de standaard datumrepresentatie voor XLSX/PDF. Daardoor kan Excel per periode groeperen.

Version 19.0.1.3.0: Repeat the source journal item partner on analytic detail rows (screen, PDF and XLSX).
