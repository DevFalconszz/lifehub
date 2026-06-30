from __future__ import annotations

import datetime

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    amount: float = Field(..., gt=0)
    type: str = Field(..., pattern='^(income|expense|transfer)$')
    category: str = Field(..., max_length=100)
    description: str | None = None
    date: datetime.date
    account: str = 'wallet'
    tags: list[str] | None = None


class TransactionUpdate(BaseModel):
    amount: float | None = None
    type: str | None = None
    category: str | None = None
    description: str | None = None
    date: datetime.date | None = None
    account: str | None = None
    tags: list[str] | None = None


class TransactionResponse(BaseModel):
    id: str
    amount: float
    type: str
    category: str
    description: str | None
    date: datetime.date
    account: str
    tags: list[str] | None
    created_at: datetime.datetime
    updated_at: datetime.datetime


class BudgetCreate(BaseModel):
    category: str = Field(..., max_length=100)
    limit_amount: float = Field(..., gt=0)
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020)


class BudgetResponse(BaseModel):
    id: str
    category: str
    limit_amount: float
    month: int
    year: int
    spent: float = 0
