# custom_addons/ziggu_partner_sync/models/ziggu_sync.py
import logging
import requests

from odoo import api, models
from datetime import datetime

_logger = logging.getLogger(__name__)


class ZigguProjectsSync(models.AbstractModel):
    _name = "ziggu.projects.sync"
    _description = "Sync Ziggu projects to Odoo projects"

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

    def _fetch_ziggu_projects(self):
        contacts = []
        url = f"{self._ziggu_base_url()}/projects"
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

    def _prepare_project_vals(self, proj):
        attributes = proj.get("attributes")

        country_id = False
        address_country = attributes.get("address_country") or ""
        if address_country:
            country_id = self.env['res.country'].search([('code_alpha3','=',address_country)])[0].id

        currency_id = False
        currency = attributes.get("currency") or ""
        if currency:
            currency_id = self.env['res.currency'].search([('name','=',currency)])[0].id

        created_at = attributes.get("created_at")
        upgraded_at = attributes.get("updated_at")

        return {
            "ziggu_id": proj["id"],
            "name": attributes.get("name"),
            "ziggu_address_city": attributes.get("address_city"),
            "ziggu_country_id": country_id,
            "ziggu_address_number": attributes.get("address_number"),
            "ziggu_address_street": attributes.get("address_street"),
            "ziggu_address_zip": attributes.get("address_zip"),
            "ziggu_delivery_date_actual": attributes.get("delivery_date_actual"),
            "ziggu_delivery_date_contractual": attributes.get("delivery_date_contractual"),
            "ziggu_description": attributes.get("description_html"),
            "ziggu_is_template": attributes.get("is_template"),
            "ziggu_measurement": attributes.get("measurement"),
            "ziggu_picture_login_url": attributes.get("picture_login_url"),
            "ziggu_quotity_total": attributes.get("quotity_total"),
            "ziggu_skip_building": attributes.get("skip_building"),
            "ziggu_skip_lot": attributes.get("skip_lot"),
            "ziggu_skip_phase": attributes.get("skip_phase"),
            "ziggu_start_date": attributes.get("start_date"),
            "ziggu_status": attributes.get("status"),
            "ziggu_timezone": attributes.get("timezone"),
            "ziggu_units_active_count": attributes.get("units_active_count"),
            "ziggu_units_count_max": attributes.get("units_count_max"),
            "ziggu_vat_percentage": attributes.get("vat_percentage"),
            "ziggu_website_url": attributes.get("website_url"),
            "ziggu_created_at": datetime.fromisoformat(created_at.replace('Z', '+00:00')).replace(tzinfo=None),
            "ziggu_updated_at": datetime.fromisoformat(upgraded_at.replace('Z', '+00:00')).replace(tzinfo=None),
            "ziggu_currency_id": currency_id,
        }


    def _get_project_template(self):
        ICP = self.env["ir.config_parameter"].sudo()
        template_id = ICP.get_param("ziggu.project_template_id")
        template = self.env["project.project"].sudo()

        if template_id:
            try:
                template = template.browse(int(template_id)).exists()
            except (TypeError, ValueError):
                template = self.env["project.project"].sudo()

        if not template:
            template = self.env["project.project"].sudo().search([
                ("name", "=", "Project Template Steensterk")
            ], limit=1)

        return template

    def _create_project_from_template(self, vals):
        template = self._get_project_template()
        if template:
            return template.copy(default=vals)
        return self.env["project.project"].sudo().create(vals)

    @api.model
    def sync_projects_from_ziggu(self):
        Project = self.env["project.project"].sudo()
        projects = self._fetch_ziggu_projects()

        created = 0
        updated = 0

        for proj in projects:
            if not proj.get("id"):
                continue

            ziggu_id = str(proj["id"])
            vals = self._prepare_project_vals(proj)

            if 'name' in vals and vals['name']:
                project_rec = Project.search([("ziggu_id", "=", ziggu_id)], limit=1)

                if project_rec:
                    project_rec.write(vals)
                    updated += 1
                else:
                    new_project = self._create_project_from_template(vals)
                    new_project.is_template = False 
                    created += 1

        _logger.info(
            "Ziggu projects sync klaar: %s aangemaakt, %s bijgewerkt",
            created,
            updated,
        )

        return {
            "created": created,
            "updated": updated,
        }
