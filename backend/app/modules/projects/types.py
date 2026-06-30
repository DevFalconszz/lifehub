import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    color: str | None = None
    status: str = 'active'
    priority: str = 'medium'
    category: str | None = None
    progress: int = 0
    start_at: datetime | None = None
    target_at: datetime | None = None
    url: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    color: str | None = None
    status: str | None = None
    priority: str | None = None
    category: str | None = None
    progress: int | None = None
    start_at: datetime | None = None
    target_at: datetime | None = None
    url: str | None = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str | None
    color: str | None
    status: str
    priority: str
    category: str | None
    progress: int
    start_at: datetime | None
    target_at: datetime | None
    url: str | None
    created_at: datetime
    updated_at: datetime
    task_count: int = 0


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    status: str = 'todo'
    priority: str = 'medium'
    due_at: datetime | None = None
    position: int = 0
    project_id: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    due_at: datetime | None = None
    position: int | None = None
    project_id: str | None = None


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str | None
    status: str
    priority: str
    due_at: datetime | None
    position: int
    project_id: str | None
    created_at: datetime
    updated_at: datetime
