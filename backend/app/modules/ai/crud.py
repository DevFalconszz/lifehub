from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.auth.models import User
from app.modules.ai.models import ChatMessage, ChatSession
from app.modules.ai.schemas import ChatSessionSummary


async def create_session(session: AsyncSession, user: User, title: str = 'New Chat') -> ChatSession:
    cs = ChatSession(user_id=user.id, title=title)
    session.add(cs)
    await session.commit()

    result = await session.execute(
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
        .where(ChatSession.id == cs.id)
    )
    return result.scalar_one()


async def get_session_by_id(session: AsyncSession, session_id: UUID, user: User) -> ChatSession | None:
    result = await session.execute(
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
        .where(ChatSession.id == session_id, ChatSession.user_id == user.id)
    )
    return result.scalar_one_or_none()


async def list_sessions(session: AsyncSession, user: User) -> list[ChatSessionSummary]:
    result = await session.execute(
        select(
            ChatSession.id,
            ChatSession.title,
            ChatSession.created_at,
            ChatSession.updated_at,
            func.count(ChatMessage.id).label('message_count'),
        )
        .outerjoin(ChatMessage, ChatMessage.session_id == ChatSession.id)
        .where(ChatSession.user_id == user.id)
        .group_by(ChatSession.id)
        .order_by(ChatSession.updated_at.desc())
    )
    return [
        ChatSessionSummary(
            id=row.id,
            title=row.title,
            created_at=row.created_at,
            updated_at=row.updated_at,
            message_count=row.message_count,
        )
        for row in result.all()
    ]


async def add_message(
    session: AsyncSession,
    session_id: UUID,
    role: str,
    content: str | None,
) -> ChatMessage:
    msg = ChatMessage(session_id=session_id, role=role, content=content)
    session.add(msg)
    await session.execute(
        update(ChatSession)
        .where(ChatSession.id == session_id)
        .values(updated_at=func.now())
    )
    await session.commit()
    await session.refresh(msg)
    return msg


async def delete_session(session: AsyncSession, session_id: UUID, user: User) -> bool:
    cs = await get_session_by_id(session, session_id, user)
    if not cs:
        return False
    await session.delete(cs)
    await session.commit()
    return True
