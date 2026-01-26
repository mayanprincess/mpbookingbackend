import json
from uuid6 import uuid7
from src.schemas.payment import PtranzPayment, PtranzSale
from src.core.config import Settings
import httpx

class PtranzService:
    def __init__(self, config: Settings):
        self.config = config

    async def create_sale(self, sale: PtranzSale) -> str:
      url = f'{self.config.ptranz_base_url}sale'
      sale.TransactionIdentifier = str(uuid7())
      sale.ExtendedData.MerchantResponseUrl = f'{self.config.base_api_url}payment/callback'

      headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'PowerTranz-PowerTranzId': self.config.ptranz_id,
        'PowerTranz-PowerTranzPassword': self.config.ptranz_password
      }
      async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=sale.model_dump())

      try: 
        response.raise_for_status()
        dataResponse = response.json()

        return dataResponse['RedirectData']
      
      except httpx.HTTPStatusError as e:
        print(e)
        return ''
    
    async def apply_payment(self, spiToken: str) -> PtranzPayment:
      url = f'{self.config.ptranz_base_url}payment'
      headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'PowerTranz-PowerTranzId': self.config.ptranz_id,
        'PowerTranz-PowerTranzPassword': self.config.ptranz_password
      }
      # Enviar el token como string JSON entre comillas dobles, igual que en axios
      json_payload = json.dumps(spiToken)
      async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, content=json_payload)


      try: 
        response.raise_for_status()
        dataResponse = response.json() 

        if(dataResponse['Approved']):
          return PtranzPayment(
            Status=True,
            AuthorizationCode=dataResponse['AuthorizationCode'],
            TransactionIdentifier=dataResponse['TransactionIdentifier'],
            OrderIdentifier=dataResponse['OrderIdentifier'],
            Response= json.dumps(dataResponse)
          )
        else:
          return PtranzPayment(
            Status=False,
            Message="Error al realizar el pago",
            AuthorizationCode=dataResponse['AuthorizationCode'],
            TransactionIdentifier=dataResponse['TransactionIdentifier'],
            OrderIdentifier=dataResponse['OrderIdentifier'],
            Response= json.dumps(dataResponse)
          )
      
      except httpx.HTTPStatusError as e:
        print(e)
        return PtranzPayment(
          Status=False,
          Message="Error al realizar el pago",
          AuthorizationCode='',
          TransactionIdentifier='',
          OrderIdentifier='',
          Response=''
        )