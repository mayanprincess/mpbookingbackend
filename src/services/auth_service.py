import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.core.security import create_access_token, hash_password, verify_password
from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.schemas.user import AuthResponse, LoginRequest, RegisterRequest
from src.services.user_service import to_portal

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def register(self, body: RegisterRequest) -> AuthResponse:
        if self.users.get_by_email(body.email):
            raise HTTPException(status_code=409, detail="Email already registered")

        user = User(
            email=body.email,
            password_hash=hash_password(body.password),
            first_name=body.first_name,
            last_name=body.last_name,
            country=body.country,
            phone=body.phone,
            national_id=body.national_id,
        )
        self.users.add(user)
        self.db.commit()
        self.db.refresh(user)

        token = create_access_token(
            subject=user.id,
            extra_claims={"email": user.email},
        )
        logger.info("User registered id=%s", user.id)
        return AuthResponse(access_token=token, user=to_portal(user))

    def login(self, body: LoginRequest) -> AuthResponse:
        user = self.users.get_by_email(body.email)
        if user is None or not verify_password(body.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = create_access_token(
            subject=user.id,
            extra_claims={"email": user.email},
        )
        return AuthResponse(access_token=token, user=to_portal(user))
