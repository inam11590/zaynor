from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    APP_NAME: str = "ZAYNOR API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"

    # Database — SQLite for development, PostgreSQL for production (Render)
    DATABASE_URL: str = "sqlite:///./zaynor.db"

    # JWT Authentication
    SECRET_KEY: str = "zaynor-dev-secret-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Email — SMTP configuration
    SMTP_ENABLED: bool = False
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@zaynor.com"
    SMTP_FROM_NAME: str = "ZAYNOR"
    ADMIN_EMAIL: str = "admin@zaynor.com"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "60/minute"
    RATE_LIMIT_AUTH: str = "10/minute"
    RATE_LIMIT_ORDERS: str = "20/minute"
    RATE_LIMIT_REVIEWS: str = "30/minute"

    # CORS origins — comma-separated in .env
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5500,http://127.0.0.1:3000,http://127.0.0.1:5500,http://localhost:8080,http://127.0.0.1:8080,https://zaynor-seven.vercel.app,null"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
