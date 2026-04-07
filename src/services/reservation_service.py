import logging

from sqlalchemy.orm import Session

from src.core.exceptions import CybersourceCaptureContextError
from src.schemas.payment import CybersourceSaleResponse
from src.services.cybersource_service import CybersourceService
from src.repositories.reservation_repository import ReservationRepository
from src.schemas.reservation import ReservationCreate, ReservationResponse
from src.services.opera_service import OperaService
from src.core.config import settings
from src.models.reservation import Reservation

logger = logging.getLogger(__name__)


class ReservationService:
    def __init__(self, db: Session):
      self.db = db
      self.repository = ReservationRepository(db)
      self.reservations = ReservationRepository(db)
      self.cybersource_service = CybersourceService(settings)
      self.opera_service = OperaService(settings)

        
    async def create_reservation(self, reservation: ReservationCreate) -> CybersourceSaleResponse:
      return await self._create_reservation_model(reservation)

    async def _create_reservation_model(self, reservation_data: ReservationCreate) -> CybersourceSaleResponse:
      reservation_model = Reservation(
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