from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.core.auth.router import router as auth_router
from app.core.exceptions import AppError
from app.core.supabase_client import close_supabase

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('shutdown')
async def shutdown():
    await close_supabase()


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={'error': {'type': exc.error_type, 'message': exc.message}},
    )


app.include_router(auth_router, prefix='/api')

from app.modules.dashboard.router import router as dashboard_router
app.include_router(dashboard_router)

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


@app.get('/api/health')
async def health():
    return {'status': 'ok'}
