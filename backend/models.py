"""SQLAlchemy models for users, chats, messages and keys."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .db import Base


class User(Base):
    """Application user authenticated via Google OAuth."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    google_sub: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="user")

    default_system_prompt: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    default_temperature: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )
    default_max_tokens: Mapped[Optional[int]] = mapped_column(
        nullable=True,
    )
    theme: Mapped[str] = mapped_column(String(20), default="system")

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    chats: Mapped[list["Chat"]] = relationship(
        "Chat",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    api_keys: Mapped[list["ApiKey"]] = relationship(
        "ApiKey",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Chat(Base):
    """Conversation owned by a user."""

    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255))

    system_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    temperature: Mapped[Optional[float]] = mapped_column(nullable=True)
    max_tokens: Mapped[Optional[int]] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    user: Mapped["User"] = relationship("User", back_populates="chats")
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )


class Message(Base):
    """Single message within a chat."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chat_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("chats.id", ondelete="CASCADE"),
        index=True,
    )
    role: Mapped[str] = mapped_column(String(20))  # user, model, system
    content: Mapped[str] = mapped_column(Text)

    provider: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")


class Provider(Base):
    """LLM provider such as GPT, Claude, Gemini and others."""

    __tablename__ = "providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    display_name: Mapped[str] = mapped_column(String(255))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    models: Mapped[list["Model"]] = relationship(
        "Model",
        back_populates="provider",
        cascade="all, delete-orphan",
    )


class Model(Base):
    """Particular LLM model exposed by a provider."""

    __tablename__ = "models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("providers.id", ondelete="CASCADE"),
    )

    name: Mapped[str] = mapped_column(String(100))
    display_name: Mapped[str] = mapped_column(String(255))

    supports_streaming: Mapped[bool] = mapped_column(Boolean, default=True)
    requires_key: Mapped[bool] = mapped_column(Boolean, default=True)
    is_local_only: Mapped[bool] = mapped_column(Boolean, default=False)
    is_free_flag: Mapped[bool] = mapped_column(Boolean, default=False)

    region_available: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    max_input_tokens: Mapped[Optional[int]] = mapped_column(nullable=True)
    max_output_tokens: Mapped[Optional[int]] = mapped_column(nullable=True)

    provider: Mapped["Provider"] = relationship(
        "Provider",
        back_populates="models",
    )

    __table_args__ = (
        UniqueConstraint("provider_id", "name", name="uq_provider_model_name"),
    )


class ApiKey(Base):
    """API keys for providers: BYOK or admin keys."""

    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    provider_name: Mapped[str] = mapped_column(String(100), index=True)
    label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    encrypted_key: Mapped[str] = mapped_column(Text)
    is_admin_key: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    user: Mapped[Optional["User"]] = relationship("User", back_populates="api_keys")

