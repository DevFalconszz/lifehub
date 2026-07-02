from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.core.supabase_client import SupabaseService


class NoteService(SupabaseService):
    async def list_notes(self, pinned_only: bool = False) -> list[dict]:
        filters = {}
        if pinned_only:
            filters['is_pinned'] = True
        return await self.list_all('notes', filters=filters, order='updated_at')

    async def get_note(self, note_id: str) -> dict:
        note = await self.get_by_id('notes', note_id)
        if not note:
            from app.core.exceptions import NotFoundError
            raise NotFoundError('Note not found')
        return note

    async def create_note(self, data: dict) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        return await self.create('notes', {
            'id': str(uuid.uuid4()),
            'user_id': self._user_id,
            'created_at': now,
            'updated_at': now,
            **data,
        })

    async def update_note(self, note_id: str, data: dict) -> dict:
        data['updated_at'] = datetime.now(timezone.utc).isoformat()
        result = await self.update('notes', note_id, data)
        if not result:
            from app.core.exceptions import NotFoundError
            raise NotFoundError('Note not found')
        return result

    async def delete_note(self, note_id: str) -> None:
        await self.soft_delete('notes', note_id)
