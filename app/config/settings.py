from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings."""

    APP_NAME: str
    # SECRET_KEY: str
    DATABASE_URI: str
    ALEMBIC_DATABASE_URI: str
    FRONTEND_HOST: str

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
