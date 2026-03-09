from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from src.schemas.payment import CybersourceConfirmPaymentRequest
from src.services.payment_service import PaymentService
from src.db.session import get_db


router = APIRouter(prefix="/payment", tags=["Payment"])


def get_payment_service(db: Session = Depends(get_db)) -> PaymentService:
  return PaymentService(db)

@router.post("/confirm-payment")
async def confirm_payment(confirm: CybersourceConfirmPaymentRequest, service: PaymentService = Depends(get_payment_service)):
  return await service.confirm_payment(confirm)