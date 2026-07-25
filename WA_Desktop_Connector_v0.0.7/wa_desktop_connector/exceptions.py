class ConnectorError(RuntimeError):
    """Base error raised for expected connector failures."""


class CommandError(ConnectorError):
    """Raised when a protocol command is unsupported or invalid."""


class OdooClientError(ConnectorError):
    """Raised when Odoo metadata cannot be retrieved or validated."""


class DownloadError(ConnectorError):
    """Raised when a remote document cannot be downloaded safely."""
