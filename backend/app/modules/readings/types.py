from datetime import datetime

from pydantic import BaseModel, Field


class ReadingCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    url: str | None = None
    author: str | None = None
    type: str = 'article'
    status: str = 'unread'
    notes: str | None = None
    priority: int = 0


class ReadingUpdate(BaseModel):
    title: str | None = None
    url: str | None = None
    author: str | None = None
    type: str | None = None
    status: str | None = None
    notes: str | None = None
    priority: int | None = None


class ReadingResponse(BaseModel):
    id: str
    title: str
    url: str | None
    author: str | None
    type: str
    status: str
    notes: str | None
    priority: int
    created_at: datetime
    updated_at: datetime
