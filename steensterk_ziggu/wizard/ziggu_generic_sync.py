# -*- coding: utf-8 -*-

import logging
from datetime import datetime
import time

import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ZigguGenericSync(models.AbstractModel):
    _name = "ziggu.generic.sync"
    _description = "Generic Ziggu Sync"

    def _ziggu_headers(self):
        token = self.env["ir.config_parameter"].sudo().get_param("ziggu.access_token")
        if not token:
            raise ValueError("Geen Ziggu access token ingesteld.")
        client_id = self.env["ir.config_parameter"].sudo().get_param("ziggu.client_id")
        if not client_id:
            raise ValueError("Geen Ziggu client id ingesteld.")
        return {
            "ziggu-integration-token": token,
            "ziggu-integration-client-id": client_id,
            "Accept": "application/json; version=1",
        }

    def _ziggu_base_url(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("ziggu.base_url")
        if not base_url:
            raise ValueError("Geen Ziggu base URL ingesteld.")
        return base_url.rstrip("/")

    def _fetch_records(self, endpoint):
        records = []
        url = "%s/%s" % (self._ziggu_base_url(), endpoint.strip("/"))
        page = 1

        while url:
            response = requests.get(url, headers=self._ziggu_headers(), timeout=30, verify=False)
            response.raise_for_status()
            payload = response.json()
            records += payload.get("data", [])

            next_url = payload.get("next_page_url")
            if next_url:
                url = next_url
                continue

            meta = payload.get("meta") or {}
            total_pages = meta.get("total_pages") or 0
            current_page = meta.get("current_page") or page
            if total_pages and current_page < total_pages:
                page = current_page + 1
                separator = "&" if "?" in url else "?"
                base_no_page = url.split("?", 1)[0]
                url = "%s%spage=%s" % (base_no_page, separator, page)
            else:
                url = False

        return records

    def _parse_datetime(self, value):
        if not value:
            return False
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
        return value

    def _parse_date(self, value):
        if not value:
            return False
        if isinstance(value, str):
            return value[:10]
        return value

    def _resolve_many2one(self, model_name, ziggu_id):
        if not ziggu_id:
            return False
        rec = self.env[model_name].sudo().search([("ziggu_id", "=", str(ziggu_id))], limit=1)
        return rec.id or False

    def _convert_value(self, model, field_name, value, relation_model=False):
        if value in (None, ""):
            return False
        field = model._fields.get(field_name)
        if not field:
            return False
        if field.type == "many2one":
            return self._resolve_many2one(relation_model or field.comodel_name, value)
        if field.type == "datetime":
            return self._parse_datetime(value)
        if field.type == "date":
            return self._parse_date(value)
        return value

    def _prepare_vals(self, model_name, record, mapping):
        model = self.env[model_name].sudo()
        attributes = record.get("attributes") or {}
        vals = {
            "ziggu_id": str(record.get("id")),
        }
        if "ziggu_type" in model._fields:
            vals["ziggu_type"] = record.get("type")

        for ziggu_field, target in mapping.items():
            if isinstance(target, tuple):
                field_name, relation_model = target
            else:
                field_name, relation_model = target, False
            if field_name not in model._fields:
                continue
            vals[field_name] = self._convert_value(model, field_name, attributes.get(ziggu_field), relation_model)

        if "name" in model._fields and not vals.get("name"):
            vals["name"] = attributes.get("name") or attributes.get("title") or attributes.get("filename") or attributes.get("subject") or str(record.get("id"))

        return vals

    @api.model
    def sync_endpoint(self, endpoint, model_name, mapping):
        Model = self.env[model_name].sudo()
        created = updated = 0

        for record in self._fetch_records(endpoint):
            if not record.get("id"):
                continue
            vals = self._prepare_vals(model_name, record, mapping)
            existing = Model.search([("ziggu_id", "=", str(record["id"]))], limit=1)
            if existing:
                existing.write(vals)
                updated += 1
            else:
                Model.create(vals)
                created += 1

        _logger.info("Ziggu sync %s -> %s klaar: %s aangemaakt, %s bijgewerkt", endpoint, model_name, created, updated)
        return {"created": created, "updated": updated}

    def _send_record(self, method, endpoint, payload):
        url = "%s/%s" % (
            self._ziggu_base_url(),
            endpoint.strip("/")
        )

        for attempt in range(5):
            response = requests.request(
                method,
                url,
                headers=self._ziggu_headers(),
                json=payload,
                timeout=30,
                verify=False,
            )

            if response.status_code != 429:
                break

            retry_after = int(response.headers.get("Retry-After", 5))

            _logger.warning(
                "Ziggu rate limit hit, waiting %s seconds",
                retry_after,
            )

            time.sleep(retry_after)

        response.raise_for_status()

        if response.content:
            return response.json()

        return {}
