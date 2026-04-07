"""Excepciones de dominio para integraciones externas."""


class CybersourceCaptureContextError(Exception):
    """Fallo al obtener el JWT de capture-context desde CyberSource."""

    def __init__(self, upstream_status: int, body: str):
        self.upstream_status = upstream_status
        self.body = body
        super().__init__(
            f"CyberSource capture-context failed with HTTP {upstream_status}",
        )
