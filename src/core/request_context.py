"""Contexto por petición para correlación de logs (request ID)."""

from __future__ import annotations

import contextvars
import logging

request_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id",
    default=None,
)


class RequestIdFilter(logging.Filter):
    """Inyecta `request_id` en cada registro para el formatter."""

    def filter(self, record: logging.LogRecord) -> bool:
        rid = request_id_ctx.get()
        record.request_id = rid if rid is not None else "-"
        return True


def get_request_id() -> str | None:
    return request_id_ctx.get()
