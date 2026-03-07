from src.core.config import Settings
import hashlib
import base64
import hmac
import json
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time
import secrets
import requests


class CybersourceService:
  def __init__(self, config: Settings):
    self.config = config

  def get_rfc1123_date(self):
    """Fecha en formato RFC1123 para el header Date."""
    now = datetime.now()
    stamp = mktime(now.timetuple())
    return format_date_time(stamp)


  def compute_digest(self, payload: str) -> str:
      """Calcula el Digest SHA-256 del payload (Base64)."""
      hash_obj = hashlib.sha256()
      hash_obj.update(payload.encode("utf-8"))
      return base64.b64encode(hash_obj.digest()).decode("utf-8")

  def compute_signature(
      self,
      method: str,
      resource: str,
      host: str,
      date: str,
      digest: str,
      merchant_id: str,
      merchant_key_id: str,
      merchant_secret_key: str,
  ) -> str:
      """Genera el header Signature para HTTP Signature."""
      sign_string_parts = [
          f"host: {host}\n",
          f"date: {date}\n",
          f"request-target: {method.lower()} {resource}\n",
          f"digest: SHA-256={digest}\n",
          f"v-c-merchant-id: {merchant_id}",
      ]
      sign_string = "".join(sign_string_parts)
      secret = base64.b64decode(merchant_secret_key)
      signature = hmac.new(
          secret,
          sign_string.encode("utf-8"),
          hashlib.sha256,
      ).digest()
      signature_b64 = base64.b64encode(signature).decode("utf-8")
      return (
          f'keyid="{merchant_key_id}", '
          'algorithm="HmacSHA256", '
          'headers="host date request-target digest v-c-merchant-id", '
          f'signature="{signature_b64}"'
      )

  def create_sale_request(self, totalAmount: float, reservationId: str) -> str:
    target_origin = self.config.base_frontend_url
    

    payload = {
    "clientVersion": "0.34",
    "targetOrigins": [target_origin],
    "allowedCardNetworks": ["VISA", "MASTERCARD", "AMEX"],
    "allowedPaymentTypes": ["PANENTRY"],
    "country": "HN",
    "locale": "es_US",
    "captureMandate": {
        "billingType": "NONE",
        "requestEmail": False,
        "requestPhone": False,
        "requestShipping": False,
        "showAcceptedNetworkIcons": True,
    },
    "completeMandate": {
        "type": "CAPTURE",
        "decisionManager": True,
        "consumerAuthentication": True,
    },
    "data": {
        "orderInformation": {
            "amountDetails": {
                "totalAmount": f"{totalAmount:.2f}",
                "currency": "USD",
            }
        },
        "clientReferenceInformation": {
            "code": reservationId,
        },
        "consumerAuthenticationInformation": {
            "challengeCode": "04",
            "messageCategory": "01"
        }
    }
  }
    payload_str = json.dumps(payload, separators=(",", ":"))
    host =  self.config.cybersource_base_url.replace("https://", "")
    url = self.config.cybersource_base_url + "/up/v1/capture-contexts"

    date = self.get_rfc1123_date()
    digest = self.compute_digest(payload_str)
    signature = self.compute_signature(
        method="POST",
        resource="/up/v1/capture-contexts",
        host=host,
        date=date,
        digest=digest,
        merchant_id=self.config.merchant_id,
        merchant_key_id=self.config.merchant_key_id,
        merchant_secret_key=self.config.merchant_secret_key,
    )

    headers = {
      "Content-Type": "application/json;charset=utf-8",
      "Accept": "application/hal+json;charset=utf-8",
      "v-c-merchant-id": self.config.merchant_id,
      "Date": date,
      "Host": host,
      "Digest": f"SHA-256={digest}",
      "Signature": signature,
      "User-Agent": "Sale-API-Client/1.0",
    }

    response = requests.post(
        url,
        data=payload_str,
        headers=headers,
        timeout=30,
    )

    if response.status_code == 201:
        jwt_token = response.text.strip()
        return jwt_token
    else:
        print("Error:", response.text)
        return response.status_code, None, response.text