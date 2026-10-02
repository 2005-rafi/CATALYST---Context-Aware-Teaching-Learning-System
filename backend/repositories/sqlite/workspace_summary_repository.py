import uuid
import datetime
from backend.repositories.sqlite.base_repository import BaseRepository

class WorkspaceSummaryRepository(BaseRepository):
    def upsert_summary(self, workspace_id: str, summary_text: str) -> dict:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        # Ensure we keep the old summary_id if it exists, otherwise generate new
        existing = self.get_summary(workspace_id)
        summary_id = existing["summary_id"] if existing else str(uuid.uuid4())
        
        self._execute(
            "INSERT OR REPLACE INTO workspace_summaries (summary_id, workspace_id, summary_text, last_updated) VALUES (?, ?, ?, ?)",
            (summary_id, workspace_id, summary_text, now)
        )
        return self.get_summary(workspace_id)
        
    def get_summary(self, workspace_id: str) -> dict | None:
        return self._execute(
            "SELECT * FROM workspace_summaries WHERE workspace_id = ?",
            (workspace_id,),
            fetch_one=True
        )
        
    def delete_summary(self, workspace_id: str):
        self._execute(
            "DELETE FROM workspace_summaries WHERE workspace_id = ?",
            (workspace_id,)
        )
