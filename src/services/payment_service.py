import html
import logging
from datetime import date, datetime
from pathlib import Path

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.core.config import settings
from src.schemas.guest import GuestCreate
from src.schemas.reservation import ReservationCreate, ReservationResponse
from src.services.cybersource_service import CybersourceService
from src.schemas.payment import CybersourceConfirmPaymentRequest, CybersourceValidatePaymentRequest
from src.models.reservation import Reservation
from src.repositories.reservation_repository import ReservationRepository
from src.repositories.user_repository import UserRepository
from src.services.loyalty_utils import membership_tier_for_points
from src.services.opera_service import OperaService
from src.core.opera_static_config import RatePlanInfo, RoomTypeInfo, opera_static_config

logger = logging.getLogger(__name__)


def _parse_reservation_date(value: str) -> date | None:
  s = str(value).strip()
  if len(s) < 10:
    return None
  try:
    return datetime.strptime(s[:10], "%Y-%m-%d").date()
  except ValueError:
    return None


def _stay_nights(check_in: str, check_out: str) -> int | None:
  d0 = _parse_reservation_date(check_in)
  d1 = _parse_reservation_date(check_out)
  if d0 is None or d1 is None:
    return None
  n = (d1 - d0).days
  return n if n >= 0 else None


def _nights_label_en(n: int) -> str:
  return "1 night" if n == 1 else f"{n} nights"


def _includes_labels_en(codes: list[str]) -> list[str]:
  labels: list[str] = []
  for key in codes:
    amenity = opera_static_config.amenities.get(key)
    if amenity:
      labels.append(amenity["en"])
    else:
      labels.append(key.replace("_", " ").title())
  return labels


class PaymentService:
  def __init__(self, db: Session):
    self.db = db
    self.repository = ReservationRepository(db)
    self.opera_service = OperaService(settings)
    self.cybersource_service = CybersourceService(settings)

  async def confirm_payment(self, model: CybersourceConfirmPaymentRequest) -> ReservationResponse:
    reservation = self.repository.get(model.ReservationId)
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    reservation_data = ReservationCreate(
      checkIn=reservation.checkIn,
      checkOut=reservation.checkOut,
      roomTypeCode=reservation.roomTypeCode,
      ratePlanCode=reservation.ratePlanCode,
      adults=reservation.adults,
      children=reservation.children,
      amountBeforeTax=reservation.amountBeforeTax,
      promoCode=reservation.promoCode,
      specialRequests=reservation.specialRequests,
      guest=GuestCreate(
        firstName=reservation.guest_first_name,
        lastName=reservation.guest_last_name,
        email=reservation.guest_email,
        phone=reservation.guest_phone,
      ),
    )
    response = await self.opera_service.create_reservation(reservation_data)

    reservation.isPaid = True
    reservation.reservationId = response.reservationId
    reservation.confirmationNumber = response.confirmationNumber
    reservation.PaymentTokenReference = model.ApprovalCode
    reservation.PaymentId = model.PaymentId

    self.repository.update(reservation)
    if reservation.user_id:
        self._sync_user_after_paid_reservation(reservation)

    self.db.commit()
    self.db.refresh(reservation)

    logger.info(
        "Payment confirmed reservation_id=%s opera_id=%s confirmation=%s",
        model.ReservationId,
        reservation.reservationId,
        reservation.confirmationNumber,
    )

    info_room = opera_static_config.roomTypes.get(reservation.roomTypeCode)
    info_rate = opera_static_config.ratePlans.get(reservation.ratePlanCode)

    await self.send_email_confirmation(reservation, info_room, info_rate)

    return ReservationResponse(
      Status=True,
      Message='Payment confirmed successfully',
      reservationId=reservation.reservationId,
      confirmationNumber=reservation.confirmationNumber,
    )

  async def send_email_confirmation(
    self,
    reservation: Reservation,
    info_room: RoomTypeInfo | None,
    info_rate: RatePlanInfo | None,
  ) -> None:
    if not settings.brevo_api_key.strip():
      logger.warning("BREVO_WAVE_API_KEY not set; skipping confirmation email")
      return

    first = reservation.guest_first_name.strip()
    last = reservation.guest_last_name.strip()
    guest_name = f"{first} {last}".strip() or "Guest"
    email = reservation.guest_email.strip()
    if not email:
      logger.warning("No guest email; skipping confirmation email")
      return

    conf = html.escape(reservation.confirmationNumber or "")
    check_in = html.escape(str(reservation.checkIn))
    check_out = html.escape(str(reservation.checkOut))
    nights_val = _stay_nights(reservation.checkIn, reservation.checkOut)
    nights_display = html.escape(_nights_label_en(nights_val) if nights_val is not None else "—")
    safe_name = html.escape(guest_name)

    room_name = html.escape(
      info_room["nameEn"] if info_room else reservation.roomTypeCode,
    )
    rate_label = html.escape(
      info_rate["labelEn"] if info_rate else reservation.ratePlanCode,
    )
    includes = info_rate["includes"] if info_rate else []
    includes_items = "".join(
      f'<li class="mp-include-li" style="margin:0 0 8px;line-height:1.5;color:#1c1917;">{html.escape(label)}</li>'
      for label in _includes_labels_en(includes)
    )
    includes_block = (
      f"""<div class="mp-includes" style="margin-top:28px;">
                <p style="margin:0 0 12px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.14em;color:#3d2f1f;">Your Package Includes</p>
                <ul class="mp-include-ul" style="margin:0;padding:0 0 0 20px;list-style-type:disc;font-size:15px;">{includes_items}</ul>
              </div>"""
      if includes_items
      else ""
    )

    subject = "Mayan Princess — Your reservation is confirmed"
    logo_src = html.escape(settings.email_logo_cdn_url, quote=True)
    html_body = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="x-apple-disable-message-reformatting" />
  <title>Reservation confirmation</title>
  <style type="text/css">
    /* Narrow screens (mobile mail clients) — smaller type for detail rows */
    @media only screen and (max-width: 480px) {{
      .mp-main-pad {{ padding: 24px 12px !important; }}
      .mp-card-pad {{ padding: 8px 18px 22px !important; }}
      .mp-header-pad {{ padding: 24px 18px 10px !important; }}
      .mp-footer-pad {{ padding: 16px 18px 24px !important; }}
      .mp-hero-brand {{ font-size: 11px !important; letter-spacing: 0.22em !important; }}
      .mp-hero-title {{ font-size: 21px !important; line-height: 1.3 !important; }}
      .mp-lead {{ font-size: 15px !important; }}
      .mp-copy {{ font-size: 13px !important; line-height: 1.6 !important; }}
      .mp-conf-label {{ font-size: 10px !important; }}
      .mp-conf-code {{ font-size: 24px !important; letter-spacing: 0.08em !important; }}
      .mp-section-label {{ font-size: 10px !important; }}
      table.mp-details td {{
        font-size: 13px !important;
        padding: 8px 10px !important;
        line-height: 1.35 !important;
      }}
      table.mp-details td strong {{ font-size: 13px !important; }}
      .mp-include-ul, .mp-include-ul .mp-include-li {{ font-size: 13px !important; }}
      .mp-footer {{ font-size: 12px !important; }}
    }}
  </style>
</head>
<body style="margin:0;padding:0;background:#e8e2d8;color:#1a141a;font-family:Georgia,'Palatino Linotype',serif;-webkit-font-smoothing:antialiased;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" bgcolor="#e8e2d8" style="background-color:#e8e2d8;padding:40px 16px;" class="mp-main-pad">
    <tr>
      <td align="center" style="color:#1a141a;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" bgcolor="#fffef9" style="max-width:560px;background-color:#fffef9;border-radius:16px;overflow:hidden;box-shadow:0 8px 24px rgba(26,20,16,0.12);border:1px solid #d4ccc0;">
          <tr>
            <td style="height:4px;background:linear-gradient(90deg,#8b6914 0%,#c9a227 50%,#8b6914 100%);"></td>
          </tr>
          <tr>
            <td style="padding:32px 36px 12px;text-align:center;" class="mp-header-pad">
              <p class="mp-hero-brand" style="margin:0;font-size:13px;font-weight:600;letter-spacing:0.28em;text-transform:uppercase;color:#3d2f1f;">Mayan Princess</p>
              <img src="{logo_src}" alt="Mayan Princess" width="220" height="auto" style="display:block;margin:18px auto 0;max-width:240px;width:100%;height:auto;border:0;outline:none;text-decoration:none;" />
              <h1 class="mp-hero-title" style="margin:14px 0 0;font-size:26px;font-weight:700;line-height:1.25;color:#0a0a0a;">Your reservation is confirmed</h1>
            </td>
          </tr>
          <tr>
            <td style="padding:8px 36px 28px;" class="mp-card-pad">
              <p class="mp-lead" style="margin:0 0 14px;font-size:17px;line-height:1.55;color:#1c1917;">Hello {safe_name},</p>
              <p class="mp-copy" style="margin:0 0 28px;font-size:15px;line-height:1.65;color:#292524;">Thank you for your payment. Please keep this email: it includes your confirmation number and stay dates.</p>
              <div style="background:#ffffff;border-radius:12px;padding:24px 20px;border:2px solid #a67c00;text-align:center;">
                <p class="mp-conf-label" style="margin:0 0 12px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.14em;color:#3d2f1f;">Confirmation number</p>
                <p class="mp-conf-code" style="margin:0;font-size:32px;font-weight:800;letter-spacing:0.12em;color:#0a0a0a;font-family:'Courier New',Consolas,monospace;line-height:1.2;">{conf or "—"}</p>
              </div>
              <p class="mp-section-label" style="margin:24px 0 12px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.14em;color:#3d2f1f;">Reservation details</p>
              <table role="presentation" class="mp-details" width="100%" cellspacing="0" cellpadding="0" style="margin-top:0;font-size:15px;border-collapse:separate;border-spacing:0 10px;table-layout:fixed;">
                <colgroup>
                  <col style="width:35%;" />
                  <col style="width:65%;" />
                </colgroup>
                <tr>
                  <td style="padding:12px 16px;background:#f0ebe3;border-radius:8px 0 0 8px;border:1px solid #cfc6b8;border-right:none;"><strong style="color:#0a0a0a;">Room</strong></td>
                  <td align="right" style="padding:12px 16px;background:#f0ebe3;border-radius:0 8px 8px 0;border:1px solid #cfc6b8;border-left:none;color:#1c1917;font-weight:600;">{room_name}</td>
                </tr>
                <tr>
                  <td style="padding:12px 16px;background:#f0ebe3;border-radius:8px 0 0 8px;border:1px solid #cfc6b8;border-right:none;"><strong style="color:#0a0a0a;">Rate plan</strong></td>
                  <td align="right" style="padding:12px 16px;background:#f0ebe3;border-radius:0 8px 8px 0;border:1px solid #cfc6b8;border-left:none;color:#1c1917;font-weight:600;">{rate_label}</td>
                </tr>
                <tr>
                  <td style="padding:12px 16px;background:#f0ebe3;border-radius:8px 0 0 8px;border:1px solid #cfc6b8;border-right:none;"><strong style="color:#0a0a0a;">Check-in</strong></td>
                  <td align="right" style="padding:12px 16px;background:#f0ebe3;border-radius:0 8px 8px 0;border:1px solid #cfc6b8;border-left:none;color:#1c1917;font-weight:600;">{check_in}</td>
                </tr>
                <tr>
                  <td style="padding:12px 16px;background:#f0ebe3;border-radius:8px 0 0 8px;border:1px solid #cfc6b8;border-right:none;"><strong style="color:#0a0a0a;">Check-out</strong></td>
                  <td align="right" style="padding:12px 16px;background:#f0ebe3;border-radius:0 8px 8px 0;border:1px solid #cfc6b8;border-left:none;color:#1c1917;font-weight:600;">{check_out}</td>
                </tr>
                <tr>
                  <td style="padding:12px 16px;background:#f0ebe3;border-radius:8px 0 0 8px;border:1px solid #cfc6b8;border-right:none;"><strong style="color:#0a0a0a;">Nights</strong></td>
                  <td align="right" style="padding:12px 16px;background:#f0ebe3;border-radius:0 8px 8px 0;border:1px solid #cfc6b8;border-left:none;color:#1c1917;font-weight:600;">{nights_display}</td>
                </tr>
              </table>
              {includes_block}
            </td>
          </tr>
          <tr>
            <td style="padding:20px 36px 32px;border-top:1px solid #d4ccc0;background:#f5f0e8;" class="mp-footer-pad">
              <p class="mp-footer" style="margin:0;font-size:13px;line-height:1.55;color:#292524;text-align:center;">Need help? Reply to this email or contact our reservations team.</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    payload = {
      "sender": {
        "name": settings.brevo_sender_name,
        "email": settings.brevo_sender_email,
      },
      "to": [{"email": email, "name": guest_name}],
      "subject": subject,
      "htmlContent": html_body,
    }
    headers = {
      "api-key": settings.brevo_api_key,
      "accept": "application/json",
      "content-type": "application/json",
    }
    try:
      async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(settings.brevo_url, json=payload, headers=headers)
      if resp.status_code >= 400:
        logger.error(
          "Brevo email failed status=%s body=%s",
          resp.status_code,
          resp.text[:500],
        )
      else:
        logger.info("Confirmation email sent to %s", email)
    except httpx.HTTPError as exc:
      logger.exception("Brevo email request failed: %s", exc)

  def _sync_user_after_paid_reservation(self, reservation: Reservation) -> None:
    repo = UserRepository(self.db)
    user = repo.get(reservation.user_id)
    if user is None:
        return
    user.reservation_count = (user.reservation_count or 0) + 1
    if settings.loyalty_enabled:
        pts = int(round(reservation.amountBeforeTax * settings.points_per_dollar))
        user.points_balance = (user.points_balance or 0) + pts
    user.membership_tier = membership_tier_for_points(user.points_balance)
    repo.update(user)