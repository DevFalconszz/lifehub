from fastapi import APIRouter, Depends

from app.core.auth.dependencies import get_current_user
from app.modules.readings.service import ReadingService
from app.modules.readings.types import ReadingCreate, ReadingUpdate

router = APIRouter(prefix='/api/readings', tags=['readings'])


def get_service(user: dict = Depends(get_current_user)) -> ReadingService:
    return ReadingService(user_id=user['id'])


@router.get('')
async def list_items(status: str | None = None, type: str | None = None, service: ReadingService = Depends(get_service)):
    items = await service.list_items(status=status, type=type)
    return {'data': items}


@router.get('/{item_id}')
async def get_item(item_id: str, service: ReadingService = Depends(get_service)):
    return await service.get_item(item_id)


@router.post('', status_code=201)
async def create_item(body: ReadingCreate, service: ReadingService = Depends(get_service)):
    return await service.create_item(body.model_dump(exclude_unset=True))


@router.patch('/{item_id}')
async def update_item(item_id: str, body: ReadingUpdate, service: ReadingService = Depends(get_service)):
    return await service.update_item(item_id, body.model_dump(exclude_unset=True))


@router.delete('/{item_id}', status_code=204)
async def delete_item(item_id: str, service: ReadingService = Depends(get_service)):
    await service.delete_item(item_id)
