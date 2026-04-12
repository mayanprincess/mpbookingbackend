from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.reservation import Reservation
from src.repositories.base import BaseRepository


class ReservationRepository(BaseRepository[Reservation]):
    def __init__(self, db: Session):
        super().__init__(db, Reservation)

    def list_by_user_id(self, user_id: str, *, limit: int = 50) -> list[Reservation]:
        stmt = (
            select(Reservation)
            .where(Reservation.user_id == user_id)
            .order_by(Reservation.createdAt.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())