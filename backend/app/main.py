from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.action_auth import router as action_auth_router
from app.api.automation import router as automation_router
from app.api.blog import router as blog_router
from app.api.infrastructure import router as infrastructure_router
from app.api.learning import router as learning_router
from app.api.router import router
from app.api.tasks import router as tasks_router
from app.api.walkforward import router as walkforward_router
from app.core.config import get_settings
from app.core.database import create_tables
from app.middleware.action_auth import ActionAuthMiddleware
from app.services.scheduler import start_scheduler, stop_scheduler

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_tables()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title=settings.app_name,
    description="仅用于学习、研究和模拟回测，不连接券商，不执行真实交易。",
    version="0.1.0",
    root_path=settings.root_path,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ActionAuthMiddleware)
app.include_router(router, prefix=settings.api_prefix)
app.include_router(tasks_router, prefix=settings.api_prefix)
app.include_router(infrastructure_router, prefix=settings.api_prefix)
app.include_router(walkforward_router, prefix=settings.api_prefix)
app.include_router(learning_router, prefix=settings.api_prefix)
app.include_router(automation_router, prefix=settings.api_prefix)
app.include_router(blog_router, prefix=settings.api_prefix)
app.include_router(action_auth_router, prefix=settings.api_prefix)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "docs": f"{settings.root_path}/docs",
        "notice": "研究与教学用途，不构成投资建议。",
    }
