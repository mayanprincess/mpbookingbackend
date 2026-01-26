from pydantic import BaseModel

class OperaReservationResponse(BaseModel):
    reservationId: str
    confirmationNumber: str