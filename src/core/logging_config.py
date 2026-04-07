"""Configuración central de logging para la aplicación y Uvicorn."""

from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any

from src.core.request_context import RequestIdFilter


class _JsonFormatter(logging.Formatter):
    """Una línea JSON por evento (útil en Railway, Datadog, CloudWatch, etc.)."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        rid = getattr(record, "request_id", None)
        if rid and rid != "-":
            payload["request_id"] = rid
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def _parse_level(name: str) -> int:
    level = getattr(logging, name.upper(), None)
    if isinstance(level, int):
        return level
    return logging.INFO


def configure_logging() -> None:
    """
    Idempotente: si el root ya tiene handlers, no reconfigura (útil en tests/reload).
    """
    root = logging.getLogger()
    if root.handlers:
        return

    level_name = os.environ.get("LOG_LEVEL", "INFO")
    level = _parse_level(level_name)
    use_json = os.environ.get("LOG_JSON", "").lower() in ("1", "true", "yes")

    fmt_text = (
        "%(asctime)s | %(levelname)-8s | %(request_id)s | %(name)s | %(message)s"
    )
    datefmt = "%Y-%m-%dT%H:%M:%S"

    req_filter = RequestIdFilter()
    handler = logging.StreamHandler(sys.stdout)

    if use_json:
        handler.setFormatter(_JsonFormatter(datefmt=datefmt))
    else:
        handler.setFormatter(logging.Formatter(fmt=fmt_text, datefmt=datefmt))

    handler.addFilter(req_filter)
    root.addHandler(handler)
    root.setLevel(level)

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(name).setLevel(level)

    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
