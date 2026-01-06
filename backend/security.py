"""Security helpers: JWT creation and cookie utilities."""

from datetime import datetime, timedelta, timezone
import os
from typing import Any, Dict

from jose import jwt

from .config import get_settings


settings = get_settings()


def create_access_token(subject: str | int, extra_claims: Dict[str, Any]) -> str:
    """Create signed JWT access token."""
    now = datetime.now(tz=timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expires_minutes)
    payload: Dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    payload.update(extra_claims)
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def cookie_settings() -> dict[str, Any]:
    """Return common cookie settings for auth cookie.

    В dev-окружении флаг secure может быть выключен, в prod (по ENVIRONMENT=production)
    включается автоматически.
    """
    is_production = os.getenv("ENVIRONMENT", "").lower() == "production"
    return {
        "httponly": True,
        "secure": is_production,
        "samesite": "lax",
        "path": "/",
    }


