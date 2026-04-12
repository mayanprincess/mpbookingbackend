from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.core.deps import get_current_user, get_current_user_optional
from src.db.session import get_db
from src.models.user import User
from src.schemas.reservation import ReservationCreate, ReservationOut
from src.services.reservation_service import ReservationService

router = APIRouter(prefix="/reservations", tags=["Reservations"])


def get_reservation_service(db: Session = Depends(get_db)) -> ReservationService:
    return ReservationService(db)


@router.get("/mine", response_model=list[ReservationOut])
def list_my_reservations(
    current_user: User = Depends(get_current_user),
    service: ReservationService = Depends(get_reservation_service),
    limit: int = Query(50, ge=1, le=100),
):
    """Reservas del usuario autenticado (requiere `Authorization: Bearer`)."""
    return service.list_for_user(current_user.id, limit=limit)


@router.post("")
async def create_reservation(
    reservation: ReservationCreate,
    current_user: User | None = Depends(get_current_user_optional),
    service: ReservationService = Depends(get_reservation_service),
):
    return await service.create_reservation(reservation, current_user=current_user)


@router.get("/{reservation_id}")
def get_reservation(
    reservation_id: str,
    service: ReservationService = Depends(get_reservation_service),
):
    row = service.get_reservation(reservation_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return row