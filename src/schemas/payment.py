from pydantic import BaseModel
from typing import Optional


# ---------- Nested models ----------

class ThreeDSecure(BaseModel):
    ChallengeWindowSize: str


class ExtendedData(BaseModel):
    ThreeDSecure: ThreeDSecure
    MerchantResponseUrl: Optional[str] = None


class CreditCardSource(BaseModel):
    CardPan: str
    CardCvv: str
    CardExpiration: str
    CardholderName: str


class BillingAddress(BaseModel):
    FirstName: str
    LastName: str
    Line1: Optional[str] = None
    City: Optional[str] = None
    CountryCode: Optional[str] = None
    State: Optional[str] = None
    EmailAddress: Optional[str] = None
    PhoneNumber: Optional[str] = None


# ---------- Root model ----------

class PtranzSale(BaseModel):
    TotalAmount: float
    TaxAmount: float
    OrderIdentifier: str
    Source: CreditCardSource
    BillingAddress: BillingAddress
    ExtendedData: ExtendedData
    TransactionIdentifier: Optional[str] = ''
    CurrencyCode: str
    ThreeDSecure: bool = True
    AddressMatch: bool = False

class PtranzPayment(BaseModel):
  Status: bool
  Message: Optional[str] = ''
  AuthorizationCode: str
  TransactionIdentifier: str
  OrderIdentifier: str
  Response: str