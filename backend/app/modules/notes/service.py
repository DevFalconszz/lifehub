import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.models import User
from app.core.exceptions import NotFoundError
from app.modules.notes.models import Note
from app.modules.notes.types import NoteCreate, NoteUpdate


class NoteService:
    def __init__(self, session: AsyncSession, user: User):
        self.session = session
        self.user = user

    async def list_notes(self, pinned_only: bool = False) -> list[Note]:
        query = select(Note).where(
            Note.user_id == self.user.id,
            Note.deleted_at.is_(None),
        )
        if pinned_only:
            query = query.where(Note.is_pinned.is_(True))
        query = query.order_by(Note.is_pinned.desc(), Note.updated_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_note(self, note_id: str) -> Note:
        result = await self.session.execute(
            select(Note).where(
                Note.id == note_id,
                Note.user_id == self.user.id,
                Note.deleted_at.is_(None),
            ),
        )
        note = result.scalar_one_or_none()
        if not note:
            raise NotFoundError('Note not found')
        return note

    async def create_note(self, data: NoteCreate) -> Note:
        note = Note(
            title=data.title,
            content=data.content,
            is_pinned=data.is_pinned,
            tags=data.tags if data.tags else None,
            user_id=self.user.id,
        )
        self.session.add(note)
        await self.session.flush()
        await self.session.refresh(note)
        return note

    async def update_note(self, note_id: str, data: NoteUpdate) -> Note:
        note = await self.get_note(note_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(note, key, value)
        await self.session.flush()
        await self.session.refresh(note)
        return note

    async def delete_note(self, note_id: str) -> None:
        note = await self.get_note(note_id)
        note.deleted_at = func.now()
        await self.session.flush()
