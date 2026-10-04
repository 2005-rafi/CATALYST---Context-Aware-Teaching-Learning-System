"""Analytics and telemetry API endpoints."""
import logging
from fastapi import APIRouter, Depends, Query
from backend.schemas.analytics import AnalyticsResponse, DetailedAnalyticsResponse
from backend.services.analytics.analytics_service import AnalyticsService
from backend.repositories.sqlite.workspace_repository import WorkspaceRepository
from backend.core.exceptions.exceptions import WorkspaceNotFoundException
from backend.core.dependencies import get_analytics_service, get_workspace_repository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/{workspace_id}", response_model=AnalyticsResponse)
def get_analytics(
    workspace_id: str,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
):
    """Get basic usage analytics counters for a workspace."""
    if not workspace_repo.workspace_exists(workspace_id):
        raise WorkspaceNotFoundException()

    stats = analytics_service.analytics_repo.get_analytics(workspace_id)
    if not stats:
        analytics_service.analytics_repo.init_analytics(workspace_id)
        stats = analytics_service.analytics_repo.get_analytics(workspace_id)

    return AnalyticsResponse(
        workspace_id=stats["workspace_id"],
        total_queries=stats.get("total_queries", 0),
        total_documents=stats.get("total_documents", 0),
        total_chunks=stats.get("total_chunks", 0),
        storage_used_mb=stats.get("total_storage_mb", 0.0),
        groq_requests=stats.get("groq_requests", 0),
        local_model_requests=stats.get("local_model_requests", 0),
        last_updated=stats.get("last_updated")
    )


@router.get("/{workspace_id}/detailed", response_model=DetailedAnalyticsResponse)
def get_detailed_analytics(
    workspace_id: str,
    days: int = Query(default=14, ge=1, le=90, description="Days of activity history"),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
):
    """
    Get end-to-end deep telemetry and visual analytics for a workspace.
    Includes daily query velocity, cognitive memory profiles, topic mastery,
    document corpus stats, and extracted visual RAG figures.
    """
    if not workspace_repo.workspace_exists(workspace_id):
        raise WorkspaceNotFoundException()

    try:
        return analytics_service.get_workspace_deep_analytics(workspace_id, days=days)
    except Exception as e:
        logger.error(f"Error fetching detailed analytics for {workspace_id}: {e}")
        raise
