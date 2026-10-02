from fastapi import APIRouter, Depends
from backend.schemas.analytics_schemas import AnalyticsResponse
from backend.repositories.sqlite.analytics_repository import AnalyticsRepository
from backend.repositories.sqlite.workspace_repository import WorkspaceRepository
from backend.core.exceptions.exceptions import WorkspaceNotFoundException
from backend.core.dependencies import get_analytics_repository, get_workspace_repository
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/{workspace_id}", response_model=AnalyticsResponse)
def get_analytics(
    workspace_id: str,
    analytics_repo: AnalyticsRepository = Depends(get_analytics_repository),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
):
    """Get usage analytics for a workspace."""
    if not workspace_repo.workspace_exists(workspace_id):
        raise WorkspaceNotFoundException()

    stats = analytics_repo.get_analytics(workspace_id)
    if not stats:
        analytics_repo.init_analytics(workspace_id)
        stats = analytics_repo.get_analytics(workspace_id)

    return AnalyticsResponse(
        workspace_id=stats["workspace_id"],
        total_queries=stats["total_queries"],
        total_documents=stats["total_documents"],
        total_chunks=stats["total_chunks"],
        storage_used_mb=stats.get("total_storage_mb", 0.0),
        groq_requests=stats["groq_requests"],
        local_model_requests=stats["local_model_requests"],
        last_updated=stats["last_updated"]
    )
