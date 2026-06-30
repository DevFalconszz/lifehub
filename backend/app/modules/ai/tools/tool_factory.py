from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.core.auth.dependencies import get_current_user
from app.core.auth.models import User
from app.modules.ai.providers.registry import ProviderRegistry, get_provider_registry
from app.modules.ai.tools.base import Tool
from app.modules.ai.tools.registry import ToolRegistry
from app.modules.projects.service import ProjectService
from app.modules.projects.types import ProjectCreate, TaskCreate
from app.modules.notes.service import NoteService
from app.modules.notes.types import NoteCreate
from app.modules.finances.service import FinanceService
from app.modules.finances.types import TransactionCreate
from app.modules.calendar.service import CalendarService
from app.modules.calendar.types import EventCreate
from app.modules.readings.service import ReadingService
from app.modules.readings.types import ReadingCreate


def build_tool_registry(
    session: AsyncSession,
    user: User,
) -> ToolRegistry:
    registry = ToolRegistry()

    ps = ProjectService(session, user)
    ns = NoteService(session, user)
    fs = FinanceService(session, user)
    cs = CalendarService(session, user)
    rs = ReadingService(session, user)

    # ── Projects ──
    registry.register(Tool(
        name='create_project',
        description='Create a new project',
        parameters={
            'type': 'object',
            'properties': {
                'name': {'type': 'string', 'description': 'Project name'},
                'description': {'type': 'string', 'description': 'Project description'},
                'color': {'type': 'string', 'description': 'Hex color code'},
                'status': {'type': 'string', 'enum': ['active', 'paused', 'completed', 'archived']},
            },
            'required': ['name'],
        },
        category='projects',
        execute=lambda **kw: ps.create_project(ProjectCreate(**kw)),
    ))

    registry.register(Tool(
        name='list_projects',
        description='List all projects',
        parameters={
            'type': 'object',
            'properties': {},
        },
        category='projects',
        execute=lambda **kw: ps.list_projects(),
    ))

    # ── Tasks ──
    registry.register(Tool(
        name='create_task',
        description='Create a new task',
        parameters={
            'type': 'object',
            'properties': {
                'title': {'type': 'string', 'description': 'Task title'},
                'description': {'type': 'string', 'description': 'Task description'},
                'status': {'type': 'string', 'enum': ['todo', 'in_progress', 'done', 'cancelled']},
                'priority': {'type': 'string', 'enum': ['low', 'medium', 'high', 'urgent']},
                'due_at': {'type': 'string', 'format': 'date-time', 'description': 'ISO 8601 due date'},
            },
            'required': ['title'],
        },
        category='tasks',
        execute=lambda **kw: ps.create_task(TaskCreate(**kw)),
    ))

    registry.register(Tool(
        name='list_tasks',
        description='List all tasks',
        parameters={
            'type': 'object',
            'properties': {
                'status': {'type': 'string', 'enum': ['todo', 'in_progress', 'done', 'cancelled']},
            },
        },
        category='tasks',
        execute=lambda **kw: ps.list_tasks(),
    ))

    registry.register(Tool(
        name='complete_task',
        description='Mark a task as done',
        parameters={
            'type': 'object',
            'properties': {
                'task_id': {'type': 'string', 'description': 'Task ID to complete'},
            },
            'required': ['task_id'],
        },
        category='tasks',
        execute=lambda task_id, **kw: ps.update_task(task_id, type('U', (), {'model_dump': lambda: {'status': 'done'}})()),
    ))

    # ── Notes ──
    registry.register(Tool(
        name='create_note',
        description='Create a new note',
        parameters={
            'type': 'object',
            'properties': {
                'title': {'type': 'string', 'description': 'Note title'},
                'content': {'type': 'string', 'description': 'Note content (markdown)'},
                'tags': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Tags'},
            },
            'required': ['title'],
        },
        category='notes',
        execute=lambda **kw: ns.create_note(NoteCreate(**kw)),
    ))

    registry.register(Tool(
        name='list_notes',
        description='List all notes',
        parameters={'type': 'object', 'properties': {}},
        category='notes',
        execute=lambda **kw: ns.list_notes(),
    ))

    # ── Finances ──
    registry.register(Tool(
        name='add_transaction',
        description='Record a financial transaction',
        parameters={
            'type': 'object',
            'properties': {
                'amount': {'type': 'number', 'description': 'Transaction amount'},
                'type': {'type': 'string', 'enum': ['income', 'expense']},
                'category': {'type': 'string', 'description': 'Category (e.g. Food, Salary, Transport)'},
                'description': {'type': 'string', 'description': 'Description'},
                'date': {'type': 'string', 'format': 'date', 'description': 'Date (YYYY-MM-DD)'},
            },
            'required': ['amount', 'type', 'category', 'date'],
        },
        category='finances',
        execute=lambda **kw: fs.create_transaction(TransactionCreate(**kw)),
    ))

    registry.register(Tool(
        name='get_finance_summary',
        description='Get monthly finance summary (income, expense, balance)',
        parameters={
            'type': 'object',
            'properties': {
                'month': {'type': 'integer', 'description': 'Month (1-12)'},
                'year': {'type': 'integer', 'description': 'Year (e.g. 2026)'},
            },
            'required': ['month', 'year'],
        },
        category='finances',
        execute=lambda **kw: fs.get_summary(**kw),
    ))

    # ── Calendar ──
    registry.register(Tool(
        name='create_event',
        description='Create a calendar event',
        parameters={
            'type': 'object',
            'properties': {
                'title': {'type': 'string', 'description': 'Event title'},
                'start_at': {'type': 'string', 'format': 'date-time', 'description': 'Start time (ISO 8601)'},
                'end_at': {'type': 'string', 'format': 'date-time', 'description': 'End time (ISO 8601)'},
                'description': {'type': 'string', 'description': 'Event description'},
            },
            'required': ['title', 'start_at'],
        },
        category='calendar',
        execute=lambda **kw: cs.create_event(EventCreate(**kw)),
    ))

    # ── Readings ──
    registry.register(Tool(
        name='add_reading',
        description='Add a book/article/link to your reading list',
        parameters={
            'type': 'object',
            'properties': {
                'title': {'type': 'string', 'description': 'Title'},
                'author': {'type': 'string', 'description': 'Author'},
                'type': {'type': 'string', 'enum': ['book', 'article', 'video', 'link', 'idea']},
                'status': {'type': 'string', 'enum': ['unread', 'reading', 'completed', 'archived']},
                'priority': {'type': 'integer', 'description': 'Priority (0-10)'},
            },
            'required': ['title'],
        },
        category='readings',
        execute=lambda **kw: rs.create_item(ReadingCreate(**kw)),
    ))

    return registry
