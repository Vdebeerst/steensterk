# custom_addons/ziggu_partner_sync/models/ziggu_sync.py
import logging
import requests

from odoo import api, models
from datetime import datetime

_logger = logging.getLogger(__name__)


class ZigguCompaniesSync(models.AbstractModel):
    _name = "ziggu.companies.sync"
    _description = "Sync Ziggu companies to Odoo partners"

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

    def _fetch_ziggu_contacts(self):
        contacts = []
        url = f"{self._ziggu_base_url()}/companies"
        print ('url:', url)
        print ('headers,', self._ziggu_headers())

        while url:
            response = requests.get(
                url,
                headers=self._ziggu_headers(),
                timeout=30,
                verify=False,
            )
            print(response.status_code)
            print(response.text)
            print(response.url)
            response.raise_for_status()
            payload = response.json()

            contacts += payload.get("data", [])
            url = payload.get("next_page_url")

        return contacts

    def _prepare_partner_vals(self, contact):
        attributes = contact.get("attributes")

        address_street = attributes.get("address_street") or ""
        address_number = attributes.get("address_number") or ""

        name = attributes.get("name")
        street = f"{address_street} {address_number}"

        country_id = False
        address_country = attributes.get("address_country") or ""
        if address_country:
            country_id = self.env['res.country'].search([('code_alpha3','=',address_country)])[0].id

        created_at = attributes.get("created_at")
        upgraded_at = attributes.get("updated_at")

        return {
            "name": name,
            "street": street,
            "zip": attributes.get("address_zip"),
            "city": attributes.get("address_city"),
            "country_id": country_id,
            "is_company": True, 
            "ziggu_id": contact["id"],
            "ziggu_type": "Companies",
            "ziggu_created_at": datetime.fromisoformat(created_at.replace('Z', '+00:00')).replace(tzinfo=None),
            "ziggu_updated_at": datetime.fromisoformat(upgraded_at.replace('Z', '+00:00')).replace(tzinfo=None),
        }

    @api.model
    def sync_companies_from_ziggu(self):
        Partner = self.env["res.partner"].sudo()
        contacts = self._fetch_ziggu_contacts()

        created = 0
        updated = 0

        for contact in contacts:
            if not contact.get("id"):
                continue

            ziggu_id = str(contact["id"])
            vals = self._prepare_partner_vals(contact)

            if 'name' in vals and vals['name']:
                partner = Partner.search([("ziggu_id", "=", ziggu_id),("ziggu_type","=","Companies")], limit=1)

                if partner:
                    partner.write(vals)
                    updated += 1
                else:
                    Partner.create(vals)
                    created += 1

        _logger.info(
            "Ziggu companies sync klaar: %s aangemaakt, %s bijgewerkt",
            created,
            updated,
        )

        return {
            "created": created,
            "updated": updated,
        }
