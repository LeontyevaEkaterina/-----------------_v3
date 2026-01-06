"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Common fields for user representation."""

    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str


class UserMe(UserBase):
    """Current user information."""

    id: int
    default_system_prompt: Optional[str] = None
    default_temperature: Optional[float] = None
    default_max_tokens: Optional[int] = None
    theme: str
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    """Payload for updating user profile settings."""

    default_system_prompt: Optional[str] = None
    default_temperature: Optional[float] = None
    default_max_tokens: Optional[int] = None
    theme: Optional[str] = None


class ChatCreate(BaseModel):
    """Payload for chat creation."""

    title: str
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


class ChatUpdate(BaseModel):
    """Payload for updating chat."""

    title: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


class ChatOut(BaseModel):
    """Chat representation."""

    id: int
    title: str
    system_prompt: Optional[str]
    temperature: Optional[float]
    max_tokens: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    """Payload for sending a user message."""

    content: str
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


class MessageOut(BaseModel):
    """Message representation."""

    id: int
    chat_id: int
    role: str
    content: str
    provider: Optional[str]
    model: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ChatWithMessages(ChatOut):
    """Chat with associated messages."""

    messages: List[MessageOut]


class ProviderModelOut(BaseModel):
    """Model metadata for discovery."""

    id: int
    provider_name: str
    provider_display_name: str
    name: str
    display_name: str
    supports_streaming: bool
    requires_key: bool
    is_local_only: bool
    is_free_flag: bool
    region_available: Optional[str] = None
    max_input_tokens: Optional[int] = None
    max_output_tokens: Optional[int] = None


class SSEEvent(BaseModel):
    """Structured representation of SSE event payload."""

    type: str
    request_id: str
    data: dict

