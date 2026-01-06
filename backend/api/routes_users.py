"""User-facing endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..api.deps import get_current_user
from ..db import get_db
from ..models import User
from ..schemas import UserMe, UserUpdate


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserMe)
def read_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserMe:
    """Return current user profile."""
    return UserMe.model_validate(current_user)


@router.patch("/me", response_model=UserMe)
def update_me(
    payload: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserMe:
    """Update current user profile settings."""
    if payload.default_system_prompt is not None:
        current_user.default_system_prompt = payload.default_system_prompt
    if payload.default_temperature is not None:
        current_user.default_temperature = payload.default_temperature
    if payload.default_max_tokens is not None:
        current_user.default_max_tokens = payload.default_max_tokens
    if payload.theme is not None:
        current_user.theme = payload.theme

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return UserMe.model_validate(current_user)

