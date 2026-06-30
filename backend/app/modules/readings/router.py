from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import get_current_user
from app.core.auth.models import User
from app.database import get_session
from app.modules.readings.service import ReadingService
from app.modules.readings.types import ReadingCreate, ReadingResponse, ReadingUpdate

router = APIRouter(prefix='/api/readings', tags=['readings'])


async def get_service(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> ReadingService:
    return ReadingService(session, user)


@router.get('')
async def list_items(
    status: str | None = None,
    type: str | None = None,
    service: ReadingService = Depends(get_service),
):
    items = await service.list_items(status=status, type=type)
    return {'data': [
        ReadingResponse(
            id=str(i.id), title=i.title, url=i.url, author=i.author,
            type=i.type, status=i.status, notes=i.notes,
            priority=i.priority, created_at=i.created_at,
            updated_at=i.updated_at,
        ) for i in items
    ]}


@router.get('/{item_id}')
async def get_item(item_id: str, service: ReadingService = Depends(get_service)):
    i = await service.get_item(item_id)
    return ReadingResponse(
        id=str(i.id), title=i.title, url=i.url, author=i.author,
        type=i.type, status=i.status, notes=i.notes,
        priority=i.priority, created_at=i.created_at,
        updated_at=i.updated_at,
    )


@router.post('', status_code=201)
async def create_item(body: ReadingCreate, service: ReadingService = Depends(get_service)):
    i = await service.create_item(body)
    return ReadingResponse(
        id=str(i.id), title=i.title, url=i.url, author=i.author,
        type=i.type, status=i.status, notes=i.notes,
        priority=i.priority, created_at=i.created_at,
        updated_at=i.updated_at,
    )


@router.patch('/{item_id}')
async def update_item(
    item_id: str, body: ReadingUpdate,
    service: ReadingService = Depends(get_service),
):
    i = await service.update_item(item_id, body)
    return ReadingResponse(
        id=str(i.id), title=i.title, url=i.url, author=i.author,
        type=i.type, status=i.status, notes=i.notes,
        priority=i.priority, created_at=i.created_at,
        updated_at=i.updated_at,
    )


@router.delete('/{item_id}', status_code=204)
async def delete_item(item_id: str, service: ReadingService = Depends(get_service)):
    await service.delete_item(item_id)
