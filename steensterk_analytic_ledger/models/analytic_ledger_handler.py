# -*- coding: utf-8 -*-
import json
from collections import defaultdict
from odoo import models, _


class SteensterkAnalyticLedgerReportHandler(models.AbstractModel):
    _name = 'steensterk.analytic.ledger.report.handler'
    _inherit = 'account.general.ledger.report.handler'
    _description = 'Analytic General Ledger Report Handler'

    def _custom_options_initializer(self, report, options, previous_options):
        super()._custom_options_initializer(report, options, previous_options)
        selected = previous_options.get('ledger_account_ids', []) if previous_options else []
        options['ledger_account_ids'] = [int(account_id) for account_id in selected if str(account_id).isdigit()]
        options['filter_ledger_accounts'] = True
        # The inherited CSV exporter writes directly from SQL and would omit analytic detail.
        options['buttons'] = [button for button in options['buttons'] if button.get('action_param') != 'generate_csv_export']

    def _report_custom_engine_general_ledger(self, expressions, options, date_scope, current_groupby, next_groupby, offset=0, limit=None, warnings=None):
        result = super()._report_custom_engine_general_ledger(expressions, options, date_scope, current_groupby, next_groupby, offset=offset, limit=limit, warnings=warnings)
        if isinstance(result, list):
            for _key, values in result:
                values['analytic_amount'] = 0.0
        elif isinstance(result, dict):
            result['analytic_amount'] = 0.0
        return result

    def _analytic_detail_lines(self, report, options, lines):
        """Add display-only analytic sublines. Never change debit, credit or balance."""
        aml_ids = set()
        aml_by_line = {}
        for line in lines:
            try:
                markup, model, res_id = report._parse_line_id(line['id'])[-1]
                if model is None and markup == {'groupby': 'id_with_accumulated_balance'} and not str(res_id).startswith('balance_line_'):
                    aml_id = int(json.loads(res_id)[1])
                    aml_ids.add(aml_id)
                    aml_by_line[line['id']] = aml_id
            except (ValueError, TypeError, IndexError, KeyError, json.JSONDecodeError):
                continue
        if not aml_ids:
            return lines
        amls = {aml.id: aml for aml in self.env['account.move.line'].browse(list(aml_ids)).exists()}
        analytic_ids = set()
        for aml in amls.values():
            for key in (aml.analytic_distribution or {}):
                analytic_ids.update(int(x) for x in str(key).split(',') if x.strip().isdigit())
        analytics = {a.id: a for a in self.env['account.analytic.account'].browse(list(analytic_ids)).exists()}
        output = []
        for line in lines:
            output.append(line)
            aml = amls.get(aml_by_line.get(line['id']))
            if not aml or not aml.analytic_distribution:
                continue
            seq = 0
            # Combined keys represent one allocation across multiple analytic plans.
            for key, percent in sorted(aml.analytic_distribution.items()):
                for token in str(key).split(','):
                    if not token.strip().isdigit():
                        continue
                    analytic = analytics.get(int(token))
                    if not analytic:
                        continue
                    seq += 1
                    amount = aml.balance * float(percent) / 100.0
                    name = '%s: %s (%s%%)' % (analytic.plan_id.name, analytic.name, format(float(percent), 'g'))
                    columns = []
                    for col in line['columns']:
                        if col['expression_label'] == 'analytic_amount':
                            columns.append(report._build_column_dict(amount, col, options))
                        elif col['expression_label'] in ('date', 'partner_name'):
                            # Preserve the parent's date and partner for Excel pivot tables.
                            columns.append(dict(col))
                        else:
                            columns.append({**col, 'name': '', 'no_format': None, 'is_zero': True})
                    output.append({
                        'id': report._get_generic_line_id('account.analytic.account', analytic.id, markup='analytic_%s_%s' % (aml.id, seq), parent_line_id=line['id']),
                        'name': name,
                        'columns': columns,
                        'level': line.get('level', 2) + 1,
                        'parent_id': line['id'],
                        'unfoldable': False,
                        'unfolded': False,
                        'class': 'text-muted',
                    })
        return output

    def _custom_line_postprocessor(self, report, options, lines):
        # Odoo's original GL postprocessor hardcodes the original report line XML ID.
        # For this independent report, run its implementation and restore its total line.
        result = super()._custom_line_postprocessor(report, options, lines)
        if result and not any(report._parse_line_id(line['id'])[-1][0] == 'total' for line in result):
            root = next((line for line in lines if report._parse_line_id(line['id'])[-1][1] == 'account.report.line'), None)
            if root and not self.env.company.totals_below_sections:
                result.append({'id': report._get_generic_line_id(None, None, 'total'), 'name': _('Total General Ledger'), 'columns': root['columns'], 'level': 1})
        return self._analytic_detail_lines(report, options, result)

    def _report_expand_unfoldable_line_with_groupby(self, line_dict_id, groupby, options, progress, offset, unfold_all_batch_data=None):
        result = super()._report_expand_unfoldable_line_with_groupby(line_dict_id, groupby, options, progress, offset, unfold_all_batch_data=unfold_all_batch_data)
        if groupby == 'id_with_accumulated_balance':
            report = self.env['account.report'].browse(options['report_id'])
            result['lines'] = self._analytic_detail_lines(report, options, result['lines'])
        return result
