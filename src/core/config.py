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
    merchant_id: str = Field(..., env="MERCHANT_ID")
    merchant_key_id: str = Field(..., env="MERCHANT_KEY_ID")
    merchant_secret_key: str = Field(..., env="MERCHANT_SECRET_KEY")
    cybersource_base_url: str = Field(..., env="CYBERSOURCE_BASE_URL")
    base_frontend_url: str = Field(..., env="BASE_FRONTEND_URL")

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()