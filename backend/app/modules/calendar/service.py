from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.core.supabase_client import SupabaseService


class CalendarService(SupabaseService):
    async def list_events(self, start: str | None = None, end: str | None = None) -> list[dict]:
        supabase = await self._table('events')
        q = supabase.select('*')
        q = self._user_filter(q)
        if start:
            q = q.gte('start_at', start)
        if end:
            q = q.lte('start_at', end)
        q = q.order('start_at')
        result = await q.execute()
        return result.data or []

    async def get_event(self, event_id: str) -> dict:
        event = await self.get_by_id('events', event_id)
        if not event:
            from app.core.exceptions import NotFoundError
            raise NotFoundError('Event not found')
        return event

    async def create_event(self, data: dict) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        return await self.create('events', {
            'id': str(uuid.uuid4()),
            'user_id': self._user_id,
            'created_at': now,
            'updated_at': now,
            **data,
        })

    async def update_event(self, event_id: str, data: dict) -> dict:
        data['updated_at'] = datetime.now(timezone.utc).isoformat()
        result = await self.update('events', event_id, data)
        if not result:
            from app.core.exceptions import NotFoundError
            raise NotFoundError('Event not found')
        return result

    async def delete_event(self, event_id: str) -> None:
        await self.soft_delete('events', event_id)
