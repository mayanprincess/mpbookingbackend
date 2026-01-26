from sqlalchemy.orm import Session
from src.services.ptranz_service import PtranzService
from src.schemas.payment import BillingAddress, CreditCardSource, ExtendedData, PtranzSale, ThreeDSecure
from src.repositories.reservation_repository import ReservationRepository
from src.schemas.reservation import ReservationCreate, ReservationResponse
from src.services.opera_service import OperaService
from src.core.config import settings
from src.models.reservation import Reservation



class ReservationService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = ReservationRepository(db)
        self.reservations = ReservationRepository(db)
        self.ptranz_service = PtranzService(settings)
        
    async def create_reservation(self, reservation: ReservationCreate) -> str:
        iframe = await self._create_reservation_model(reservation)
        return iframe

    async def _create_reservation_model(self, reservation_data: ReservationCreate) -> str:
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
      self.db.commit()
      self.db.refresh(new_reservation)
      iframe3ds = await self._getIframe3ds(new_reservation, reservation_data)
      return iframe3ds
    
    async def _getIframe3ds(self, reservation: Reservation, model: ReservationCreate):
      firstName = model.payment.cardHolder.split(' ')[0]
      lastName = model.payment.cardHolder.split(' ')[1]
      

      saleInfo = PtranzSale(
        TotalAmount= reservation.amountBeforeTax,
        TaxAmount=0,
        OrderIdentifier= reservation.id,
        Source= CreditCardSource(
          CardPan= model.payment.cardNumber,
          CardCvv=model.payment.cvv,
          CardExpiration=f"{model.payment.expiryYear}{model.payment.expiryMonth:02d}",
          CardholderName=model.payment.cardHolder,
        ),
        BillingAddress= BillingAddress(
          FirstName=firstName,
          LastName=lastName,
        ),
        ExtendedData= ExtendedData(
          ThreeDSecure= ThreeDSecure(
            ChallengeWindowSize= "5"
          ),
        ),
        CurrencyCode= settings.ptranz_currency,
        ThreeDSecure= True,
        AddressMatch= False,
      )

      return await self.ptranz_service.create_sale(saleInfo)

    def get_reservation(self, reservation_id: str):
      response= self.repository.get(reservation_id)
      return response