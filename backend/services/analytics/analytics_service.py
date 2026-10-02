import logging
from backend.repositories.sqlite.analytics_repository import AnalyticsRepository
from backend.repositories.sqlite.workspace_repository import WorkspaceRepository
from backend.repositories.sqlite.document_repository import DocumentRepository  # FIX P9: moved from inline import

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.analytics_repo = AnalyticsRepository()
        self.workspace_repo = WorkspaceRepository()
        self.doc_repo = DocumentRepository()  # FIX P9: stored as instance variable
        
    def record_query(self, workspace_id: str, model_used: str) -> None:
        try:
            self.analytics_repo.increment_query_count(workspace_id)
            if model_used and "groq" in model_used.lower():
                self.analytics_repo.increment_groq_requests(workspace_id)
            elif model_used and "qwen" in model_used.lower():
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
            # FIX P9: was "chunk_count" (non-existent field) — correct field is "total_chunks"
            total_chunks = sum(d.get("total_chunks", 0) for d in docs)

            self.analytics_repo.update_storage_stats(workspace_id, total_docs, total_chunks, storage_used)
        except Exception as e:
            logger.error(f"Failed to update document analytics stats: {e}")
