"""Colapsa barras duplicadas en la ruta (p. ej. POST //reservations -> /reservations)."""

from __future__ import annotations

import re

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class NormalizePathMiddleware(BaseHTTPMiddleware):
    _multi_slash = re.compile(r"/{2,}")

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.scope["type"] == "http":
            path = request.scope.get("path") or ""
            collapsed = self._multi_slash.sub("/", path)
            if collapsed != path:
                request.scope["path"] = collapsed
        return await call_next(request)
