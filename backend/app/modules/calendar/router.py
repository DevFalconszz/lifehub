from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import get_current_user
from app.core.auth.models import User
from app.database import get_session
from app.modules.calendar.service import CalendarService
from app.modules.calendar.types import EventCreate, EventResponse, EventUpdate

router = APIRouter(prefix='/api/calendar', tags=['calendar'])


async def get_service(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> CalendarService:
    return CalendarService(session, user)


@router.get('/events')
async def list_events(
    start: datetime | None = None,
    end: datetime | None = None,
    service: CalendarService = Depends(get_service),
):
    events = await service.list_events(start=start, end=end)
    return {'data': [
        EventResponse(
            id=str(e.id), title=e.title, description=e.description,
            start_at=e.start_at, end_at=e.end_at,
            all_day=e.all_day, recurrence=e.recurrence,
            project_id=str(e.project_id) if e.project_id else None,
            created_at=e.created_at, updated_at=e.updated_at,
        ) for e in events
    ]}


@router.get('/events/{event_id}')
async def get_event(event_id: str, service: CalendarService = Depends(get_service)):
    e = await service.get_event(event_id)
    return EventResponse(
        id=str(e.id), title=e.title, description=e.description,
        start_at=e.start_at, end_at=e.end_at,
        all_day=e.all_day, recurrence=e.recurrence,
        project_id=str(e.project_id) if e.project_id else None,
        created_at=e.created_at, updated_at=e.updated_at,
    )


@router.post('/events', status_code=201)
async def create_event(body: EventCreate, service: CalendarService = Depends(get_service)):
    e = await service.create_event(body)
    return EventResponse(
        id=str(e.id), title=e.title, description=e.description,
        start_at=e.start_at, end_at=e.end_at,
        all_day=e.all_day, recurrence=e.recurrence,
        project_id=str(e.project_id) if e.project_id else None,
        created_at=e.created_at, updated_at=e.updated_at,
    )


@router.patch('/events/{event_id}')
async def update_event(
    event_id: str, body: EventUpdate,
    service: CalendarService = Depends(get_service),
):
    e = await service.update_event(event_id, body)
    return EventResponse(
        id=str(e.id), title=e.title, description=e.description,
        start_at=e.start_at, end_at=e.end_at,
        all_day=e.all_day, recurrence=e.recurrence,
        project_id=str(e.project_id) if e.project_id else None,
        created_at=e.created_at, updated_at=e.updated_at,
    )


@router.delete('/events/{event_id}', status_code=204)
async def delete_event(event_id: str, service: CalendarService = Depends(get_service)):
    await service.delete_event(event_id)
