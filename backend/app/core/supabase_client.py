from __future__ import annotations

from typing import Any

from supabase import create_async_client, AsyncClient

from app.config import get_settings

settings = get_settings()

_client: AsyncClient | None = None


async def get_supabase() -> AsyncClient:
    global _client
    if _client is None:
        _client = await create_async_client(
            settings.supabase_url,
            settings.supabase_service_key,
        )
    return _client


async def close_supabase():
    global _client
    if _client:
        try:
            await _client.postgrest.aclose()
            await _client.auth.aclose()
        except Exception:
            pass
        _client = None


class SupabaseService:
    def __init__(self, user_id: str | None = None):
        self._user_id = user_id

    async def _table(self, name: str) -> Any:
        client = await get_supabase()
        return client.table(name)

    def _user_filter(self, query: Any) -> Any:
        if self._user_id:
            return query.eq('user_id', self._user_id)
        return query

    async def list_all(self, table: str, filters: dict | None = None, order: str | None = None, limit: int | None = None) -> list[dict]:
        q = await self._table(table)
        q = q.select('*')
        q = self._user_filter(q)
        if filters:
            for k, v in filters.items():
                q = q.eq(k, v)
        if order:
            q = q.order(order, desc=True)
        if limit:
            q = q.limit(limit)
        result = await q.execute()
        return result.data

    async def get_by_id(self, table: str, id: str) -> dict | None:
        q = await self._table(table)
        q = q.select('*').eq('id', id)
        if self._user_id:
            q = q.eq('user_id', self._user_id)
        result = await q.execute()
        return result.data[0] if result.data else None

    async def create(self, table: str, data: dict) -> dict:
        q = await self._table(table)
        result = await q.insert(data).execute()
        return result.data[0]

    async def update(self, table: str, id: str, data: dict) -> dict:
        q = await self._table(table)
        q = q.update(data).eq('id', id)
        if self._user_id:
            q = q.eq('user_id', self._user_id)
        result = await q.execute()
        return result.data[0] if result.data else None

    async def soft_delete(self, table: str, id: str) -> None:
        from datetime import datetime, timezone
        q = await self._table(table)
        q = q.update({'deleted_at': datetime.now(timezone.utc).isoformat()}).eq('id', id)
        if self._user_id:
            q = q.eq('user_id', self._user_id)
        await q.execute()

    async def hard_delete(self, table: str, id: str) -> None:
        q = await self._table(table)
        q = q.delete().eq('id', id)
        if self._user_id:
            q = q.eq('user_id', self._user_id)
        await q.execute()

    async def count(self, table: str, filters: dict | None = None) -> int:
        q = await self._table(table)
        q = q.select('*', count='exact')
        q = self._user_filter(q)
        if filters:
            for k, v in filters.items():
                q = q.eq(k, v)
        result = await q.execute()
        return result.count

    async def raw(self, query: str) -> list[dict]:
        client = await get_supabase()
        result = await client.rpc('raw_sql', {'query': query}).execute()
        return result.data
