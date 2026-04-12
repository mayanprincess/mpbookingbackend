from urllib.parse import urlparse

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_port: int = Field(..., env="DATABASE_PORT")
    database_host: str = Field(..., env="DATABASE_HOST")
    database_user: str = Field(..., env="DATABASE_USER")
    database_password: str = Field(..., env="DATABASE_PASSWORD")
    database_name: str = Field(..., env="DATABASE_NAME")

    # Opera PMS
    opera_app_key: str = Field(..., env="OPERA_APP_KEY")
    opera_client_id: str = Field(..., env="OPERA_CLIENT_ID")
    opera_client_secret: str = Field(..., env="OPERA_CLIENT_SECRET")
    opera_enterprise_id: str = Field(..., env="OPERA_ENTERPRISE_ID")
    opera_gateway_url: str = Field(..., env="OPERA_GATEWAY_URL")
    opera_hotel_id: str = Field(..., env="OPERA_HOTEL_ID")
    opera_scope: str = Field(..., env="OPERA_SCOPE")

    # Payment
    queue_connection: str = Field(..., env="QUEUE_CONNECTION")
    merchant_id: str = Field(..., env="MERCHANT_ID")
    merchant_key_id: str = Field(..., env="MERCHANT_KEY_ID")
    merchant_secret_key: str = Field(..., env="MERCHANT_SECRET_KEY")
    cybersource_base_url: str = Field(..., env="CYBERSOURCE_BASE_URL")

    # Frontend
    base_frontend_url: str = Field(..., env="BASE_FRONTEND_URL")

    @field_validator("base_frontend_url", mode="before")
    @classmethod
    def normalize_base_frontend_url(cls, v: object) -> str:
        if v is None or (isinstance(v, str) and not v.strip()):
            raise ValueError(
                "BASE_FRONTEND_URL must be set to the public frontend URL "
                "(e.g. https://reservas.tudominio.com)",
            )
        s = str(v).strip()
        if not s.startswith(("http://", "https://")):
            s = f"https://{s.lstrip('/')}"
        s = s.rstrip("/")
        parsed = urlparse(s)
        if not parsed.netloc:
            raise ValueError(
                "BASE_FRONTEND_URL must be a valid URL with host "
                "(CyberSource targetOrigins rejects invalid values)",
            )
        return s

    # JWT Auth
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=60, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=30, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")

    # Email
    smtp_host: str = Field(default="sandbox.smtp.mailtrap.io", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: str = Field(default="", env="SMTP_USER")
    smtp_password: str = Field(default="", env="SMTP_PASSWORD")
    emails_from_email: str = Field(default="noreply@mpbooking.com", env="EMAILS_FROM_EMAIL")
    emails_from_name: str = Field(default="MP Booking", env="EMAILS_FROM_NAME")

    # Loyalty (feature-flagged — set LOYALTY_ENABLED=True when ready to launch)
    loyalty_enabled: bool = Field(default=False, env="LOYALTY_ENABLED")
    points_per_dollar: int = Field(default=10, env="POINTS_PER_DOLLAR")
    silver_threshold: int = Field(default=1000, env="SILVER_THRESHOLD")
    gold_threshold: int = Field(default=5000, env="GOLD_THRESHOLD")
    platinum_threshold: int = Field(default=15000, env="PLATINUM_THRESHOLD")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
