from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.schemas.reservation import ReservationCreate, ReservationResponse
from src.services.reservation_service import ReservationService
from src.db.session import get_db

router = APIRouter(prefix="/reservations", tags=["Reservations"])

def get_reservation_service(db: Session = Depends(get_db)) -> ReservationService:
    return ReservationService(db)

@router.post("/")
async def create_reservation(reservation: ReservationCreate, service: ReservationService = Depends(get_reservation_service)):
  response = await service.create_reservation(reservation)
  return response

@router.get("/{reservation_id}") 
def get_reservation(reservation_id: str, service: ReservationService = Depends(get_reservation_service)) -> ReservationResponse:
  return service.get_reservation(reservation_id)