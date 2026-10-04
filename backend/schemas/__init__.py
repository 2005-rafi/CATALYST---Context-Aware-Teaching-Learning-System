"""
Centralized Pydantic Request / Response DTO Schemas for all API endpoints.
"""
from backend.schemas.workspaces import (
    CreateWorkspaceRequest,
    WorkspaceResponse,
    WorkspaceListResponse,
    DeleteWorkspaceResponse,
)
from backend.schemas.documents import (
    DocumentUploadResponse,
    DocumentStatusResponse,
    DocumentListResponse,
)
from backend.schemas.chat import (
    ChatRequest,
    ChatResponse,
    SourceChunk,
    FigureReference,
)
from backend.schemas.analytics import (
    AnalyticsResponse,
    DetailedAnalyticsResponse,
    DailyActivityPoint,
    TopicMasteryItem,
    DocumentMetricItem,
    FigureMetricSummary,
)
from backend.schemas.sessions import (
    CreateSessionRequest,
    RenameSessionRequest,
    SessionResponse,
    SessionListResponse,
)
from backend.schemas.system import (
    HealthResponse,
)
from backend.schemas.memory import (
    ProfileResponse,
)
from backend.schemas.figures import (
    FigureMetadataResponse,
    DocumentFiguresResponse,
    FigureItem,
)

__all__ = [
    "CreateWorkspaceRequest",
    "WorkspaceResponse",
    "WorkspaceListResponse",
    "DeleteWorkspaceResponse",
    "DocumentUploadResponse",
    "DocumentStatusResponse",
    "DocumentListResponse",
    "ChatRequest",
    "ChatResponse",
    "SourceChunk",
    "FigureReference",
    "AnalyticsResponse",
    "DetailedAnalyticsResponse",
    "DailyActivityPoint",
    "TopicMasteryItem",
    "DocumentMetricItem",
    "FigureMetricSummary",
    "CreateSessionRequest",
    "RenameSessionRequest",
    "SessionResponse",
    "SessionListResponse",
    "HealthResponse",
    "ProfileResponse",
    "FigureMetadataResponse",
    "DocumentFiguresResponse",
    "FigureItem",
]
