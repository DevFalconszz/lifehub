import asyncio
from fastapi import APIRouter, Depends
from app.core.auth.dependencies import get_current_user, get_token
from app.modules.projects.service import ProjectService
from app.modules.notes.service import NoteService
from app.modules.finances.service import FinanceService
from app.modules.calendar.service import CalendarService
from app.modules.readings.service import ReadingService

router = APIRouter(prefix='/api/dashboard', tags=['dashboard'])


@router.get('')
async def get_dashboard(
    month: int,
    year: int,
    user: dict = Depends(get_current_user),
    token: str = Depends(get_token),
):
    project_service = ProjectService(user_id=user['id'], token=token)
    note_service = NoteService(user_id=user['id'], token=token)
    finance_service = FinanceService(user_id=user['id'], token=token)
    calendar_service = CalendarService(user_id=user['id'], token=token)
    reading_service = ReadingService(user_id=user['id'], token=token)

    # Fetch all data concurrently using asyncio.gather to minimize latency
    projects_task = project_service.list_projects()
    tasks_task = project_service.list_tasks()
    notes_task = note_service.list_notes()
    transactions_task = finance_service.list_transactions(month=month, year=year)
    events_task = calendar_service.list_events()
    readings_task = reading_service.list_items()
    summary_task = finance_service.get_summary(month, year)

    projects, tasks, notes, transactions, events, readings, summary = await asyncio.gather(
        projects_task,
        tasks_task,
        notes_task,
        transactions_task,
        events_task,
        readings_task,
        summary_task,
        return_exceptions=True
    )

    # Fallback to empty defaults in case of error
    projects = projects if isinstance(projects, list) else []
    tasks = tasks if isinstance(tasks, list) else []
    notes = notes if isinstance(notes, list) else []
    transactions = transactions if isinstance(transactions, list) else []
    events = events if isinstance(events, list) else []
    readings = readings if isinstance(readings, list) else []
    summary = summary if not isinstance(summary, Exception) else None

    # Optimize project task counts
    from collections import Counter
    task_counts = Counter(t['project_id'] for t in tasks if t.get('project_id'))
    for p in projects:
        p['task_count'] = task_counts.get(p['id'], 0)

    return {
        'projects': {'data': projects},
        'tasks': {'data': tasks},
        'notes': {'data': notes},
        'transactions': {'data': transactions},
        'events': {'data': events},
        'readings': {'data': readings},
        'summary': summary
    }
