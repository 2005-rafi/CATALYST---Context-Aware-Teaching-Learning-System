"""
backend/core/dependencies.py — Centralized Dependency Injection Container

P1 / P14 FIX: Services were previously instantiated as module-level singletons in
each router file. This breaks testability, lifecycle management, and DI principles.

This module provides @lru_cache-backed singleton factories for every service.
Usage in routers:
    from fastapi import Depends
    from backend.core.dependencies import get_chat_service

    @router.post("/")
    def endpoint(service: ChatService = Depends(get_chat_service)):
        ...

For unit tests, override via FastAPI's dependency_overrides:
    app.dependency_overrides[get_chat_service] = lambda: MockChatService()
"""
from functools import lru_cache


@lru_cache(maxsize=1)
def get_chat_service():
    from backend.services.llm.chat_service import ChatService
    return ChatService()


@lru_cache(maxsize=1)
def get_workspace_service():
    from backend.services.workspace.workspace_service import WorkspaceService
    return WorkspaceService()


@lru_cache(maxsize=1)
def get_ingestion_service():
    from backend.services.document.ingestion_service import IngestionService
    return IngestionService()


@lru_cache(maxsize=1)
def get_upload_service():
    from backend.services.document.upload_service import UploadService
    return UploadService()


@lru_cache(maxsize=1)
def get_document_deletion_service():
    from backend.services.document.document_deletion_service import DocumentDeletionService
    return DocumentDeletionService()


@lru_cache(maxsize=1)
def get_analytics_service():
    from backend.services.analytics.analytics_service import AnalyticsService
    return AnalyticsService()


@lru_cache(maxsize=1)
def get_conversation_repository():
    from backend.repositories.sqlite.conversation_repository import ConversationRepository
    return ConversationRepository()


@lru_cache(maxsize=1)
def get_document_repository():
    from backend.repositories.sqlite.document_repository import DocumentRepository
    return DocumentRepository()


@lru_cache(maxsize=1)
def get_workspace_repository():
    from backend.repositories.sqlite.workspace_repository import WorkspaceRepository
    return WorkspaceRepository()


@lru_cache(maxsize=1)
def get_analytics_repository():
    from backend.repositories.sqlite.analytics_repository import AnalyticsRepository
    return AnalyticsRepository()


@lru_cache(maxsize=1)
def get_health_service():
    from backend.services.system.health_service import HealthService
    return HealthService()
