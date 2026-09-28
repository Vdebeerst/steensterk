# custom_addons/ziggu_partner_sync/models/ziggu_sync.py
import logging
import requests

from odoo import api, models
from datetime import datetime

_logger = logging.getLogger(__name__)


class ZigguCustomersSync(models.AbstractModel):
    _name = "ziggu.customers.sync"
    _description = "Sync Ziggu customers to Odoo partners"

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
        url = f"{self._ziggu_base_url()}/customers"
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
        first_name = attributes.get("first_name") or ""
        last_name = attributes.get("last_name") or ""
        company_name = attributes.get("company_name")

        company_address_street = attributes.get("company_address_street") or ""
        company_address_number = attributes.get("company_address_number") or ""

        name = company_name or f"{first_name} {last_name}".strip() or attributes.get("email_address")
        street = f"{company_address_street} {company_address_number}"

        country_id = False
        company_address_country = attributes.get("company_address_country") or ""
        if company_address_country:
            country_id = self.env['res.country'].search([('code_alpha3','=',company_address_country)])[0].id

        created_at = attributes.get("created_at")
        upgraded_at = attributes.get("updated_at")

        return {
            "name": name,
            "email": attributes.get("email_address"),
            "phone": attributes.get("phone_landline"),
            "ziggu_mobile": attributes.get("phone_mobile"),
            "street": street,
            "zip": attributes.get("company_address_zip"),
            "city": attributes.get("company_address_city"),
            "country_id": country_id,
            "is_company": True, 
            "ziggu_id": contact["id"],
            "vat": attributes.get("company_vat"),
            "ziggu_note": attributes.get("internal_note_html"),
            "ziggu_type": "Customers",
            "ziggu_created_at": datetime.fromisoformat(created_at.replace('Z', '+00:00')).replace(tzinfo=None),
            "ziggu_updated_at": datetime.fromisoformat(upgraded_at.replace('Z', '+00:00')).replace(tzinfo=None),
        }

    @api.model
    def sync_customers_from_ziggu(self):
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
                partner = Partner.search([("ziggu_id", "=", ziggu_id),("ziggu_type","=","Customers")], limit=1)

                if partner:
                    partner.write(vals)
                    updated += 1
                else:
                    Partner.create(vals)
                    created += 1

        _logger.info(
            "Ziggu customers sync klaar: %s aangemaakt, %s bijgewerkt",
            created,
            updated,
        )

        return {
            "created": created,
            "updated": updated,
        }
