from datetime import datetime

from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    start_at: datetime
    end_at: datetime | None = None
    all_day: bool = False
    recurrence: str | None = None
    project_id: str | None = None


class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    all_day: bool | None = None
    recurrence: str | None = None
    project_id: str | None = None


class EventResponse(BaseModel):
    id: str
    title: str
    description: str | None
    start_at: datetime
    end_at: datetime | None
    all_day: bool
    recurrence: str | None
    project_id: str | None
    created_at: datetime
    updated_at: datetime
