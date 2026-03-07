from pydantic import BaseModel
from typing import Optional

class CybersourceValidatePaymentRequest(BaseModel):
  Token: str
  ReservationId: str
  
class PtranzPayment(BaseModel):
  Status: bool
  Message: Optional[str] = ''
  AuthorizationCode: str
  TransactionIdentifier: str
  OrderIdentifier: str
  Response: str

class CybersourceSale(BaseModel):
  Status: bool
  Message: Optional[str] = ''
  Id: Optional[str] = None
  Token: Optional[str] = None

class CybersourceSaleResponse(BaseModel):
  Status: bool
  Token: Optional[str] = None
  ReservationId: Optional[str] = None

class CybersourceConfirmPaymentRequest(BaseModel):
  ApprovalCode: str
  PaymentId: str
  ReservationId: str