from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.models import User
from app.core.exceptions import NotFoundError
from app.modules.readings.models import ReadingItem
from app.modules.readings.types import ReadingCreate, ReadingUpdate


class ReadingService:
    def __init__(self, session: AsyncSession, user: User):
        self.session = session
        self.user = user

    async def list_items(
        self, status: str | None = None, type: str | None = None,
    ) -> list[ReadingItem]:
        query = select(ReadingItem).where(
            ReadingItem.user_id == self.user.id,
            ReadingItem.deleted_at.is_(None),
        )
        if status:
            query = query.where(ReadingItem.status == status)
        if type:
            query = query.where(ReadingItem.type == type)
        query = query.order_by(ReadingItem.priority.desc(), ReadingItem.created_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_item(self, item_id: str) -> ReadingItem:
        result = await self.session.execute(
            select(ReadingItem).where(
                ReadingItem.id == item_id,
                ReadingItem.user_id == self.user.id,
                ReadingItem.deleted_at.is_(None),
            ),
        )
        item = result.scalar_one_or_none()
        if not item:
            raise NotFoundError('Reading item not found')
        return item

    async def create_item(self, data: ReadingCreate) -> ReadingItem:
        item = ReadingItem(
            title=data.title, url=data.url, author=data.author,
            type=data.type, status=data.status, notes=data.notes,
            priority=data.priority, user_id=self.user.id,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def update_item(self, item_id: str, data: ReadingUpdate) -> ReadingItem:
        item = await self.get_item(item_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def delete_item(self, item_id: str) -> None:
        item = await self.get_item(item_id)
        item.deleted_at = func.now()
        await self.session.flush()
