from fastapi import APIRouter, Depends, Query

from app.core.auth.dependencies import get_current_user
from app.modules.finances.service import FinanceService
from app.modules.finances.types import TransactionCreate, BudgetCreate

router = APIRouter(prefix='/api/finances', tags=['finances'])


def get_service(user: dict = Depends(get_current_user)) -> FinanceService:
    return FinanceService(user_id=user['id'])


@router.get('/transactions')
async def list_transactions(
    type: str | None = None,
    category: str | None = None,
    month: int | None = Query(None, ge=1, le=12),
    year: int | None = None,
    service: FinanceService = Depends(get_service),
):
    transactions = await service.list_transactions(type=type, category=category, month=month, year=year)
    return {'data': transactions}


@router.post('/transactions', status_code=201)
async def create_transaction(body: TransactionCreate, service: FinanceService = Depends(get_service)):
    return await service.create_transaction(body.model_dump())


@router.delete('/transactions/{transaction_id}', status_code=204)
async def delete_transaction(transaction_id: str, service: FinanceService = Depends(get_service)):
    await service.delete_transaction(transaction_id)


@router.get('/summary')
async def get_summary(month: int, year: int, service: FinanceService = Depends(get_service)):
    return await service.get_summary(month, year)


@router.get('/budgets')
async def get_budgets(month: int, year: int, service: FinanceService = Depends(get_service)):
    return {'data': await service.get_budgets(month, year)}


@router.post('/budgets', status_code=201)
async def set_budget(body: BudgetCreate, service: FinanceService = Depends(get_service)):
    return await service.set_budget(body.model_dump())
