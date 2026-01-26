from math import fabs
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    database_port: int = Field(..., env="DATABASE_PORT")
    database_host: str = Field(..., env="DATABASE_HOST")
    database_user: str = Field(..., env="DATABASE_USER")
    database_password: str = Field(..., env="DATABASE_PASSWORD")
    database_name: str = Field(..., env="DATABASE_NAME")
    opera_app_key: str = Field(..., env="OPERA_APP_KEY")
    opera_client_id: str = Field(..., env="OPERA_CLIENT_ID")
    opera_client_secret: str = Field(..., env="OPERA_CLIENT_SECRET")
    opera_enterprise_id: str = Field(..., env="OPERA_ENTERPRISE_ID")
    opera_gateway_url: str = Field(..., env="OPERA_GATEWAY_URL")
    opera_hotel_id: str = Field(..., env="OPERA_HOTEL_ID")
    opera_scope: str = Field(..., env="OPERA_SCOPE")
    queue_connection: str = Field(..., env="QUEUE_CONNECTION")
    ptranz_currency: str = Field(..., env="PTRANZ_CURRENCY")
    ptranz_base_url: str = Field(..., env="PTRANZ_BASE_URL")
    ptranz_id: str = Field(..., env="PTRANZ_ID")
    ptranz_password: str = Field(..., env="PTRANZ_PASSWORD")
    base_frontend_url: str = Field(..., env="BASE_FRONTEND_URL")
    base_api_url: str = Field(..., env="BASE_API_URL")

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()