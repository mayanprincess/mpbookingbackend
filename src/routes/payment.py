from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.services.payment_service import PaymentService
from src.db.session import get_db


router = APIRouter(prefix="/payment", tags=["Payment"])


def get_payment_service(db: Session = Depends(get_db)) -> PaymentService:
  return PaymentService(db)


@router.post("/callback")
async def callback(request: Request, service: PaymentService = Depends(get_payment_service)):
  form_data = await request.form()
  spi_token = form_data.get("SpiToken")
  return await service.apply_payment(spi_token)