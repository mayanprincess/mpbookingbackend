"""Respuestas 422 con más contexto para clientes (front / integraciones)."""

from __future__ import annotations

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    errors = exc.errors()
    ct = (request.headers.get("content-type") or "").lower()
    hints: list[str] = []

    if request.method in ("POST", "PUT", "PATCH"):
        if not ct.startswith("application/json"):
            hints.append(
                "Envía el header Content-Type: application/json y un objeto JSON en el cuerpo "
                "(no form-data vacío ni texto plano sin JSON)."
            )

    for e in errors:
        loc = e.get("loc") or ()
        loc_list = [str(x) for x in (loc if isinstance(loc, (list, tuple)) else (loc,))]
        typ = e.get("type")
        if "query" in loc_list and "body" in loc_list:
            hints.append(
                "El endpoint espera un JSON en el cuerpo del POST (Content-Type: application/json), "
                "no parámetros de query. Si el cliente envía el payload como query string o el cuerpo "
                "está vacío, fallará la validación."
            )
        if typ == "missing":
            if loc_list == ["body"] or (len(loc_list) >= 1 and loc_list[0] == "body"):
                hints.append(
                    "Falta el cuerpo JSON o está vacío. Ej. login: "
                    '{"email":"user@dominio.com","password":"..."} '
                    "o register con firstName/lastName/country/phone/nationalId."
                )
            if "body" in loc_list and len(loc_list) > 1:
                hints.append(
                    "Algún campo obligatorio falta en el JSON. Revisa login (email, password) "
                    "o registro (email, password, first_name|firstName, last_name|lastName, "
                    "country HN|US, phone, national_id|nationalId)."
                )

    if not hints:
        hints.append(
            "Revisa nombres de campos (snake_case o camelCase), tipos y campos obligatorios. "
            "Ver OpenAPI en /docs."
        )

    deduped: list[str] = []
    seen: set[str] = set()
    for h in hints:
        if h not in seen:
            seen.add(h)
            deduped.append(h)

    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "La petición no cumple el esquema esperado.",
            "path": request.url.path,
            "method": request.method,
            "content_type_received": request.headers.get("content-type"),
            "hints": deduped,
            "detail": errors,
        },
    )
