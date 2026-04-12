from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.schemas.phone_country import normalize_phone
from src.schemas.user import PortalUser, UpdateProfileRequest


def to_portal(user: User) -> PortalUser:
    return PortalUser(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        country=user.country,
        phone=user.phone,
        national_id=user.national_id,
        points_balance=user.points_balance,
        membership_tier=user.membership_tier,
        reservation_count=user.reservation_count,
        account_verified=user.account_verified,
    )


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def get_me(self, user: User) -> PortalUser:
        return to_portal(user)

    def update_profile(self, user: User, body: UpdateProfileRequest) -> PortalUser:
        data = body.model_dump(exclude_unset=True)
        phone = data.pop("phone", None)
        country = data.pop("country", None)

        for field, value in data.items():
            setattr(user, field, value)

        if country is not None and phone is None:
            raise HTTPException(
                status_code=422,
                detail="phone is required when changing country",
            )

        if phone is not None or country is not None:
            eff_country = country if country is not None else user.country
            eff_phone = phone if phone is not None else user.phone
            user.phone = normalize_phone(eff_country, eff_phone)
            if country is not None:
                user.country = country

        self.users.update(user)
        self.db.commit()
        self.db.refresh(user)
        return to_portal(user)
