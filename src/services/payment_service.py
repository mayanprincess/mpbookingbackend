from sqlalchemy.orm import Session
from src.schemas.guest import GuestCreate
from src.schemas.reservation import ReservationCreate, ReservationResponse
from src.services.cybersource_service import CybersourceService
from src.schemas.payment import CybersourceConfirmPaymentRequest, CybersourceValidatePaymentRequest
from src.repositories.reservation_repository import ReservationRepository
from src.services.opera_service import OperaService
from src.core.config import settings

class PaymentService:
  def __init__(self, db: Session):
    self.db = db
    self.repository = ReservationRepository(db)
    self.opera_service = OperaService(settings)
    self.cybersource_service = CybersourceService(settings)

  async def confirm_payment(self, model: CybersourceConfirmPaymentRequest) -> ReservationResponse:
    reservation = self.repository.get(model.ReservationId)

    reservation_data = ReservationCreate(
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
      ),
    )
    response = await self.opera_service.create_reservation(reservation_data)

    reservation.isPaid = True
    reservation.reservationId = response.reservationId
    reservation.confirmationNumber = response.confirmationNumber
    reservation.PaymentTokenReference = model.ApprovalCode
    reservation.PaymentId = model.PaymentId

    self.repository.update(reservation)
    self.db.commit()
    self.db.refresh(reservation)

    return ReservationResponse(
      Status=True,
      Message='Payment confirmed successfully',
      reservationId=reservation.reservationId,
      confirmationNumber=reservation.confirmationNumber,
    )