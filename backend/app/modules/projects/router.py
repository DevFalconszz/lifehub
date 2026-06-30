from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import get_current_user
from app.core.auth.models import User
from app.database import get_session
from app.modules.projects.service import ProjectService
from app.modules.projects.types import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)

router = APIRouter(prefix='/api/projects', tags=['projects'])


async def get_service(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> ProjectService:
    return ProjectService(session, user)


@router.get('')
async def list_projects(service: ProjectService = Depends(get_service)):
    projects = await service.list_projects()
    result = []
    for p in projects:
        tasks = await service.list_tasks(project_id=str(p.id))
        result.append(ProjectResponse(
            id=str(p.id), name=p.name, description=p.description,
            color=p.color, status=p.status, priority=p.priority,
            category=p.category, progress=p.progress,
            start_at=p.start_at, target_at=p.target_at, url=p.url,
            created_at=p.created_at, updated_at=p.updated_at,
            task_count=len(tasks),
        ))
    return {'data': result}


@router.get('/{project_id}')
async def get_project(project_id: str, service: ProjectService = Depends(get_service)):
    p = await service.get_project(project_id)
    tasks = await service.list_tasks(project_id=project_id)
    return ProjectResponse(
        id=str(p.id), name=p.name, description=p.description,
        color=p.color, status=p.status, priority=p.priority,
        category=p.category, progress=p.progress,
        start_at=p.start_at, target_at=p.target_at, url=p.url,
        created_at=p.created_at, updated_at=p.updated_at,
        task_count=len(tasks),
    )


@router.post('', status_code=201)
async def create_project(body: ProjectCreate, service: ProjectService = Depends(get_service)):
    p = await service.create_project(body)
    return ProjectResponse(
        id=str(p.id), name=p.name, description=p.description,
        color=p.color, status=p.status, priority=p.priority,
        category=p.category, progress=p.progress,
        start_at=p.start_at, target_at=p.target_at, url=p.url,
        created_at=p.created_at, updated_at=p.updated_at,
    )


@router.patch('/{project_id}')
async def update_project(
    project_id: str, body: ProjectUpdate,
    service: ProjectService = Depends(get_service),
):
    p = await service.update_project(project_id, body)
    return ProjectResponse(
        id=str(p.id), name=p.name, description=p.description,
        color=p.color, status=p.status, priority=p.priority,
        category=p.category, progress=p.progress,
        start_at=p.start_at, target_at=p.target_at, url=p.url,
        created_at=p.created_at, updated_at=p.updated_at,
    )


@router.delete('/{project_id}', status_code=204)
async def delete_project(project_id: str, service: ProjectService = Depends(get_service)):
    await service.delete_project(project_id)


@router.get('/{project_id}/tasks')
async def list_tasks(project_id: str, service: ProjectService = Depends(get_service)):
    tasks = await service.list_tasks(project_id=project_id)
    return {'data': [
        TaskResponse(
            id=str(t.id), title=t.title, description=t.description,
            status=t.status, priority=t.priority, due_at=t.due_at,
            position=t.position, project_id=str(t.project_id) if t.project_id else None,
            created_at=t.created_at, updated_at=t.updated_at,
        ) for t in tasks
    ]}


@router.post('/{project_id}/tasks', status_code=201)
async def create_task(
    project_id: str, body: TaskCreate,
    service: ProjectService = Depends(get_service),
):
    body.project_id = project_id
    t = await service.create_task(body)
    return TaskResponse(
        id=str(t.id), title=t.title, description=t.description,
        status=t.status, priority=t.priority, due_at=t.due_at,
        position=t.position, project_id=str(t.project_id) if t.project_id else None,
        created_at=t.created_at, updated_at=t.updated_at,
    )


@router.patch('/{project_id}/tasks/{task_id}')
async def update_task(
    project_id: str, task_id: str, body: TaskUpdate,
    service: ProjectService = Depends(get_service),
):
    t = await service.update_task(task_id, body)
    return TaskResponse(
        id=str(t.id), title=t.title, description=t.description,
        status=t.status, priority=t.priority, due_at=t.due_at,
        position=t.position, project_id=str(t.project_id) if t.project_id else None,
        created_at=t.created_at, updated_at=t.updated_at,
    )


@router.delete('/{project_id}/tasks/{task_id}', status_code=204)
async def delete_task(
    project_id: str, task_id: str,
    service: ProjectService = Depends(get_service),
):
    await service.delete_task(task_id)


task_router = APIRouter(prefix='/api/tasks', tags=['tasks'])


@task_router.get('')
async def list_all_tasks(service: ProjectService = Depends(get_service)):
    tasks = await service.list_tasks()
    return {'data': [
        TaskResponse(
            id=str(t.id), title=t.title, description=t.description,
            status=t.status, priority=t.priority, due_at=t.due_at,
            position=t.position, project_id=str(t.project_id) if t.project_id else None,
            created_at=t.created_at, updated_at=t.updated_at,
        ) for t in tasks
    ]}


@task_router.post('', status_code=201)
async def create_task_no_project(
    body: TaskCreate,
    service: ProjectService = Depends(get_service),
):
    t = await service.create_task(body)
    return TaskResponse(
        id=str(t.id), title=t.title, description=t.description,
        status=t.status, priority=t.priority, due_at=t.due_at,
        position=t.position, project_id=str(t.project_id) if t.project_id else None,
        created_at=t.created_at, updated_at=t.updated_at,
    )
