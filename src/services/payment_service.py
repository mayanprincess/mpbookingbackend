import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.core.config import settings
from src.schemas.guest import GuestCreate
from src.schemas.reservation import ReservationCreate, ReservationResponse
from src.services.cybersource_service import CybersourceService
from src.schemas.payment import CybersourceConfirmPaymentRequest, CybersourceValidatePaymentRequest
from src.models.reservation import Reservation
from src.repositories.reservation_repository import ReservationRepository
from src.repositories.user_repository import UserRepository
from src.services.loyalty_utils import membership_tier_for_points
from src.services.opera_service import OperaService

logger = logging.getLogger(__name__)


class PaymentService:
  def __init__(self, db: Session):
    self.db = db
    self.repository = ReservationRepository(db)
    self.opera_service = OperaService(settings)
    self.cybersource_service = CybersourceService(settings)

  async def confirm_payment(self, model: CybersourceConfirmPaymentRequest) -> ReservationResponse:
    reservation = self.repository.get(model.ReservationId)
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

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
    if reservation.user_id:
        self._sync_user_after_paid_reservation(reservation)

    self.db.commit()
    self.db.refresh(reservation)

    logger.info(
        "Payment confirmed reservation_id=%s opera_id=%s confirmation=%s",
        model.ReservationId,
        reservation.reservationId,
        reservation.confirmationNumber,
    )

    return ReservationResponse(
      Status=True,
      Message='Payment confirmed successfully',
      reservationId=reservation.reservationId,
      confirmationNumber=reservation.confirmationNumber,
    )

  def _sync_user_after_paid_reservation(self, reservation: Reservation) -> None:
    repo = UserRepository(self.db)
    user = repo.get(reservation.user_id)
    if user is None:
        return
    user.reservation_count = (user.reservation_count or 0) + 1
    if settings.loyalty_enabled:
        pts = int(round(reservation.amountBeforeTax * settings.points_per_dollar))
        user.points_balance = (user.points_balance or 0) + pts
    user.membership_tier = membership_tier_for_points(user.points_balance)
    repo.update(user)