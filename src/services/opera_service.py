from src.schemas.opera import OperaReservationResponse
from src.schemas.reservation import ReservationCreate
from src.core.config import Settings
import base64
import httpx
import re

class OperaService:
    def __init__(self, config: Settings):
        self.config = config

    async def _get_access_token(self):

      credentials = f'{self.config.opera_client_id}:{self.config.opera_client_secret}'
      basicAuth = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
      

      headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {basicAuth}',
        'x-app-key': self.config.opera_app_key,
        'enterpriseId': self.config.opera_enterprise_id,
      }
      data = {
        'grant_type': 'client_credentials',
        'scope': self.config.opera_scope,
      }
      async with httpx.AsyncClient() as client:
        response = await client.post(self.config.opera_gateway_url + '/oauth/v1/tokens', headers=headers, data=data)
      
      if response.status_code != 200:
        raise Exception(f'Failed to get access token: {response.status_code} {response.text}')

      data = response.json()
      return data['access_token']

    def _map_reservation_to_opera(self, reservation: ReservationCreate):
        return {
            'reservations': {
                'reservation': [
                    {
                        'sourceOfSale': {
                            'sourceType': 'PMS',
                            'sourceCode': self.config.opera_hotel_id
                        },
                        'roomStay': {
                            'roomRates': [
                                {
                                    'roomType': reservation.roomTypeCode,
                                    'ratePlanCode': reservation.ratePlanCode,
                                    'start': reservation.checkIn,
                                    'end': reservation.checkOut,
                                    'suppressRate': False,
                                    'marketCode': 'INTERNET',
                                    'sourceCode': 'WEB',
                                    'numberOfUnits': '1',
                                    'pseudoRoom': False,
                                    'roomTypeCharged': reservation.roomTypeCode,
                                    'houseUseOnly': False,
                                    'complimentary': False,
                                    'fixedRate': True,
                                    'discountAllowed': False,
                                    'bogoDiscount': False,
                                    'roomNumberLocked': False,
                                    'guestCounts': {
                                        'adults': str(reservation.adults),
                                        'children': str(reservation.children)
                                    },
                                    'rates': {
                                        'rate': [
                                            {
                                                'base': {
                                                    'amountBeforeTax': str(reservation.amountBeforeTax),
                                                    'currencyCode': 'USD'
                                                },
                                                'total': {
                                                    'amountBeforeTax': str(reservation.amountBeforeTax)
                                                },
                                                'start': reservation.checkIn,
                                                'end': reservation.checkOut,
                                                'shareDistributionInstruction': 'Full'
                                            }
                                        ]
                                    },
                                    'total': {
                                        'amountBeforeTax': str(reservation.amountBeforeTax),
                                        'currencyCode': 'USD'
                                    }
                                }
                            ],
                            'guestCounts': {
                                'adults': str(reservation.adults),
                                'children': str(reservation.children)
                            },
                            'arrivalDate': reservation.checkIn,
                            'departureDate': reservation.checkOut,
                            'guarantee': {
                                'guaranteeCode': 'PROP',
                                'shortDescription': 'Property Guaranteed',
                                'onHold': False
                            },
                            'roomNumberLocked': False,
                            'printRate': False
                        },
                        'reservationGuests': [
                            {
                                'profileInfo': {
                                    'profile': {
                                        'customer': {
                                            'personName': [
                                                {
                                                    'givenName': reservation.guest.firstName,
                                                    'surname': reservation.guest.lastName,
                                                    'nameType': 'Primary'
                                                }
                                            ],
                                            'language': 'E'
                                        },
                                        'profileType': 'Guest'
                                    }
                                },
                                'primary': True
                            }
                        ],
                        'reservationCommunication': {
                            'emails': {
                                'emailInfo': [
                                    {
                                        'email': {
                                            'emailAddress': reservation.guest.email,
                                            'type': 'HOME',
                                            'primaryInd': True
                                        }
                                    }
                                ] if reservation.guest.email else []
                            },
                            'telephones': {
                                'telephoneInfo': [
                                    {
                                        'telephone': {
                                            'phoneNumber': reservation.guest.phone,
                                            'phoneUseType': 'HOME',
                                            'primaryInd': True
                                        }
                                    }
                                ] if reservation.guest.phone else []
                            }
                        },
                        'reservationPaymentMethods': [
                            {
                                'paymentMethod': 'CA',
                                'folioView': 1
                            }
                        ],
                        'comments': [
                            {
                                'comment': {
                                    'text': {
                                        'value': 'Booking from website'
                                    },
                                    'commentTitle': 'General Notes',
                                    'notificationLocation': 'RESERVATION',
                                    'type': 'GEN',
                                    'internal': False
                                }
                            }
                        ],
                        'hotelId': self.config.opera_hotel_id,
                        'roomStayReservation': True,
                        'reservationStatus': 'Reserved',
                        'computedReservationStatus': 'Reserved',
                        'walkIn': False,
                        'printRate': False,
                        'preRegistered': False,
                        'upgradeEligible': False,
                        'allowAutoCheckin': False,
                        'hasOpenFolio': False,
                        'allowMobileCheckout': False,
                        'allowMobileViewFolio': False,
                        'allowPreRegistration': False,
                        'optedForCommunication': False
                    }
                ]
            }
        }

    async def create_reservation(self, reservation: ReservationCreate) -> OperaReservationResponse:
      operaJson = self._map_reservation_to_opera(reservation)
      access_token = await self._get_access_token()
      headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'x-enterpriseid': self.config.opera_enterprise_id,
        'x-hotelid': self.config.opera_hotel_id,
        'x-app-key': self.config.opera_app_key,
      }

      url = f'{self.config.opera_gateway_url}/rsv/v1/hotels/{self.config.opera_hotel_id}/reservations'

      async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=operaJson)

      try:
        response.raise_for_status()
        dataResponse = response.json()
        
        links = dataResponse.get('links', [])
        reservation_id = None
        confirmation_number = None

        if links:
          # Reservation ID desde el self link
          self_link = next(
              (link for link in links if link.get("operationId") == "getReservation"),
              None
          )
          if self_link:
              match = re.search(r"/reservations/(\d+)", self_link.get("href", ""))
              if match:
                  reservation_id = match.group(1)

          # Confirmation number desde query param
          confirmation_link = next(
              (link for link in links if "confirmationNumberList" in link.get("href", "")),
              None
          )
          if confirmation_link:
              match = re.search(r"confirmationNumberList=(\d+)", confirmation_link.get("href", ""))
              if match:
                  confirmation_number = match.group(1)

        return OperaReservationResponse(reservationId=reservation_id, confirmationNumber=confirmation_number)
        
      except httpx.HTTPStatusError as e:
        raise Exception(f'Failed to create reservation: {e}')