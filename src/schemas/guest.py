from pydantic import BaseModel

class GuestCreate(BaseModel):
  firstName: str
  lastName: str
  email: str
  phone: str