from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.core.supabase_client import SupabaseService


class ReadingService(SupabaseService):
    async def list_items(self, status: str | None = None, type: str | None = None) -> list[dict]:
        filters = {}
        if status:
            filters['status'] = status
        if type:
            filters['type'] = type
        return await self.list_all('reading_items', filters=filters, order='created_at')

    async def get_item(self, item_id: str) -> dict:
        item = await self.get_by_id('reading_items', item_id)
        if not item:
            from app.core.exceptions import NotFoundError
            raise NotFoundError('Reading item not found')
        return item

    async def create_item(self, data: dict) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        return await self.create('reading_items', {
            'id': str(uuid.uuid4()),
            'user_id': self._user_id,
            'created_at': now,
            'updated_at': now,
            **data,
        })

    async def update_item(self, item_id: str, data: dict) -> dict:
        data['updated_at'] = datetime.now(timezone.utc).isoformat()
        result = await self.update('reading_items', item_id, data)
        if not result:
            from app.core.exceptions import NotFoundError
            raise NotFoundError('Reading item not found')
        return result

    async def delete_item(self, item_id: str) -> None:
        await self.soft_delete('reading_items', item_id)
