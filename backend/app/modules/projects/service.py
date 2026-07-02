from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.core.supabase_client import SupabaseService


class ProjectService(SupabaseService):
    async def list_projects(self) -> list[dict]:
        return await self.list_all('projects', order='created_at')

    async def get_project(self, project_id: str) -> dict:
        project = await self.get_by_id('projects', project_id)
        if not project:
            from app.core.exceptions import NotFoundError
            raise NotFoundError('Project not found')
        return project

    async def create_project(self, data: dict) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        return await self.create('projects', {
            'id': str(uuid.uuid4()),
            'user_id': self._user_id,
            'created_at': now,
            'updated_at': now,
            **data,
        })

    async def update_project(self, project_id: str, data: dict) -> dict:
        data['updated_at'] = datetime.now(timezone.utc).isoformat()
        result = await self.update('projects', project_id, data)
        if not result:
            from app.core.exceptions import NotFoundError
            raise NotFoundError('Project not found')
        return result

    async def delete_project(self, project_id: str) -> None:
        await self.soft_delete('projects', project_id)

    async def list_tasks(self, project_id: str | None = None) -> list[dict]:
        filters = {}
        if project_id:
            filters['project_id'] = project_id
        return await self.list_all('tasks', filters=filters, order='position')

    async def get_task(self, task_id: str) -> dict:
        task = await self.get_by_id('tasks', task_id)
        if not task:
            from app.core.exceptions import NotFoundError
            raise NotFoundError('Task not found')
        return task

    async def create_task(self, data: dict) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        return await self.create('tasks', {
            'id': str(uuid.uuid4()),
            'user_id': self._user_id,
            'created_at': now,
            'updated_at': now,
            **data,
        })

    async def update_task(self, task_id: str, data: dict) -> dict:
        data['updated_at'] = datetime.now(timezone.utc).isoformat()
        result = await self.update('tasks', task_id, data)
        if not result:
            from app.core.exceptions import NotFoundError
            raise NotFoundError('Task not found')
        return result

    async def delete_task(self, task_id: str) -> None:
        await self.soft_delete('tasks', task_id)
