"""
API v1 Resource Endpoints.
"""
from backend.api.v1.endpoints.workspaces import router as workspaces_router
from backend.api.v1.endpoints.documents import router as documents_router
from backend.api.v1.endpoints.chat import router as chat_router
from backend.api.v1.endpoints.analytics import router as analytics_router
from backend.api.v1.endpoints.sessions import router as sessions_router
from backend.api.v1.endpoints.figures import router as figures_router
from backend.api.v1.endpoints.memory import router as memory_router
from backend.api.v1.endpoints.system import router as system_router

__all__ = [
    "workspaces_router",
    "documents_router",
    "chat_router",
    "analytics_router",
    "sessions_router",
    "figures_router",
    "memory_router",
    "system_router",
]
