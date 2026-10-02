from backend.repositories.sqlite.base_repository import BaseRepository
from datetime import datetime, timezone

class AnalyticsRepository(BaseRepository):
    def init_analytics(self, workspace_id: str) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        self._execute(
            "INSERT INTO analytics (analytics_id, workspace_id, last_updated) VALUES (?, ?, ?)",
            (workspace_id, workspace_id, now) # Using workspace_id as analytics_id since it's 1:1
        )
        return self.get_analytics(workspace_id)

    def get_analytics(self, workspace_id: str) -> dict | None:
        return self._execute(
            "SELECT * FROM analytics WHERE workspace_id = ?",
            (workspace_id,),
            fetch_one=True
        )

    def increment_query_count(self, workspace_id: str):
        now = datetime.now(timezone.utc).isoformat()
        self._execute(
            "UPDATE analytics SET total_queries = total_queries + 1, last_updated = ? WHERE workspace_id = ?",
            (now, workspace_id)
        )

    def increment_groq_requests(self, workspace_id: str):
        now = datetime.now(timezone.utc).isoformat()
        self._execute(
            "UPDATE analytics SET groq_requests = groq_requests + 1, last_updated = ? WHERE workspace_id = ?",
            (now, workspace_id)
        )

    def increment_local_requests(self, workspace_id: str):
        now = datetime.now(timezone.utc).isoformat()
        self._execute(
            "UPDATE analytics SET local_model_requests = local_model_requests + 1, last_updated = ? WHERE workspace_id = ?",
            (now, workspace_id)
        )

    def update_storage_stats(self, workspace_id: str, total_documents: int, total_chunks: int, total_storage_mb: float):
        now = datetime.now(timezone.utc).isoformat()
        self._execute(
            "UPDATE analytics SET total_documents = ?, total_chunks = ?, total_storage_mb = ?, last_updated = ? WHERE workspace_id = ?",
            (total_documents, total_chunks, total_storage_mb, now, workspace_id)
        )
