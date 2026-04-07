"""Middleware: asigna X-Request-ID y propaga el ID en el contexto de logging."""

from __future__ import annotations

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.core.request_context import request_id_ctx

logger = logging.getLogger(__name__)

_HEADER = "X-Request-ID"


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        incoming = request.headers.get(_HEADER)
        request_id = incoming.strip() if incoming and incoming.strip() else str(uuid.uuid4())

        token = request_id_ctx.set(request_id)
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.exception(
                "%s %s failed after %.2fms",
                request.method,
                request.url.path,
                duration_ms,
            )
            raise
        else:
            duration_ms = (time.perf_counter() - start) * 1000
            response.headers[_HEADER] = request_id
            logger.info(
                "%s %s -> %s (%.2fms)",
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
            )
            return response
        finally:
            request_id_ctx.reset(token)
