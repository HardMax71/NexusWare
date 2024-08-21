# /server/app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "NexusWare WMS"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "SECRET"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "sqlite:///./nexusware.db"

    # SMTP Configuration
    SMTP_SERVER: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "your-username"
    SMTP_PASSWORD: str = "your-password"
    EMAIL_FROM: str = "your-email@example.com"
    EMAIL_FROM_NAME: str = "NexusWare WMS"

    PASSWORD_RESET_LINK: str = "https://nexusware-wms.com/reset-password"  # Not working for now

    # ShipEngine API configuration
    SHIPENGINE_API_KEY: str = "SHIPENGINE_API_KEY"
    SHIPENGINE_API_URL: str = "https://api.shipengine.com/v1"

    # User settings
    CACHE_SIZE_MB: int = 100
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
