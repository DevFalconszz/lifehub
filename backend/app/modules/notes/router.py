from fastapi import APIRouter, Depends

from app.core.auth.dependencies import get_current_user, get_token
from app.modules.notes.service import NoteService
from app.modules.notes.types import NoteCreate, NoteUpdate

router = APIRouter(prefix='/api/notes', tags=['notes'])


def get_service(
    user: dict = Depends(get_current_user),
    token: str = Depends(get_token),
) -> NoteService:
    return NoteService(user_id=user['id'], token=token)


@router.get('')
async def list_notes(pinned: bool = False, service: NoteService = Depends(get_service)):
    notes = await service.list_notes(pinned_only=pinned)
    return {'data': notes}


@router.get('/{note_id}')
async def get_note(note_id: str, service: NoteService = Depends(get_service)):
    return await service.get_note(note_id)


@router.post('', status_code=201)
async def create_note(body: NoteCreate, service: NoteService = Depends(get_service)):
    return await service.create_note(body.model_dump(exclude_unset=True))


@router.patch('/{note_id}')
async def update_note(note_id: str, body: NoteUpdate, service: NoteService = Depends(get_service)):
    return await service.update_note(note_id, body.model_dump(exclude_unset=True))


@router.delete('/{note_id}', status_code=204)
async def delete_note(note_id: str, service: NoteService = Depends(get_service)):
    await service.delete_note(note_id)
