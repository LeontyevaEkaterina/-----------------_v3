"""Chat and message CRUD endpoints."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..api.deps import get_current_user
from ..db import get_db
from ..models import Chat, Message, User
from ..schemas import (
    ChatCreate,
    ChatOut,
    ChatUpdate,
    ChatWithMessages,
    MessageCreate,
    MessageOut,
)


router = APIRouter(prefix="/chats", tags=["chats"])


def _get_chat_or_404(
    db: Session,
    chat_id: int,
    user_id: int,
) -> Chat:
    chat = (
        db.query(Chat)
        .filter(Chat.id == chat_id, Chat.user_id == user_id)
        .first()
    )
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return chat


@router.get("/", response_model=List[ChatOut])
def list_chats(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> List[ChatOut]:
    """Return list of user chats."""
    chats = (
        db.query(Chat)
        .filter(Chat.user_id == current_user.id)
        .order_by(Chat.updated_at.desc())
        .all()
    )
    return [ChatOut.model_validate(chat) for chat in chats]


@router.post("/", response_model=ChatOut, status_code=status.HTTP_201_CREATED)
def create_chat(
    payload: ChatCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ChatOut:
    """Create new chat for current user."""
    chat = Chat(
        user_id=current_user.id,
        title=payload.title,
        system_prompt=payload.system_prompt,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return ChatOut.model_validate(chat)


@router.get("/{chat_id}", response_model=ChatWithMessages)
def read_chat(
    chat_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ChatWithMessages:
    """Return chat with messages."""
    chat = _get_chat_or_404(db, chat_id=chat_id, user_id=current_user.id)
    return ChatWithMessages(
        **ChatOut.model_validate(chat).model_dump(),
        messages=[
            MessageOut.model_validate(msg) for msg in chat.messages
        ],
    )


@router.patch("/{chat_id}", response_model=ChatOut)
def update_chat(
    chat_id: int,
    payload: ChatUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ChatOut:
    """Update chat properties."""
    chat = _get_chat_or_404(db, chat_id=chat_id, user_id=current_user.id)

    if payload.title is not None:
        chat.title = payload.title
    if payload.system_prompt is not None:
        chat.system_prompt = payload.system_prompt
    if payload.temperature is not None:
        chat.temperature = payload.temperature
    if payload.max_tokens is not None:
        chat.max_tokens = payload.max_tokens

    db.add(chat)
    db.commit()
    db.refresh(chat)
    return ChatOut.model_validate(chat)


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(
    chat_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete chat with all messages."""
    chat = _get_chat_or_404(db, chat_id=chat_id, user_id=current_user.id)
    db.delete(chat)
    db.commit()
    return None


@router.get(
    "/{chat_id}/messages",
    response_model=List[MessageOut],
)
def list_messages(
    chat_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> List[MessageOut]:
    """Return messages for chat."""
    chat = _get_chat_or_404(db, chat_id=chat_id, user_id=current_user.id)
    return [MessageOut.model_validate(msg) for msg in chat.messages]


@router.post(
    "/{chat_id}/messages",
    response_model=MessageOut,
    status_code=status.HTTP_201_CREATED,
)
def create_message(
    chat_id: int,
    payload: MessageCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MessageOut:
    """Append user message to chat (without starting generation yet)."""
    chat = _get_chat_or_404(db, chat_id=chat_id, user_id=current_user.id)
    message = Message(
        chat_id=chat.id,
        role="user",
        content=payload.content,
        provider=payload.provider,
        model=payload.model,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return MessageOut.model_validate(message)

