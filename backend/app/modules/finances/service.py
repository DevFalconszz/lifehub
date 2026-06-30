from sqlalchemy import select, func, extract, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.models import User
from app.core.exceptions import NotFoundError
from app.modules.finances.models import Budget, Transaction
from app.modules.finances.types import BudgetCreate, TransactionCreate, TransactionUpdate


class FinanceService:
    def __init__(self, session: AsyncSession, user: User):
        self.session = session
        self.user = user

    async def list_transactions(
        self, type: str | None = None, category: str | None = None, month: int | None = None, year: int | None = None,
        limit: int = 50,
    ) -> list[Transaction]:
        query = select(Transaction).where(
            Transaction.user_id == self.user.id,
            Transaction.deleted_at.is_(None),
        )
        if type:
            query = query.where(Transaction.type == type)
        if category:
            query = query.where(Transaction.category == category)
        if month:
            query = query.where(extract('month', Transaction.date) == month)
        if year:
            query = query.where(extract('year', Transaction.date) == year)
        query = query.order_by(Transaction.date.desc()).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_transaction(self, data: TransactionCreate) -> Transaction:
        t = Transaction(
            amount=data.amount, type=data.type, category=data.category,
            description=data.description, date=data.date, account=data.account,
            tags=data.tags if data.tags else None,
            user_id=self.user.id,
        )
        self.session.add(t)
        await self.session.flush()
        await self.session.refresh(t)
        return t

    async def delete_transaction(self, transaction_id: str) -> None:
        result = await self.session.execute(
            select(Transaction).where(
                Transaction.id == transaction_id,
                Transaction.user_id == self.user.id,
                Transaction.deleted_at.is_(None),
            ),
        )
        t = result.scalar_one_or_none()
        if not t:
            raise NotFoundError('Transaction not found')
        t.deleted_at = func.now()
        await self.session.flush()

    async def get_summary(self, month: int, year: int) -> dict:
        query = select(
            func.coalesce(func.sum(Transaction.amount).filter(Transaction.type == 'income'), 0),
            func.coalesce(func.sum(Transaction.amount).filter(Transaction.type == 'expense'), 0),
        ).where(
            Transaction.user_id == self.user.id,
            Transaction.deleted_at.is_(None),
            extract('month', Transaction.date) == month,
            extract('year', Transaction.date) == year,
        )
        result = await self.session.execute(query)
        income, expense = result.one()
        return {
            'month': month, 'year': year,
            'income': float(income), 'expense': float(expense),
            'balance': float(income) - float(expense),
        }

    async def set_budget(self, data: BudgetCreate) -> Budget:
        budget = Budget(
            category=data.category, limit_amount=data.limit_amount,
            month=data.month, year=data.year, user_id=self.user.id,
        )
        self.session.add(budget)
        await self.session.flush()
        await self.session.refresh(budget)
        return budget

    async def get_budgets(self, month: int, year: int) -> list[dict]:
        result = await self.session.execute(
            select(Budget).where(
                Budget.user_id == self.user.id,
                Budget.month == month,
                Budget.year == year,
                Budget.deleted_at.is_(None),
            ),
        )
        budgets = result.scalars().all()
        result_list = []
        for b in budgets:
            spent_result = await self.session.execute(
                select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                    Transaction.user_id == self.user.id,
                    Transaction.deleted_at.is_(None),
                    Transaction.category == b.category,
                    Transaction.type == 'expense',
                    extract('month', Transaction.date) == month,
                    extract('year', Transaction.date) == year,
                ),
            )
            spent = float(spent_result.scalar())
            result_list.append({
                'id': str(b.id), 'category': b.category,
                'limit_amount': float(b.limit_amount),
                'month': b.month, 'year': b.year, 'spent': spent,
            })
        return result_list
