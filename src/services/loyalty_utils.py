"""Cálculo de tier según puntos y umbrales de configuración."""

from src.core.config import settings


def membership_tier_for_points(points: int) -> str:
    if points >= settings.platinum_threshold:
        return "platinum"
    if points >= settings.gold_threshold:
        return "gold"
    if points >= settings.silver_threshold:
        return "silver"
    return "bronze"
