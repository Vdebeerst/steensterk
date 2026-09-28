# -*- coding: utf-8 -*-
import base64
import logging

import requests

from odoo import api, models

_logger = logging.getLogger(__name__)


class ZigguDocumentsSync(models.AbstractModel):
    _name = 'ziggu.documents.sync'

    def _enabled(self, key):
        value = self.env['ir.config_parameter'].sudo().get_param(key, 'False')
        return str(value).strip().lower() in ('1', 'true', 'yes', 'y', 'on')

    _description = 'Sync Ziggu documents to ir.attachment and Documents folders'

    def _download_file(self, url):
        if not url:
            return False
        try:
            response = requests.get(url, timeout=60, verify=False)
            response.raise_for_status()
            return base64.b64encode(response.content)
        except Exception as exc:
            _logger.warning('Kon Ziggu document niet downloaden van %s: %s', url, exc)
            return False

    def _get_or_create_document_record(self, attachment, project, folder):
        Document = self.env['documents.document'].sudo()
        existing = Document.search([('attachment_id', '=', attachment.id)], limit=1)
        vals = {
            'name': attachment.name,
            'attachment_id': attachment.id,
            'folder_id': folder.id,
        }
        if 'res_model' in Document._fields:
            vals['res_model'] = 'project.project'
        if 'res_id' in Document._fields:
            vals['res_id'] = project.id
        if existing:
            existing.write(vals)
            return existing
        return Document.create(vals)

    @api.model
    def sync_documents_from_ziggu(self):
        ICP = self.env['ir.config_parameter'].sudo()
        if ICP.get_param('ziggu.get_documents') in ('False', 'false', '0', False, None):
            _logger.info('Ziggu documents import overgeslagen: ziggu.get_documents is niet actief.')
            return {'created': 0, 'updated': 0, 'skipped': True}

        generic = self.env['ziggu.generic.sync']
        Attachment = self.env['ir.attachment'].sudo()
        created = updated = 0

        for record in generic._fetch_records('documents'):
            if not record.get('id'):
                continue
            attributes = record.get('attributes') or {}
            project = False
            if attributes.get('project_id'):
                project = self.env['project.project'].sudo().search([('ziggu_id', '=', str(attributes.get('project_id')))], limit=1)
            if not project:
                _logger.warning('Ziggu document %s overgeslagen: geen project gevonden voor project_id %s', record.get('id'), attributes.get('project_id'))
                continue

            folder = project._get_or_create_ziggu_documents_folder()
            filename = attributes.get('filename') or attributes.get('title') or str(record.get('id'))
            file_url = attributes.get('file_url') or attributes.get('url')
            vals = {
                'ziggu_id': str(record.get('id')),
                'ziggu_type': record.get('type'),
                'name': filename,
                'ziggu_title': attributes.get('title'),
                'ziggu_filename': attributes.get('filename'),
                'ziggu_description': attributes.get('description_html'),
                'ziggu_url': attributes.get('url'),
                'ziggu_file_url': attributes.get('file_url'),
                'ziggu_mime_type': attributes.get('mime_type'),
                'ziggu_file_size': attributes.get('file_size') or 0,
                'ziggu_project_id': project.id,
                'ziggu_building_id': generic._resolve_many2one('ziggu.building', attributes.get('building_id')),
                'ziggu_lot_id': generic._resolve_many2one('ziggu.lot', attributes.get('lot_id')),
                'ziggu_unit_id': generic._resolve_many2one('ziggu.unit', attributes.get('unit_id')),
                'ziggu_attachment_category_id': generic._resolve_many2one('ziggu.attachment.category', attributes.get('attachment_category_id')),
                'ziggu_created_at': generic._parse_datetime(attributes.get('created_at')),
                'ziggu_updated_at': generic._parse_datetime(attributes.get('updated_at')),
                'res_model': 'project.project',
                'res_id': project.id,
                'type': 'binary',
            }
            existing = Attachment.search([('ziggu_id', '=', str(record.get('id')))], limit=1)
            if not existing and file_url:
                datas = self._download_file(file_url)
                if datas:
                    vals['datas'] = datas
            if existing:
                existing.write(vals)
                updated += 1
                attachment = existing
            else:
                attachment = Attachment.create(vals)
                created += 1
            self._get_or_create_document_record(attachment, project, folder)

        _logger.info('Ziggu documents import klaar: %s aangemaakt, %s bijgewerkt', created, updated)
        return {'created': created, 'updated': updated}
