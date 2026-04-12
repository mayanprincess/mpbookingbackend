import logging

from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.exceptions import CybersourceCaptureContextError
from src.models.reservation import Reservation
from src.models.user import User
from src.repositories.reservation_repository import ReservationRepository
from src.schemas.payment import CybersourceSaleResponse
from src.schemas.reservation import ReservationCreate, ReservationResponse
from src.services.cybersource_service import CybersourceService
from src.services.opera_service import OperaService

logger = logging.getLogger(__name__)


class ReservationService:
    def __init__(self, db: Session):
      self.db = db
      self.repository = ReservationRepository(db)
      self.reservations = ReservationRepository(db)
      self.cybersource_service = CybersourceService(settings)
      self.opera_service = OperaService(settings)

        
    async def create_reservation(
        self,
        reservation: ReservationCreate,
        *,
        current_user: User | None = None,
    ) -> CybersourceSaleResponse:
      return await self._create_reservation_model(reservation, current_user=current_user)

    async def _create_reservation_model(
        self,
        reservation_data: ReservationCreate,
        *,
        current_user: User | None = None,
    ) -> CybersourceSaleResponse:
      reservation_model = Reservation(
        user_id=current_user.id if current_user else None,
        checkIn=reservation_data.checkIn,
        checkOut=reservation_data.checkOut,
        roomTypeCode=reservation_data.roomTypeCode,
        ratePlanCode=reservation_data.ratePlanCode,
        adults=reservation_data.adults,
        children=reservation_data.children,
        amountBeforeTax=reservation_data.amountBeforeTax,
        promoCode=reservation_data.promoCode,
        specialRequests=reservation_data.specialRequests,
        guest_first_name=reservation_data.guest.firstName,
        guest_last_name=reservation_data.guest.lastName,
        guest_email=reservation_data.guest.email,
        guest_phone=reservation_data.guest.phone,
      )

      new_reservation = self.repository.add(reservation_model)
      self.db.flush()
      self.db.refresh(new_reservation)
      logger.info(
          "Reservation persisted id=%s amount=%s",
          new_reservation.id,
          reservation_model.amountBeforeTax,
      )
      try:
        token = self.cybersource_service.create_sale_request(
            new_reservation.amountBeforeTax,
            new_reservation.id,
        )
      except CybersourceCaptureContextError:
        self.db.rollback()
        raise

      self.db.commit()
      self.db.refresh(new_reservation)

      return CybersourceSaleResponse(
        Status=True,
        Token=token,
        ReservationId=new_reservation.id,
      )
    

    def get_reservation(self, reservation_id: str):
      response= self.repository.get(reservation_id)
      return response

    def list_for_user(self, user_id: str, *, limit: int = 50):
        return self.repository.list_by_user_id(user_id, limit=limit)