"""Models and providers discovery endpoints."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Model, Provider
from ..schemas import ProviderModelOut


router = APIRouter(prefix="/models", tags=["models"])


@router.get("/", response_model=List[ProviderModelOut])
def list_models(db: Session = Depends(get_db)) -> list[ProviderModelOut]:
    """Return available models with provider metadata."""
    query = db.query(Model, Provider).join(Provider, Model.provider_id == Provider.id)
    items: list[ProviderModelOut] = []
    for model, provider in query.all():
        items.append(
            ProviderModelOut(
                id=model.id,
                provider_name=provider.name,
                provider_display_name=provider.display_name,
                name=model.name,
                display_name=model.display_name,
                supports_streaming=model.supports_streaming,
                requires_key=model.requires_key,
                is_local_only=model.is_local_only,
                is_free_flag=model.is_free_flag,
                region_available=model.region_available,
                max_input_tokens=model.max_input_tokens,
                max_output_tokens=model.max_output_tokens,
            )
        )
    return items

