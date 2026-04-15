"""Config estática OPERA (mapeos de room types, rate plans, etc.) — paridad con el frontend."""

from __future__ import annotations

from typing import TypedDict


class _RoomTypeInfoBase(TypedDict):
    nameEn: str
    nameEs: str
    bedrooms: int
    maxAdults: int
    maxChildren: int
    beds: list[str]
    location: str
    view: str
    sortOrder: int


class RoomTypeInfo(_RoomTypeInfoBase, total=False):
    """`hidden` solo aplica a algunos códigos (p. ej. 2BBFM)."""

    hidden: bool


class RatePlanInfo(TypedDict):
    package: str
    labelEn: str
    labelEs: str
    includes: list[str]
    sortOrder: int


class PackageTypeStyle(TypedDict):
    labelEn: str
    labelEs: str
    color: str
    bgClass: str


class LocalizedLabel(TypedDict):
    en: str
    es: str


class OperaStaticConfig:
    """Valores por defecto y catálogos no sensibles para enriquecer respuestas OPERA."""

    defaultRatePlanCode: str = "AIF-2025"

    roomTypes: dict[str, RoomTypeInfo] = {
        "1BT": {
            "nameEn": "One Bedroom Tower Villa",
            "nameEs": "Una Recámara Tower Villa",
            "bedrooms": 1,
            "maxAdults": 3,
            "maxChildren": 0,
            "beds": ["1 KING"],
            "location": "Mayan",
            "view": "garden",
            "sortOrder": 10,
        },
        "1BBFG": {
            "nameEn": "One Bedroom Beach Front Ground Floor Villa",
            "nameEs": "Una Recámara Frente al Mar Planta Baja",
            "bedrooms": 1,
            "maxAdults": 3,
            "maxChildren": 0,
            "beds": ["1 KING"],
            "location": "Mayan",
            "view": "ocean",
            "sortOrder": 11,
        },
        "1BBFS": {
            "nameEn": "One Bedroom Beach Front 2nd Floor Villa",
            "nameEs": "Una Recámara Frente al Mar 2do Piso",
            "bedrooms": 1,
            "maxAdults": 3,
            "maxChildren": 0,
            "beds": ["1 KING"],
            "location": "Mayan",
            "view": "ocean",
            "sortOrder": 12,
        },
        "1BGS": {
            "nameEn": "One Bedroom Garden 2nd Floor Villa",
            "nameEs": "Una Recámara Jardín 2do Piso",
            "bedrooms": 1,
            "maxAdults": 3,
            "maxChildren": 0,
            "beds": ["1 KING"],
            "location": "Mayan",
            "view": "garden",
            "sortOrder": 13,
        },
        "1BPTG": {
            "nameEn": "One Bedroom Pool View Trundle Ground Floor Villa",
            "nameEs": "Una Recámara Vista Alberca Trundle Planta Baja",
            "bedrooms": 1,
            "maxAdults": 4,
            "maxChildren": 0,
            "beds": ["1 KING", "1 TRUNDLE"],
            "location": "Mayan",
            "view": "pool",
            "sortOrder": 14,
        },
        "1BPG": {
            "nameEn": "One Bedroom Pool View Ground Floor Villa",
            "nameEs": "Una Recámara Vista Alberca Planta Baja",
            "bedrooms": 1,
            "maxAdults": 3,
            "maxChildren": 0,
            "beds": ["1 KING"],
            "location": "Mayan",
            "view": "pool",
            "sortOrder": 15,
        },
        "1DLX": {
            "nameEn": "One Deluxe Studio",
            "nameEs": "Estudio Deluxe Sencillo",
            "bedrooms": 1,
            "maxAdults": 2,
            "maxChildren": 0,
            "beds": ["1 KING"],
            "location": "Mayan",
            "view": "garden",
            "sortOrder": 20,
        },
        "2DLX": {
            "nameEn": "Two Deluxe Studio",
            "nameEs": "Estudio Deluxe Doble",
            "bedrooms": 1,
            "maxAdults": 3,
            "maxChildren": 0,
            "beds": ["2 FULL"],
            "location": "Mayan",
            "view": "garden",
            "sortOrder": 21,
        },
        "2BMS": {
            "nameEn": "Two Bedroom Master Suite Ground Floor",
            "nameEs": "Dos Recámaras Master Suite Planta Baja",
            "bedrooms": 2,
            "maxAdults": 5,
            "maxChildren": 0,
            "beds": ["1 KING", "1 QUEEN", "1 SOFA"],
            "location": "Mayan",
            "view": "ocean",
            "sortOrder": 40,
        },
        "2BMSS": {
            "nameEn": "Two Bedroom Master Suite 2nd Floor",
            "nameEs": "Dos Recámaras Master Suite 2do Piso",
            "bedrooms": 2,
            "maxAdults": 5,
            "maxChildren": 0,
            "beds": ["1 KING", "1 QUEEN", "1 SOFA"],
            "location": "Mayan",
            "view": "ocean",
            "sortOrder": 41,
        },
        "2BT": {
            "nameEn": "Two Bedroom Tower Villa",
            "nameEs": "Dos Recámaras Tower Villa",
            "bedrooms": 2,
            "maxAdults": 5,
            "maxChildren": 0,
            "beds": ["1 KING", "1 QUEEN", "1 SOFA"],
            "location": "Mayan",
            "view": "garden",
            "sortOrder": 42,
        },
        "2BJS": {
            "nameEn": "Two Bedroom Tower Junior Suite",
            "nameEs": "Dos Recámaras Tower Junior Suite",
            "bedrooms": 2,
            "maxAdults": 5,
            "maxChildren": 0,
            "beds": ["1 KING", "1 QUEEN", "1 SOFA"],
            "location": "Mayan",
            "view": "ocean",
            "sortOrder": 43,
        },
        "SF": {
            "nameEn": "Two Bedroom Family Suite",
            "nameEs": "Dos Recámaras Suite Familiar",
            "bedrooms": 2,
            "maxAdults": 4,
            "maxChildren": 0,
            "beds": ["2 QUEEN", "1 SOFA"],
            "location": "Mayan",
            "view": "garden",
            "sortOrder": 44,
        },
        "2BBFM": {
            "nameEn": "Two Bedroom Beach Front Master Villa",
            "nameEs": "Dos Recámaras Frente al Mar Master Villa",
            "bedrooms": 2,
            "maxAdults": 5,
            "maxChildren": 0,
            "beds": ["1 KING", "1 QUEEN", "1 SOFA"],
            "location": "Mayan",
            "view": "ocean",
            "sortOrder": 45,
            "hidden": True,
        },
    }

    ratePlans: dict[str, RatePlanInfo] = {
        "ALLINCPREM": {
            "package": "premium",
            "labelEn": "All Inclusive Premium",
            "labelEs": "Todo Incluido Premium",
            "includes": ["meals", "drinks", "activities", "premium_spirits"],
            "sortOrder": 1,
        },
        "FRACKMP2025": {
            "package": "promo",
            "labelEn": "Special Rate 2025",
            "labelEs": "Tarifa Especial 2025",
            "includes": ["meals", "drinks", "activities"],
            "sortOrder": 5,
        },
        "AIF": {
            "package": "family",
            "labelEn": "All Inclusive Family",
            "labelEs": "Todo Incluido Familiar",
            "includes": ["meals", "drinks", "kids_club", "activities"],
            "sortOrder": 2,
        },
        "AIF-2025": {
            "package": "family",
            "labelEn": "All Inclusive Family 2025",
            "labelEs": "Todo Incluido Familiar 2025",
            "includes": ["meals", "drinks", "kids_club", "activities"],
            "sortOrder": 3,
        },
        "AIP-2025": {
            "package": "premium",
            "labelEn": "All Inclusive Premium 2025",
            "labelEs": "Todo Incluido Premium 2025",
            "includes": [
                "meals",
                "drinks",
                "kids_club",
                "activities",
                "premium_spirits",
            ],
            "sortOrder": 4,
        },
        "BI-2025": {
            "package": "basic",
            "labelEn": "Breakfast Included 2025",
            "labelEs": "Desayuno Incluido 2025",
            "includes": ["breakfast"],
            "sortOrder": 10,
        },
        "BIMPOTA": {
            "package": "basic",
            "labelEn": "Breakfast Included (OTA)",
            "labelEs": "Desayuno Incluido (OTA)",
            "includes": ["breakfast"],
            "sortOrder": 11,
        },
        "BILSOTA": {
            "package": "basic",
            "labelEn": "Breakfast Included LS (OTA)",
            "labelEs": "Desayuno Incluido LS (OTA)",
            "includes": ["breakfast"],
            "sortOrder": 12,
        },
        "AIPLSOTA": {
            "package": "premium",
            "labelEn": "All Inclusive Premium LS (OTA)",
            "labelEs": "Todo Incluido Premium LS (OTA)",
            "includes": [
                "meals",
                "drinks",
                "kids_club",
                "activities",
                "premium_spirits",
            ],
            "sortOrder": 13,
        },
        "AIPMOTA": {
            "package": "premium",
            "labelEn": "All Inclusive Premium (OTA)",
            "labelEs": "Todo Incluido Premium (OTA)",
            "includes": [
                "meals",
                "drinks",
                "kids_club",
                "activities",
                "premium_spirits",
            ],
            "sortOrder": 14,
        },
    }

    packageTypes: dict[str, PackageTypeStyle] = {
        "premium": {
            "labelEn": "Premium",
            "labelEs": "Premium",
            "color": "#b58e4b",
            "bgClass": "bg-premium",
        },
        "family": {
            "labelEn": "Family",
            "labelEs": "Familiar",
            "color": "#2babd9",
            "bgClass": "bg-family",
        },
        "basic": {
            "labelEn": "Breakfast Only",
            "labelEs": "Solo Desayuno",
            "color": "#2babd9",
            "bgClass": "bg-breakfast",
        },
        "promo": {
            "labelEn": "Special",
            "labelEs": "Especial",
            "color": "#9333ea",
            "bgClass": "bg-promo",
        },
    }

    amenities: dict[str, LocalizedLabel] = {
        "meals": {"en": "All Meals", "es": "Todas las Comidas"},
        "drinks": {"en": "Unlimited Drinks", "es": "Bebidas Ilimitadas"},
        "premium_spirits": {"en": "Premium Spirits", "es": "Licores Premium"},
        "activities": {"en": "Daily Activities", "es": "Actividades Diarias"},
        "kids_club": {"en": "Kids Club Access", "es": "Acceso a Club de Niños"},
        "breakfast": {"en": "Daily Breakfast", "es": "Desayuno Diario"},
    }

    views: dict[str, LocalizedLabel] = {
        "ocean": {"en": "Ocean View", "es": "Vista al Mar"},
        "garden": {"en": "Garden View", "es": "Vista al Jardín"},
        "pool": {"en": "Pool View", "es": "Vista a la Piscina"},
    }


opera_static_config = OperaStaticConfig()

__all__ = ["OperaStaticConfig", "LocalizedLabel", "RatePlanInfo", "RoomTypeInfo", "opera_static_config"]
