import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.warning("WA ANALYTIC DISTRIBUTION: PRE-MIGRATE STARTED")

    cr.execute("""
        UPDATE ir_model_fields
        SET company_dependent = FALSE
        WHERE model = 'account.account'
          AND name = 'wa_analytic_distribution'
          AND ttype = 'json'
          AND company_dependent = TRUE
    """)

    _logger.warning(
        "WA ANALYTIC DISTRIBUTION: updated %s field records",
        cr.rowcount,
    )