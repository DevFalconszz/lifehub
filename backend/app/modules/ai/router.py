from __future__ import annotations

import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import get_current_user
from app.core.auth.models import User
from app.database import get_session
from app.modules.ai import crud
from app.modules.ai.providers.registry import get_provider_registry
from app.modules.ai.schemas import ChatMessageOut, ChatSessionOut, ChatSessionSummary
from app.modules.ai.service import ChatService

router = APIRouter(prefix='/api/ai', tags=['ai'])


class ChatRequest(BaseModel):
    messages: list[dict]
    model: str | None = None
    stream: bool = False
    provider: str = 'openzen'
    session_id: str | None = None


class ChatResponse(BaseModel):
    id: str
    content: str | None
    role: str


async def get_chat_service(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> ChatService:
    return ChatService(
        session=session,
        user=user,
        provider_registry=get_provider_registry(),
    )


@router.post('/chat')
async def chat(
    body: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    if body.stream:
        return StreamingResponse(
            chat_service.chat_stream(
                messages=body.messages,
                model=body.model,
                provider_key=body.provider,
            ),
            media_type='text/event-stream',
        )

    result = await chat_service.chat(
        messages=body.messages,
        model=body.model,
        provider_key=body.provider,
    )

    choice = result['choices'][0]
    content = choice['message'].get('content')

    return ChatResponse(
        id=result['id'],
        content=content,
        role='assistant',
    )


@router.get('/sessions', response_model=list[ChatSessionSummary])
async def list_sessions(
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    return await crud.list_sessions(db, user)


class CreateSessionBody(BaseModel):
    title: str = 'New Chat'


@router.post('/sessions', response_model=ChatSessionOut)
async def create_session(
    body: CreateSessionBody = CreateSessionBody(),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    session = await crud.create_session(db, user, body.title)
    return session


@router.get('/sessions/{session_id}', response_model=ChatSessionOut)
async def get_session_by_id(
    session_id: UUID,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    session = await crud.get_session_by_id(db, session_id, user)
    if not session:
        raise HTTPException(404, 'Session not found')
    return session


@router.delete('/sessions/{session_id}', status_code=204)
async def delete_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    deleted = await crud.delete_session(db, session_id, user)
    if not deleted:
        raise HTTPException(404, 'Session not found')
    return None


@router.post('/sessions/{session_id}/messages', response_model=ChatMessageOut)
async def add_message(
    session_id: UUID,
    body: ChatRequest,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    session = await crud.get_session_by_id(db, session_id, user)
    if not session:
        raise HTTPException(404, 'Session not found')

    last_msg = body.messages[-1] if body.messages else None
    if last_msg and last_msg.get('role') in ('user', 'assistant'):
        msg = await crud.add_message(db, session_id, last_msg['role'], last_msg.get('content'))
        return msg

    raise HTTPException(400, 'No valid message to save')


@router.get('/providers')
async def list_providers():
    return {'data': get_provider_registry().list_available()}


@router.get('/tools')
async def list_tools(
    chat_service: ChatService = Depends(get_chat_service),
):
    tools = chat_service.tool_registry.build_openai_tools()
    return {'data': tools}
