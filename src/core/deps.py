"""Dependencias FastAPI: usuario JWT opcional u obligatorio."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.core.security import get_sub_from_token
from src.db.session import get_db
from src.models.user import User
from src.repositories.user_repository import UserRepository

_optional_bearer = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    db: Session = Depends(get_db),
    creds: HTTPAuthorizationCredentials | None = Depends(_optional_bearer),
) -> User | None:
    if creds is None:
        return None
    try:
        uid = get_sub_from_token(creds.credentials)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    repo = UserRepository(db)
    user = repo.get(uid)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


async def get_current_user(
    user: User | None = Depends(get_current_user_optional),
) -> User:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user
