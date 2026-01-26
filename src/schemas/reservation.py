from typing import Any, Optional
from pydantic import BaseModel

from src.schemas.guest import GuestCreate

class Payment(BaseModel):
  cardHolder: str
  cardNumber: str
  cvv: str
  expiryMonth: int
  expiryYear: int


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

class ReservationResponse(BaseModel):
    id: str
    reservationId: Optional[str] = None
    confirmationNumber: Optional[str] = None

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

