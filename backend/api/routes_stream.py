"""SSE streaming endpoint (placeholder implementation)."""

from datetime import datetime
import json
from typing import AsyncGenerator
import uuid

from fastapi import APIRouter
from starlette.responses import StreamingResponse

from ..schemas import SSEEvent


router = APIRouter(prefix="/stream", tags=["stream"])


async def _fake_stream_generator(request_id: str) -> AsyncGenerator[str, None]:
    """Yield a short, fake SSE stream for testing the frontend pipeline."""
    events = [
        SSEEvent(
            type="metadata",
            request_id=request_id,
            data={"started_at": datetime.utcnow().isoformat()},
        ),
        SSEEvent(
            type="delta",
            request_id=request_id,
            data={"text": "Привет, "},
        ),
        SSEEvent(
            type="delta",
            request_id=request_id,
            data={"text": "это тестовый стрим ответа."},
        ),
        SSEEvent(
            type="done",
            request_id=request_id,
            data={"status": "ok"},
        ),
    ]
    for event in events:
        payload = event.model_dump()
        yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@router.get("/{chat_id}")
async def stream_chat(chat_id: int) -> StreamingResponse:
    """Stream model response for a chat (SSE placeholder).

    TODO: подключить реальный слой провайдеров и отмену генерации.
    """
    request_id = str(uuid.uuid4())
    generator = _fake_stream_generator(request_id=request_id)
    return StreamingResponse(generator, media_type="text/event-stream")

