from datetime import datetime

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str | None = None
    is_pinned: bool = False
    tags: list[str] | None = None


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    is_pinned: bool | None = None
    tags: list[str] | None = None


class NoteResponse(BaseModel):
    id: str
    title: str
    content: str | None
    is_pinned: bool
    tags: list[str] | None
    created_at: datetime
    updated_at: datetime
