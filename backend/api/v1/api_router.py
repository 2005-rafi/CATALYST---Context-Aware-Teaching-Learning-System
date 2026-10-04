"""
Central API v1 Router consolidating all resource endpoints.
"""
from fastapi import APIRouter
from backend.api.v1.endpoints.workspaces import router as workspaces_router
from backend.api.v1.endpoints.documents import router as documents_router
from backend.api.v1.endpoints.chat import router as chat_router
from backend.api.v1.endpoints.analytics import router as analytics_router
from backend.api.v1.endpoints.sessions import router as sessions_router
from backend.api.v1.endpoints.figures import router as figures_router
from backend.api.v1.endpoints.memory import router as memory_router
from backend.api.v1.endpoints.system import router as system_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(workspaces_router)
api_router.include_router(documents_router)
api_router.include_router(chat_router)
api_router.include_router(analytics_router)
api_router.include_router(sessions_router)
api_router.include_router(figures_router)
api_router.include_router(memory_router)
api_router.include_router(system_router)
