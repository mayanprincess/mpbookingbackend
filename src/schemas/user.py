"""Esquemas del portal de usuario (JSON en snake_case)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from src.schemas.phone_country import CountryCode, normalize_phone


class PortalUser(BaseModel):
    """Modelo alineado con el store del frontend SvelteKit."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    first_name: str
    last_name: str
    country: str
    phone: str
    national_id: str
    points_balance: int
    membership_tier: str
    reservation_count: int
    account_verified: bool


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    first_name: str = Field(..., min_length=1, max_length=255)
    last_name: str = Field(..., min_length=1, max_length=255)
    country: CountryCode
    phone: str = Field(..., min_length=1, max_length=64)
    national_id: str = Field(..., min_length=3, max_length=128)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("first_name", "last_name", "national_id")
    @classmethod
    def strip_nonempty(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("must not be empty")
        return s

    @model_validator(mode="after")
    def normalize_phone_for_country(self) -> RegisterRequest:
        self.phone = normalize_phone(self.country, self.phone)
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=72)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class UpdateProfileRequest(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=255)
    last_name: str | None = Field(None, min_length=1, max_length=255)
    country: CountryCode | None = None
    phone: str | None = Field(None, min_length=1, max_length=64)
    national_id: str | None = Field(None, min_length=3, max_length=128)

    @field_validator("first_name", "last_name", "national_id")
    @classmethod
    def strip_if_set(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        if not s:
            raise ValueError("must not be empty")
        return s


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: PortalUser
