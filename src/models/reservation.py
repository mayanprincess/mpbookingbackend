from typing import Any
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String, BINARY
from src.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7
from datetime import datetime


class Reservation(Base):
    __tablename__ = "reservations"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid7())
    )

    checkIn: Mapped[str] = mapped_column(String(255))
    checkOut: Mapped[str] = mapped_column(String(255))
    roomTypeCode: Mapped[str] = mapped_column(String(255))
    ratePlanCode: Mapped[str] = mapped_column(String(255))
    adults: Mapped[int] = mapped_column(Integer)
    children: Mapped[int] = mapped_column(Integer)
    amountBeforeTax: Mapped[float] = mapped_column(Float)
    promoCode: Mapped[str] = mapped_column(String(255), default='')
    specialRequests: Mapped[str] = mapped_column(String(255), default='')
    guest_first_name: Mapped[str] = mapped_column(String(255))
    guest_last_name: Mapped[str] = mapped_column(String(255))
    guest_email: Mapped[str] = mapped_column(String(255))
    guest_phone: Mapped[str] = mapped_column(String(255))
    isPaid: Mapped[bool] = mapped_column(Boolean, default=False)
    createdAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    reservationId: Mapped[str] = mapped_column(String(255), default = '')
    confirmationNumber: Mapped[str] = mapped_column(String(255), default = '')


    @property
    def guest(self) -> dict:
        return {
            "firstName": self.guest_first_name,
            "lastName": self.guest_last_name,
            "email": self.guest_email,
            "phone": self.guest_phone,
        }