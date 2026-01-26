from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from src.schemas.guest import GuestCreate
from src.services.ptranz_service import PtranzService
from src.schemas.payment import BillingAddress, CreditCardSource, ExtendedData, PtranzSale, ThreeDSecure
from src.repositories.reservation_repository import ReservationRepository
from src.schemas.reservation import ReservationCreate
from src.services.opera_service import OperaService
from src.core.config import settings
from src.models.reservation import Reservation

class PaymentService:
  def __init__(self, db: Session):
    self.db = db
    self.repository = ReservationRepository(db)
    self.reservations = ReservationRepository(db)
    self.ptranz_service = PtranzService(settings)
    self.opera_service = OperaService(settings)

  async def apply_payment(self, spiToken: str):
    response = await self.ptranz_service.apply_payment(spiToken)
    if response.Status:
      reservation = self.repository.get(response.OrderIdentifier)
      if reservation:
        reservationToOpera = ReservationCreate(
          checkIn=reservation.checkIn,
          checkOut=reservation.checkOut,
          roomTypeCode=reservation.roomTypeCode,
          ratePlanCode=reservation.ratePlanCode,
          adults=reservation.adults,
          children=reservation.children,
          amountBeforeTax=reservation.amountBeforeTax,
          promoCode=reservation.promoCode,
          specialRequests=reservation.specialRequests,
          guest=GuestCreate(
            firstName=reservation.guest_first_name,
            lastName=reservation.guest_last_name,
            email=reservation.guest_email,
            phone=reservation.guest_phone,
          )
        )
        operaResponse = await self.opera_service.create_reservation(reservationToOpera)
        reservation.isPaid = True
        reservation.reservationId = operaResponse.reservationId
        reservation.confirmationNumber = operaResponse.confirmationNumber
        self.db.commit()
        self.db.refresh(reservation)
        return RedirectResponse(url=f'{settings.base_api_url}reservation/{reservation.id}')
    return RedirectResponse(url=f'{settings.base_api_url}reservation-failed/{response.OrderIdentifier}')

