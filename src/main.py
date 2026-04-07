import json

from src.core.logging_config import configure_logging

configure_logging()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.core.exceptions import CybersourceCaptureContextError
from src.middleware.normalize_path import NormalizePathMiddleware
from src.middleware.request_context import RequestContextMiddleware
from src.routes.payment import router as payment_router
from src.routes.reservation import router as reservation_router

app = FastAPI()


@app.exception_handler(CybersourceCaptureContextError)
async def cybersource_capture_context_handler(
    _request,
    exc: CybersourceCaptureContextError,
):
    try:
        upstream = json.loads(exc.body)
    except json.JSONDecodeError:
        upstream = {"raw": exc.body}
    return JSONResponse(
        status_code=502,
        content={
            "detail": "Failed to obtain payment session from CyberSource",
            "upstream_status": exc.upstream_status,
            "upstream": upstream,
        },
    )

# CORS primero; RequestContext después queda más externo y corre primero (request ID en toda la petición).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestContextMiddleware)
# Último en registrarse = más externo: normaliza //ruta antes de routing/CORS/request-id.
app.add_middleware(NormalizePathMiddleware)

app.include_router(reservation_router)
app.include_router(payment_router)