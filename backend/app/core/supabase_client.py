from __future__ import annotations

import logging
from typing import Any

from fastapi import HTTPException
from supabase import create_async_client, AsyncClient

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

_admin_client: AsyncClient | None = None
_user_clients: dict[str, AsyncClient] = {}


async def get_supabase() -> AsyncClient:
    global _admin_client
    if _admin_client is None:
        _admin_client = await create_async_client(
            settings.supabase_url,
            settings.supabase_service_key,
        )
    return _admin_client


async def get_admin_client() -> AsyncClient:
    return await get_supabase()


_anon_client: AsyncClient | None = None


async def get_anon_client() -> AsyncClient:
    """Client with anon_key for auth operations (login, register, etc.)."""
    global _anon_client
    if _anon_client is None:
        _anon_client = await create_async_client(
            settings.supabase_url,
            settings.supabase_anon_key,
        )
    return _anon_client


async def get_user_client(token: str | None = None) -> AsyncClient:
    if not token:
        return await get_supabase()
    if token not in _user_clients:
        client = await create_async_client(
            settings.supabase_url,
            settings.supabase_anon_key,
        )
        try:
            await client.auth.set_session(token, '')
        except Exception as e:
            logger.warning(f"Invalid or expired token: {e}")
            try:
                await client.aclose()
            except Exception:
                pass
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        _user_clients[token] = client
    return _user_clients[token]


async def close_supabase():
    global _admin_client, _anon_client
    for client in _user_clients.values():
        try:
            await client.aclose()
        except Exception:
            pass
    _user_clients.clear()
    if _anon_client:
        try:
            await _anon_client.aclose()
        except Exception:
            pass
        _anon_client = None
    if _admin_client:
        try:
            await _admin_client.aclose()
        except Exception:
            pass
        _admin_client = None


class SupabaseService:
    def __init__(self, user_id: str | None = None, token: str | None = None):
        self._user_id = user_id
        self._token = token

    async def _get_client(self) -> AsyncClient:
        return await get_user_client(self._token)

    async def _table(self, name: str) -> Any:
        client = await self._get_client()
        return client.table(name)

    def _user_filter(self, q: Any) -> Any:
        if self._user_id:
            return q.eq('user_id', self._user_id)
        return q

    async def list_all(self, table: str, filters: dict | None = None, order: str | None = None, limit: int | None = None) -> list[dict]:
        q = await self._table(table)
        q = q.select('*')
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
        result = await q.execute()
        return result.data[0] if result.data else None

    async def create(self, table: str, data: dict) -> dict:
        q = await self._table(table)
        result = await q.insert(data).execute()
        return result.data[0]

    async def update(self, table: str, id: str, data: dict) -> dict:
        q = await self._table(table)
        q = q.update(data).eq('id', id)
        result = await q.execute()
        return result.data[0] if result.data else None

    async def soft_delete(self, table: str, id: str) -> None:
        from datetime import datetime, timezone
        q = await self._table(table)
        q = q.update({'deleted_at': datetime.now(timezone.utc).isoformat()}).eq('id', id)
        await q.execute()
