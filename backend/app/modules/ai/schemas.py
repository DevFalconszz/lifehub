from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ChatMessageOut(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str | None
    created_at: datetime

    model_config = {'from_attributes': True}


class ChatSessionOut(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[ChatMessageOut] = []

    model_config = {'from_attributes': True}


class ChatSessionSummary(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int

    model_config = {'from_attributes': True}
