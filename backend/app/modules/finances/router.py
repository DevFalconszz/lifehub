from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import get_current_user
from app.core.auth.models import User
from app.database import get_session
from app.modules.finances.service import FinanceService
from app.modules.finances.types import (
    BudgetCreate, BudgetResponse, TransactionCreate, TransactionResponse,
)

router = APIRouter(prefix='/api/finances', tags=['finances'])


async def get_service(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> FinanceService:
    return FinanceService(session, user)


@router.get('/transactions')
async def list_transactions(
    type: str | None = None,
    category: str | None = None,
    month: int | None = Query(None, ge=1, le=12),
    year: int | None = None,
    service: FinanceService = Depends(get_service),
):
    transactions = await service.list_transactions(
        type=type, category=category, month=month, year=year,
    )
    return {'data': [
        TransactionResponse(
            id=str(t.id), amount=float(t.amount), type=t.type,
            category=t.category, description=t.description,
            date=t.date, account=t.account, tags=t.tags,
            created_at=t.created_at, updated_at=t.updated_at,
        ) for t in transactions
    ]}


@router.post('/transactions', status_code=201)
async def create_transaction(
    body: TransactionCreate,
    service: FinanceService = Depends(get_service),
):
    t = await service.create_transaction(body)
    return TransactionResponse(
        id=str(t.id), amount=float(t.amount), type=t.type,
        category=t.category, description=t.description,
        date=t.date, account=t.account, tags=t.tags,
        created_at=t.created_at, updated_at=t.updated_at,
    )


@router.delete('/transactions/{transaction_id}', status_code=204)
async def delete_transaction(
    transaction_id: str,
    service: FinanceService = Depends(get_service),
):
    await service.delete_transaction(transaction_id)


@router.get('/summary')
async def get_summary(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(...),
    service: FinanceService = Depends(get_service),
):
    return await service.get_summary(month, year)


@router.get('/budgets')
async def get_budgets(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(...),
    service: FinanceService = Depends(get_service),
):
    return {'data': await service.get_budgets(month, year)}


@router.post('/budgets', status_code=201)
async def set_budget(
    body: BudgetCreate,
    service: FinanceService = Depends(get_service),
):
    b = await service.set_budget(body)
    return BudgetResponse(
        id=str(b.id), category=b.category,
        limit_amount=float(b.limit_amount),
        month=b.month, year=b.year, spent=0,
    )
