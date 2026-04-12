"""Usuario del portal (alineado con PortalUser del frontend)."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from src.db.base import Base


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserTier(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid7()),
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(255))
    country: Mapped[str] = mapped_column(String(2), default="HN")
    phone: Mapped[str] = mapped_column(String(64))
    national_id: Mapped[str] = mapped_column(String(128))

    points_balance: Mapped[int] = mapped_column(Integer, default=0)
    membership_tier: Mapped[str] = mapped_column(String(32), default=UserTier.BRONZE.value)
    reservation_count: Mapped[int] = mapped_column(Integer, default=0)
    account_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utc_now,
        onupdate=_utc_now,
    )
