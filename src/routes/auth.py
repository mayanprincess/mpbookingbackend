from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from src.core.deps import get_current_user
from src.core.limiter import limiter
from src.db.session import get_db
from src.models.user import User
from src.schemas.user import AuthResponse, LoginRequest, PortalUser, RegisterRequest
from src.services.auth_service import AuthService
from src.services.user_service import to_portal

router = APIRouter(prefix="/auth", tags=["Auth"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post("/register", response_model=AuthResponse, status_code=201)
@limiter.limit("10/minute")
async def register(
    request: Request,
    body: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    return service.register(body)


@router.post("/login", response_model=AuthResponse)
@limiter.limit("20/minute")
async def login(
    request: Request,
    body: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    return service.login(body)


@router.get("/me", response_model=PortalUser)
async def get_me(current_user: User = Depends(get_current_user)) -> PortalUser:
    return to_portal(current_user)


@router.post("/logout", status_code=204)
async def logout() -> Response:
    return Response(status_code=204)
