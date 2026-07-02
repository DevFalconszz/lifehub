from fastapi import APIRouter, Depends

from app.core.auth.dependencies import get_current_user
from app.modules.projects.service import ProjectService
from app.modules.projects.types import ProjectCreate, ProjectUpdate, TaskCreate, TaskUpdate

router = APIRouter(prefix='/api/projects', tags=['projects'])
task_router = APIRouter(prefix='/api/tasks', tags=['tasks'])


def get_service(user: dict = Depends(get_current_user)) -> ProjectService:
    return ProjectService(user_id=user['id'])


@router.get('')
async def list_projects(service: ProjectService = Depends(get_service)):
    projects = await service.list_projects()
    result = []
    for p in projects:
        tasks = await service.list_tasks(project_id=p['id'])
        p['task_count'] = len(tasks)
        result.append(p)
    return {'data': result}


@router.get('/{project_id}')
async def get_project(project_id: str, service: ProjectService = Depends(get_service)):
    p = await service.get_project(project_id)
    tasks = await service.list_tasks(project_id=project_id)
    p['task_count'] = len(tasks)
    return p


@router.post('', status_code=201)
async def create_project(body: ProjectCreate, service: ProjectService = Depends(get_service)):
    return await service.create_project(body.model_dump(exclude_unset=True))


@router.patch('/{project_id}')
async def update_project(project_id: str, body: ProjectUpdate, service: ProjectService = Depends(get_service)):
    return await service.update_project(project_id, body.model_dump(exclude_unset=True))


@router.delete('/{project_id}', status_code=204)
async def delete_project(project_id: str, service: ProjectService = Depends(get_service)):
    await service.delete_project(project_id)


@router.get('/{project_id}/tasks')
async def list_tasks(project_id: str, service: ProjectService = Depends(get_service)):
    tasks = await service.list_tasks(project_id=project_id)
    return {'data': tasks}


@router.post('/{project_id}/tasks', status_code=201)
async def create_task(project_id: str, body: TaskCreate, service: ProjectService = Depends(get_service)):
    data = body.model_dump(exclude_unset=True)
    data['project_id'] = project_id
    return await service.create_task(data)


@router.patch('/{project_id}/tasks/{task_id}')
async def update_task(project_id: str, task_id: str, body: TaskUpdate, service: ProjectService = Depends(get_service)):
    return await service.update_task(task_id, body.model_dump(exclude_unset=True))


@router.delete('/{project_id}/tasks/{task_id}', status_code=204)
async def delete_task(project_id: str, task_id: str, service: ProjectService = Depends(get_service)):
    await service.delete_task(task_id)


@task_router.get('')
async def list_all_tasks(service: ProjectService = Depends(get_service)):
    tasks = await service.list_tasks()
    return {'data': tasks}


@task_router.post('', status_code=201)
async def create_task_no_project(body: TaskCreate, service: ProjectService = Depends(get_service)):
    return await service.create_task(body.model_dump(exclude_unset=True))
