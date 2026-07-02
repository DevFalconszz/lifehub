from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.auth.dependencies import get_current_user
from app.modules.ai import crud
from app.modules.ai.providers.registry import get_provider_registry
from app.modules.ai.service import ChatService
from app.modules.ai.tools.tool_factory import build_tool_registry

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


class CreateSessionBody(BaseModel):
    title: str = 'New Chat'


def get_chat_service(user: dict = Depends(get_current_user)) -> ChatService:
    return ChatService(
        user=user,
        provider_registry=get_provider_registry(),
    )


@router.post('/chat')
async def chat(
    body: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
    user: dict = Depends(get_current_user),
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


@router.get('/sessions')
async def list_sessions(user: dict = Depends(get_current_user)):
    return await crud.list_sessions(user['id'])


@router.post('/sessions')
async def create_session(
    body: CreateSessionBody = CreateSessionBody(),
    user: dict = Depends(get_current_user),
):
    return await crud.create_session(user['id'], body.title)


@router.get('/sessions/{session_id}')
async def get_session_by_id(
    session_id: str,
    user: dict = Depends(get_current_user),
):
    session = await crud.get_session_by_id(session_id, user['id'])
    if not session:
        raise HTTPException(404, 'Session not found')
    return session


@router.delete('/sessions/{session_id}', status_code=204)
async def delete_session(
    session_id: str,
    user: dict = Depends(get_current_user),
):
    deleted = await crud.delete_session(session_id, user['id'])
    if not deleted:
        raise HTTPException(404, 'Session not found')


@router.post('/sessions/{session_id}/messages')
async def add_message(
    session_id: str,
    body: ChatRequest,
    user: dict = Depends(get_current_user),
):
    session = await crud.get_session_by_id(session_id, user['id'])
    if not session:
        raise HTTPException(404, 'Session not found')

    last_msg = body.messages[-1] if body.messages else None
    if last_msg and last_msg.get('role') in ('user', 'assistant'):
        return await crud.add_message(session_id, last_msg['role'], last_msg.get('content'))

    raise HTTPException(400, 'No valid message to save')


@router.get('/providers')
async def list_providers():
    return {'data': get_provider_registry().list_available()}


@router.get('/tools')
async def list_tools(user: dict = Depends(get_current_user)):
    registry = build_tool_registry(user['id'])
    tools = registry.build_openai_tools()
    return {'data': tools}
