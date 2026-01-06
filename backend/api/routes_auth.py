"""Auth endpoints: Google OAuth, session info and logout."""

from secrets import token_urlsafe
from typing import Annotated
from urllib.parse import urlencode

import httpx
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..models import User
from ..schemas import UserMe
from ..security import cookie_settings, create_access_token


router = APIRouter(prefix="/auth", tags=["auth"])

settings = get_settings()

OAUTH_STATE_COOKIE_NAME = "oauth_state"


@router.get("/google/login")
async def google_login(response: Response) -> dict:
    """Return Google OAuth authorization URL.

    Фронтенд получает URL и выполняет редирект пользователя.
    """
    state = token_urlsafe(32)
    response.set_cookie(
        key=OAUTH_STATE_COOKIE_NAME,
        value=state,
        max_age=600,
        **cookie_settings(),
    )

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": " ".join(settings.google_scopes),
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    url = f"{settings.google_auth_base_url}?{urlencode(params)}"
    return {"authorization_url": url}


@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: str,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """Handle Google OAuth callback, create user and issue session cookie."""
    state_query = request.query_params.get("state")
    state_cookie = request.cookies.get(OAUTH_STATE_COOKIE_NAME)
    if not state_query or not state_cookie or state_query != state_cookie:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OAuth state",
        )

    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth is not configured",
        )

    token_payload = {
        "code": code,
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "redirect_uri": settings.google_redirect_uri,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        token_resp = await client.post(
            settings.google_token_url,
            data=token_payload,
        )
        if token_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not exchange authorization code",
            )
        token_data = token_resp.json()

        id_token = token_data.get("id_token")
        access_token = token_data.get("access_token")
        if not id_token and not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token response from Google",
            )

        if id_token:
            claims = jwt.get_unverified_claims(id_token)
            sub = claims.get("sub")
            email = claims.get("email")
            name = claims.get("name")
            picture = claims.get("picture")
        else:
            userinfo_resp = await client.get(
                settings.google_userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if userinfo_resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not fetch user info from Google",
                )
            info = userinfo_resp.json()
            sub = info.get("sub")
            email = info.get("email")
            name = info.get("name")
            picture = info.get("picture")

    if not sub or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google did not provide required user data",
        )

    user = db.query(User).filter(User.google_sub == sub).first()
    if user is None:
        user = User(
            google_sub=sub,
            email=email,
            name=name,
            avatar_url=picture,
            role="user",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.email = email
        user.name = name
        user.avatar_url = picture
        db.add(user)
        db.commit()
        db.refresh(user)

    jwt_token = create_access_token(
        subject=user.id,
        extra_claims={"role": user.role},
    )

    response.set_cookie(
        key=settings.access_token_cookie_name,
        value=jwt_token,
        **cookie_settings(),
    )

    return {"status": "ok"}


@router.get("/session", response_model=UserMe | None)
async def get_session(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> UserMe | None:
    """Return current session information based on auth cookie."""
    token = request.cookies.get(settings.access_token_cookie_name)
    if not token:
        return None
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        sub = payload.get("sub")
        if sub is None:
            return None
        user_id = int(sub)
    except (JWTError, ValueError):
        return None

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return None
    return UserMe.model_validate(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    """Logout by clearing auth cookie."""
    response.delete_cookie(
        key=settings.access_token_cookie_name,
        path="/",
    )
    return None


