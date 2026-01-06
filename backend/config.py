"""Application configuration utilities."""

from functools import lru_cache
import os
from typing import List


class Settings:
    """Runtime configuration loaded from environment variables."""

    api_v1_prefix: str = "/api/v1"
    project_name: str = "Chat with Neural Networks API"

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://chat_user:chat_password@db:5432/chat_app",
    )

    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    google_redirect_uri: str = os.getenv(
        "GOOGLE_REDIRECT_URI",
        "http://localhost:8000/api/v1/auth/google/callback",
    )
    google_auth_base_url: str = "https://accounts.google.com/o/oauth2/v2/auth"
    google_token_url: str = "https://oauth2.googleapis.com/token"
    google_userinfo_url: str = "https://openidconnect.googleapis.com/v1/userinfo"
    google_scopes: List[str] = [
        "openid",
        "email",
        "profile",
    ]

    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-me")
    jwt_algorithm: str = "HS256"
    access_token_expires_minutes: int = 60
    access_token_cookie_name: str = "chat_access_token"

    allowed_origins: List[str] = [
        os.getenv("FRONTEND_ORIGIN", "http://localhost:8080")
    ]


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


