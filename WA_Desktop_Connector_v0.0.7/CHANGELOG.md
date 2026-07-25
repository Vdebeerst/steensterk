# Changelog

## 0.0.7

- Added a real two-step Odoo document flow.
- Added metadata lookup using `server` and `document_id`.
- Added the default metadata endpoint `/wa_desktop_connector/api/document/{document_id}`.
- Added support for custom `metadata_path` and `metadata_url` values.
- Added support for direct JSON and Odoo-style `result` responses.
- Added validation of required metadata fields.
- Added resolution of relative Odoo download URLs.
- Added same-host protection for returned download URLs.
- Added metadata fields to successful command output.
- Preserved direct `download_url` support and preview mode.

## 0.0.6

- Added command dispatch for the `wa://open` action.
- Added real HTTPS document downloading through `download_url`.
- Added optional Bearer authentication through `access_token`.
- Added safe filename handling and a persistent downloads folder.
- Added automatic opening with the default Windows application.
- Added `--download-only` for controlled testing.
- Kept the v0.0.5 preview behaviour when no `download_url` is supplied.
- Prevented access tokens from appearing in command output and normal log entries.
- Added clearer errors for unsupported actions and unsafe URLs.

## 0.0.5

- Preserved Windows `wa://` protocol installation and status checks.
- Added validation and parsing of `wa://` URLs.
- Added configuration creation under `%APPDATA%\WA`.
- Added rotating file logging.
- Added `--show-log`.
- Added clearer error handling and exit codes.
