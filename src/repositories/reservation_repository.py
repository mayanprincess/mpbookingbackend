from sqlalchemy.orm import Session
from src.models.reservation import Reservation
from src.repositories.base import BaseRepository

class ReservationRepository(BaseRepository[Reservation]):
    def __init__(self, db: Session):
        super().__init__(db, Reservation)