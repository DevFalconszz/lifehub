from contextlib import asynccontextmanager

import strawberry
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from strawberry.fastapi import GraphQLRouter

from app.config import get_settings
from app.core.auth.router import router as auth_router
from app.core.exceptions import AppError
from app.database import engine
from app.core.models import Base

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        from app.core.auth.models import User
        from app.modules.projects.models import Project, Task
        from app.modules.notes.models import Note, NoteLink
        from app.modules.finances.models import Transaction, Budget
        from app.modules.calendar.models import Event
        from app.modules.readings.models import ReadingItem
        from app.modules.ai.models import ChatSession, ChatMessage
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={'error': {'type': exc.error_type, 'message': exc.message}},
    )


app.include_router(auth_router, prefix='/api')

from app.modules.projects.router import router as projects_router, task_router
app.include_router(projects_router)
app.include_router(task_router)

from app.modules.notes.router import router as notes_router
app.include_router(notes_router)

from app.modules.finances.router import router as finances_router
app.include_router(finances_router)

from app.modules.calendar.router import router as calendar_router
app.include_router(calendar_router)

from app.modules.readings.router import router as readings_router
app.include_router(readings_router)

from app.modules.ai.router import router as ai_router
app.include_router(ai_router)


@strawberry.type
class Query:
    @strawberry.field
    def health(self) -> str:
        return 'ok'


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema, graphql_ide='graphiql')
app.include_router(graphql_app, prefix='/api/graphql')


@app.get('/api/health')
async def health():
    return {'status': 'ok'}
