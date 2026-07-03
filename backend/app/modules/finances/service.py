from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.core.supabase_client import SupabaseService


class FinanceService(SupabaseService):
    async def list_transactions(
        self, type: str | None = None, category: str | None = None,
        month: int | None = None, year: int | None = None, limit: int = 50,
    ) -> list[dict]:
        q = await self._table('transactions')
        q = q.select('*')
        q = self._user_filter(q)
        if type:
            q = q.eq('type', type)
        if category:
            q = q.eq('category', category)
        
        # Apply date filters at database level for indexing and performance
        if month and year:
            start_date = f"{year}-{month:02d}-01T00:00:00"
            if month == 12:
                end_date = f"{year + 1}-01-01T00:00:00"
            else:
                end_date = f"{year}-{month + 1:02d}-01T00:00:00"
            q = q.gte('date', start_date).lt('date', end_date)
        elif year:
            q = q.gte('date', f"{year}-01-01T00:00:00").lt('date', f"{year + 1}-01-01T00:00:00")

        q = q.order('date', desc=True)
        
        # Only limit if we are not fetching a full month/year report (where totals matter)
        if not (month or year):
            q = q.limit(limit)
            
        result = await q.execute()
        return result.data or []

    def _get_month(self, date_str: str) -> int:
        try:
            return datetime.fromisoformat(date_str).month
        except (ValueError, TypeError):
            return 1

    def _get_year(self, date_str: str) -> int:
        try:
            return datetime.fromisoformat(date_str).year
        except (ValueError, TypeError):
            return 2026

    async def create_transaction(self, data: dict) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        return await self.create('transactions', {
            'id': str(uuid.uuid4()),
            'user_id': self._user_id,
            'created_at': now,
            'updated_at': now,
            **data,
        })

    async def delete_transaction(self, transaction_id: str) -> None:
        await self.soft_delete('transactions', transaction_id)

    async def get_summary(self, month: int, year: int) -> dict:
        transactions = await self.list_transactions(month=month, year=year)
        income = sum(t['amount'] for t in transactions if t.get('type') == 'income')
        expense = sum(t['amount'] for t in transactions if t.get('type') == 'expense')
        return {
            'month': month,
            'year': year,
            'income': income,
            'expense': expense,
            'balance': income - expense,
        }

    async def set_budget(self, data: dict) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        return await self.create('budgets', {
            'id': str(uuid.uuid4()),
            'user_id': self._user_id,
            'created_at': now,
            'updated_at': now,
            **data,
        })

    async def get_budgets(self, month: int, year: int) -> list[dict]:
        budgets = await self.list_all('budgets', filters={
            'month': month,
            'year': year,
        })
        transactions = await self.list_transactions(month=month, year=year)

        result = []
        for b in budgets:
            spent = sum(
                t['amount'] for t in transactions
                if t.get('type') == 'expense' and t.get('category') == b['category']
            )
            result.append({
                'id': b['id'],
                'category': b['category'],
                'limit_amount': float(b['limit_amount']),
                'month': b['month'],
                'year': b['year'],
                'spent': spent,
            })
        return result
