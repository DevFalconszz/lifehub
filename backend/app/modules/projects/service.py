import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.models import User
from app.core.exceptions import NotFoundError
from app.modules.projects.models import Project, Task
from app.modules.projects.types import ProjectCreate, ProjectUpdate, TaskCreate, TaskUpdate


class ProjectService:
    def __init__(self, session: AsyncSession, user: User):
        self.session = session
        self.user = user

    async def list_projects(self) -> list[Project]:
        result = await self.session.execute(
            select(Project)
            .where(Project.user_id == self.user.id, Project.deleted_at.is_(None))
            .order_by(Project.created_at.desc()),
        )
        return result.scalars().all()

    async def get_project(self, project_id: str) -> Project:
        result = await self.session.execute(
            select(Project).where(
                Project.id == project_id,
                Project.user_id == self.user.id,
                Project.deleted_at.is_(None),
            ),
        )
        project = result.scalar_one_or_none()
        if not project:
            raise NotFoundError('Project not found')
        return project

    async def create_project(self, data: ProjectCreate) -> Project:
        project = Project(
            name=data.name,
            description=data.description,
            color=data.color,
            status=data.status,
            priority=data.priority,
            category=data.category,
            progress=data.progress,
            start_at=data.start_at,
            target_at=data.target_at,
            url=data.url,
            user_id=self.user.id,
        )
        self.session.add(project)
        await self.session.flush()
        await self.session.refresh(project)
        return project

    async def update_project(self, project_id: str, data: ProjectUpdate) -> Project:
        project = await self.get_project(project_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(project, key, value)
        await self.session.flush()
        await self.session.refresh(project)
        return project

    async def delete_project(self, project_id: str) -> None:
        project = await self.get_project(project_id)
        project.deleted_at = func.now()
        await self.session.flush()

    async def list_tasks(self, project_id: str | None = None) -> list[Task]:
        query = select(Task).where(
            Task.user_id == self.user.id,
            Task.deleted_at.is_(None),
        )
        if project_id:
            query = query.where(Task.project_id == project_id)
        query = query.order_by(Task.position, Task.created_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_task(self, task_id: str) -> Task:
        result = await self.session.execute(
            select(Task).where(
                Task.id == task_id,
                Task.user_id == self.user.id,
                Task.deleted_at.is_(None),
            ),
        )
        task = result.scalar_one_or_none()
        if not task:
            raise NotFoundError('Task not found')
        return task

    async def create_task(self, data: TaskCreate) -> Task:
        task = Task(
            title=data.title,
            description=data.description,
            status=data.status,
            priority=data.priority,
            due_at=data.due_at,
            position=data.position,
            project_id=uuid.UUID(data.project_id) if data.project_id else None,
            user_id=self.user.id,
        )
        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def update_task(self, task_id: str, data: TaskUpdate) -> Task:
        task = await self.get_task(task_id)
        update_data = data.model_dump(exclude_unset=True)
        if 'project_id' in update_data:
            update_data['project_id'] = (
                uuid.UUID(update_data['project_id']) if update_data['project_id'] else None
            )
        for key, value in update_data.items():
            setattr(task, key, value)
        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def delete_task(self, task_id: str) -> None:
        task = await self.get_task(task_id)
        task.deleted_at = func.now()
        await self.session.flush()
