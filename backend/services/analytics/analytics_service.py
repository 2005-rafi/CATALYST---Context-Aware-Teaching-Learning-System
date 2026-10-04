import logging
from backend.repositories.sqlite.analytics_repository import AnalyticsRepository
from backend.repositories.sqlite.workspace_repository import WorkspaceRepository
from backend.repositories.sqlite.document_repository import DocumentRepository
from backend.schemas.analytics_schemas import (
    DetailedAnalyticsResponse,
    DailyActivityPoint,
    TopicMasteryItem,
    DocumentMetricItem,
    FigureMetricSummary,
)

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.analytics_repo = AnalyticsRepository()
        self.workspace_repo = WorkspaceRepository()
        self.doc_repo = DocumentRepository()
        
    def record_query(self, workspace_id: str, model_used: str) -> None:
        try:
            self.analytics_repo.increment_query_count(workspace_id)
            if model_used and "groq" in model_used.lower():
                self.analytics_repo.increment_groq_requests(workspace_id)
            elif model_used and ("qwen" in model_used.lower() or "ollama" in model_used.lower()):
                self.analytics_repo.increment_local_requests(workspace_id)
        except Exception as e:
            logger.error(f"Failed to record query analytics: {e}")
            
    def update_document_stats(self, workspace_id: str) -> None:
        try:
            workspace = self.workspace_repo.get_workspace(workspace_id)
            if not workspace:
                return

            docs = self.doc_repo.get_documents_by_workspace(workspace_id)
            storage_used = sum(d.get("file_size_mb", 0.0) for d in docs)
            total_docs = len(docs)
            total_chunks = sum(d.get("total_chunks", 0) for d in docs)

            self.analytics_repo.update_storage_stats(workspace_id, total_docs, total_chunks, storage_used)
        except Exception as e:
            logger.error(f"Failed to update document analytics stats: {e}")

    def get_workspace_deep_analytics(self, workspace_id: str, days: int = 14) -> DetailedAnalyticsResponse:
        """
        Gathers core KPI metrics, daily query velocity, cognitive memory profiles,
        document-level chunks and visual figure telemetry into a unified response.
        """
        workspace = self.workspace_repo.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")

        stats = self.analytics_repo.get_analytics(workspace_id)
        if not stats:
            self.analytics_repo.init_analytics(workspace_id)
            stats = self.analytics_repo.get_analytics(workspace_id)

        # Get time-series activity
        activity_data = self.analytics_repo.get_daily_activity(workspace_id, days=days)
        activity_timeline = [DailyActivityPoint(**p) for p in activity_data]

        # Get deep telemetry
        telemetry = self.analytics_repo.get_deep_telemetry(workspace_id)

        topic_items = [TopicMasteryItem(**t) for t in telemetry.get("topic_mastery", [])]
        doc_items = [DocumentMetricItem(**d) for d in telemetry.get("documents", [])]
        fig_summary = FigureMetricSummary(**telemetry.get("figures_summary", {"total_figures": 0, "by_type": {}}))

        return DetailedAnalyticsResponse(
            workspace_id=workspace["workspace_id"],
            workspace_name=workspace.get("workspace_name", "Workspace"),
            created_at=workspace.get("created_at", ""),
            last_updated=stats.get("last_updated"),
            total_queries=stats.get("total_queries", 0),
            total_documents=stats.get("total_documents", len(doc_items)),
            total_chunks=stats.get("total_chunks", sum(d.total_chunks for d in doc_items)),
            storage_used_mb=stats.get("total_storage_mb", sum(d.file_size_mb for d in doc_items)),
            groq_requests=stats.get("groq_requests", 0),
            local_model_requests=stats.get("local_model_requests", 0),
            avg_chunks_per_query=telemetry.get("avg_chunks_per_query", 0.0),
            total_sessions=telemetry.get("total_sessions", 0),
            total_messages=telemetry.get("total_messages", 0),
            learning_style=telemetry.get("learning_style", "balanced"),
            preferred_mode=telemetry.get("preferred_mode", "medium"),
            topic_mastery=topic_items,
            struggle_topics=telemetry.get("struggle_topics", []),
            activity_timeline=activity_timeline,
            documents=doc_items,
            figures_summary=fig_summary,
        )
