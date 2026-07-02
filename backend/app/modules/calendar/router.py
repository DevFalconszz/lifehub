from fastapi import APIRouter, Depends

from app.core.auth.dependencies import get_current_user
from app.modules.calendar.service import CalendarService
from app.modules.calendar.types import EventCreate, EventUpdate

router = APIRouter(prefix='/api/calendar', tags=['calendar'])


def get_service(user: dict = Depends(get_current_user)) -> CalendarService:
    return CalendarService(user_id=user['id'])


@router.get('/events')
async def list_events(start: str | None = None, end: str | None = None, service: CalendarService = Depends(get_service)):
    events = await service.list_events(start=start, end=end)
    return {'data': events}


@router.post('/events', status_code=201)
async def create_event(body: EventCreate, service: CalendarService = Depends(get_service)):
    return await service.create_event(body.model_dump())


@router.patch('/events/{event_id}')
async def update_event(event_id: str, body: EventUpdate, service: CalendarService = Depends(get_service)):
    return await service.update_event(event_id, body.model_dump(exclude_unset=True))


@router.delete('/events/{event_id}', status_code=204)
async def delete_event(event_id: str, service: CalendarService = Depends(get_service)):
    await service.delete_event(event_id)
