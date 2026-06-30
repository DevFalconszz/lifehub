from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import get_current_user
from app.core.auth.models import User
from app.database import get_session
from app.modules.notes.service import NoteService
from app.modules.notes.types import NoteCreate, NoteResponse, NoteUpdate

router = APIRouter(prefix='/api/notes', tags=['notes'])


async def get_service(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> NoteService:
    return NoteService(session, user)


@router.get('')
async def list_notes(
    pinned: bool = Query(False),
    service: NoteService = Depends(get_service),
):
    notes = await service.list_notes(pinned_only=pinned)
    return {'data': [
        NoteResponse(
            id=str(n.id), title=n.title, content=n.content,
            is_pinned=n.is_pinned, tags=n.tags,
            created_at=n.created_at, updated_at=n.updated_at,
        ) for n in notes
    ]}


@router.get('/{note_id}')
async def get_note(note_id: str, service: NoteService = Depends(get_service)):
    n = await service.get_note(note_id)
    return NoteResponse(
        id=str(n.id), title=n.title, content=n.content,
        is_pinned=n.is_pinned, tags=n.tags,
        created_at=n.created_at, updated_at=n.updated_at,
    )


@router.post('', status_code=201)
async def create_note(body: NoteCreate, service: NoteService = Depends(get_service)):
    n = await service.create_note(body)
    return NoteResponse(
        id=str(n.id), title=n.title, content=n.content,
        is_pinned=n.is_pinned, tags=n.tags,
        created_at=n.created_at, updated_at=n.updated_at,
    )


@router.patch('/{note_id}')
async def update_note(
    note_id: str, body: NoteUpdate,
    service: NoteService = Depends(get_service),
):
    n = await service.update_note(note_id, body)
    return NoteResponse(
        id=str(n.id), title=n.title, content=n.content,
        is_pinned=n.is_pinned, tags=n.tags,
        created_at=n.created_at, updated_at=n.updated_at,
    )


@router.delete('/{note_id}', status_code=204)
async def delete_note(note_id: str, service: NoteService = Depends(get_service)):
    await service.delete_note(note_id)
