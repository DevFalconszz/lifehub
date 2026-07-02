from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.core.supabase_client import SupabaseService


class FinanceService(SupabaseService):
    async def list_transactions(
        self, type: str | None = None, category: str | None = None,
        month: int | None = None, year: int | None = None, limit: int = 50,
    ) -> list[dict]:
        filters = {}
        if type:
            filters['type'] = type
        if category:
            filters['category'] = category
        if month:
            filters['month'] = month
        if year:
            filters['year'] = year

        q = await self._table('transactions')
        q = q.select('*')
        q = self._user_filter(q)
        if type:
            q = q.eq('type', type)
        if category:
            q = q.eq('category', category)
        if month:
            from sqlalchemy import extract
            # We'll filter in Python for month/year since supabase doesn't support extract
            pass
        if year:
            pass
        q = q.order('date', desc=True).limit(limit)
        result = await q.execute()
        data = result.data or []

        if month:
            data = [t for t in data if self._get_month(t.get('date', '')) == month]
        if year:
            data = [t for t in data if self._get_year(t.get('date', '')) == year]

        return data

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
