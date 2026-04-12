"""Validación y normalización de teléfono por país (HN, US)."""

from __future__ import annotations

import re
from typing import Literal

CountryCode = Literal["HN", "US"]


def digits_only(value: str) -> str:
    return re.sub(r"\D", "", value)


def normalize_phone(country: CountryCode, phone: str) -> str:
    """
    Devuelve formato E.164 compacto:
    - US: +1 + 10 dígitos NANP
    - HN: +504 + 8 dígitos (móvil)
    """
    d = digits_only(phone)
    if country == "US":
        if len(d) == 11 and d.startswith("1"):
            d = d[1:]
        if len(d) != 10:
            raise ValueError(
                "US phone must be 10 digits (or 11 starting with country code 1)",
            )
        if d[0] in ("0", "1"):
            raise ValueError("US area code cannot start with 0 or 1")
        return f"+1{d}"

    if country == "HN":
        if len(d) == 11 and d.startswith("504"):
            local = d[3:]
        elif len(d) == 8:
            local = d
        else:
            raise ValueError(
                "Honduras: use 8 digits (mobile) or 11 digits starting with 504",
            )
        if len(local) != 8:
            raise ValueError("Honduras mobile number must be 8 digits")
        return f"+504{local}"

    raise ValueError("unsupported country")
