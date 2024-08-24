# settings.py

import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings."""

    APP_NAME: str
    # database
    DATABASE_URI: str
    FRONTEND_HOST: str

    # email
    # EMAIL_PASSWORD: str
    # EMAIL_PORT: int

    # EMAIL_STARTTLS: bool
    # EMAIL_USER: str
    # EMAIL_FROM: str
    # EMAIL_SERVER:str
    EMAIL_USER: str = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT"))
    EMAIL_SERVER: str = os.getenv("EMAIL_SERVER")
    EMAIL_STARTTLS: bool = os.getenv("EMAIL_TLS") == "True"
    EMAIL_SSL_TLS: bool = os.getenv("EMAIL_SSL") == "True"

    # jwt config
    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    # App Secret Key
    SECRET_KEY: str

    class Config:
        """Settings configuration."""
        env_file = '.env'
        case_sensitive = True
        ignore_undefined = True
        validat_default = True
        extra = 'ignore'

@lru_cache()
def get_settings() -> Settings:
    """Get the application settings."""
    return Settings()

settings = get_settings()
