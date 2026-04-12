from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict

from src.schemas.guest import GuestCreate

class Payment(BaseModel):
  cardHolder: str
  cardNumber: str
  cvv: str
  expiryMonth: int
  expiryYear: int

class ReservationResponse(BaseModel):
  Status: bool
  Message: Optional[str] = ''
  reservationId: Optional[str] = None
  confirmationNumber: Optional[str] = None


class ReservationCreate(BaseModel):
    checkIn: str
    checkOut: str
    roomTypeCode: str
    ratePlanCode: str
    adults: int
    children: int
    amountBeforeTax: float
    promoCode: Optional[str] = None
    specialRequests: Optional[str] = None
    guest: GuestCreate
    payment: Optional[Payment] = None

class Reservation(BaseModel):
    id: str
    checkIn: str
    checkOut: str
    roomTypeCode: str
    ratePlanCode: str
    adults: int
    children: int
    amountBeforeTax: float
    promoCode: Optional[str] = None
    specialRequests: Optional[str] = None
    guest: GuestCreate
    
    class Config:
        from_attributes = True


class ReservationOut(BaseModel):
    """Reserva para listados / detalle portal (campos persistidos)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: Optional[str] = None
    checkIn: str
    checkOut: str
    roomTypeCode: str
    ratePlanCode: str
    adults: int
    children: int
    amountBeforeTax: float
    promoCode: str
    specialRequests: str
    guest_first_name: str
    guest_last_name: str
    guest_email: str
    guest_phone: str
    isPaid: bool
    createdAt: datetime
    reservationId: str
    confirmationNumber: str

