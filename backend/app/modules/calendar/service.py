from datetime import datetime

from sqlalchemy import select, func, extract, Date
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.models import User
from app.core.exceptions import NotFoundError
from app.modules.calendar.models import Event
from app.modules.calendar.types import EventCreate, EventUpdate


class CalendarService:
    def __init__(self, session: AsyncSession, user: User):
        self.session = session
        self.user = user

    async def list_events(
        self, start: datetime | None = None, end: datetime | None = None,
    ) -> list[Event]:
        query = select(Event).where(
            Event.user_id == self.user.id,
            Event.deleted_at.is_(None),
        )
        if start:
            query = query.where(
                func.coalesce(Event.end_at, Event.start_at) >= start,
            )
        if end:
            query = query.where(Event.start_at <= end)
        query = query.order_by(Event.start_at)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_event(self, event_id: str) -> Event:
        result = await self.session.execute(
            select(Event).where(
                Event.id == event_id,
                Event.user_id == self.user.id,
                Event.deleted_at.is_(None),
            ),
        )
        event = result.scalar_one_or_none()
        if not event:
            raise NotFoundError('Event not found')
        return event

    async def create_event(self, data: EventCreate) -> Event:
        event = Event(
            title=data.title, description=data.description,
            start_at=data.start_at, end_at=data.end_at,
            all_day=data.all_day, recurrence=data.recurrence,
            project_id=data.project_id, user_id=self.user.id,
        )
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        return event

    async def update_event(self, event_id: str, data: EventUpdate) -> Event:
        event = await self.get_event(event_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(event, key, value)
        await self.session.flush()
        await self.session.refresh(event)
        return event

    async def delete_event(self, event_id: str) -> None:
        event = await self.get_event(event_id)
        event.deleted_at = func.now()
        await self.session.flush()
