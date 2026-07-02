from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.core.supabase_client import get_user_client


async def create_session(user_id: str, title: str = 'New Chat', token: str | None = None) -> dict:
    supabase = await get_user_client(token)
    now = datetime.now(timezone.utc).isoformat()
    data = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'title': title,
        'created_at': now,
        'updated_at': now,
    }
    result = await supabase.table('chat_sessions').insert(data).execute()
    return result.data[0]


async def get_session_by_id(session_id: str, user_id: str, token: str | None = None) -> dict | None:
    supabase = await get_user_client(token)
    result = await supabase.table('chat_sessions').select('*,chat_messages(*)').eq('id', session_id).eq('user_id', user_id).execute()
    return result.data[0] if result.data else None


async def list_sessions(user_id: str, token: str | None = None) -> list[dict]:
    supabase = await get_user_client(token)
    result = await supabase.table('chat_sessions').select('*,chat_messages(count)').eq('user_id', user_id).order('updated_at', desc=True).execute()
    sessions = []
    for s in result.data or []:
        sessions.append({
            'id': s['id'],
            'title': s['title'],
            'created_at': s['created_at'],
            'updated_at': s['updated_at'],
            'message_count': s.get('chat_messages', [{}])[0].get('count', 0) if s.get('chat_messages') else 0,
        })
    return sessions


async def add_message(session_id: str, role: str, content: str | None, token: str | None = None) -> dict:
    supabase = await get_user_client(token)
    now = datetime.now(timezone.utc).isoformat()
    msg_data = {
        'id': str(uuid.uuid4()),
        'session_id': session_id,
        'role': role,
        'content': content,
        'created_at': now,
    }
    msg_result = await supabase.table('chat_messages').insert(msg_data).execute()
    await supabase.table('chat_sessions').update({'updated_at': now}).eq('id', session_id).execute()
    return msg_result.data[0]


async def delete_session(session_id: str, user_id: str, token: str | None = None) -> bool:
    supabase = await get_user_client(token)
    await supabase.table('chat_messages').delete().eq('session_id', session_id).execute()
    result = await supabase.table('chat_sessions').delete().eq('id', session_id).eq('user_id', user_id).execute()
    return len(result.data) > 0
