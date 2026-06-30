from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import Base, BaseModelMixin


class ChatSession(Base, BaseModelMixin):
    __tablename__ = 'chat_sessions'

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, default='New Chat')
    is_active: Mapped[bool] = mapped_column(default=True)

    messages: Mapped[list['ChatMessage']] = relationship(
        back_populates='session', order_by='ChatMessage.created_at', cascade='all, delete-orphan',
    )


class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('chat_sessions.id'), nullable=False, index=True)
    role: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    session: Mapped['ChatSession'] = relationship(back_populates='messages')
