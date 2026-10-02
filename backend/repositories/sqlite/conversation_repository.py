from backend.repositories.sqlite.base_repository import BaseRepository

class ConversationRepository(BaseRepository):
    def save_message(self, message_id: str, workspace_id: str, role: str, message: str, created_at: str, model_used: str = None, retrieval_chunks: int = 0) -> dict:
        self._execute(
            "INSERT INTO conversations (message_id, workspace_id, role, message, model_used, created_at, retrieval_chunks) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (message_id, workspace_id, role, message, model_used, created_at, retrieval_chunks)
        )
        return self._execute("SELECT * FROM conversations WHERE message_id = ?", (message_id,), fetch_one=True)

    def get_recent_messages(self, workspace_id: str, limit: int = 5) -> list[dict]:
        rows = self._execute(
            "SELECT * FROM conversations WHERE workspace_id = ? ORDER BY created_at DESC LIMIT ?",
            (workspace_id, limit),
            fetch_all=True
        )
        return list(reversed(rows))

    def get_all_messages(self, workspace_id: str) -> list[dict]:
        return self._execute(
            "SELECT * FROM conversations WHERE workspace_id = ? ORDER BY created_at ASC",
            (workspace_id,),
            fetch_all=True
        )

    def get_message_count(self, workspace_id: str) -> int:
        row = self._execute(
            "SELECT COUNT(*) as count FROM conversations WHERE workspace_id = ?",
            (workspace_id,),
            fetch_one=True
        )
        return row["count"] if row else 0

    def delete_conversation(self, workspace_id: str):
        self._execute(
            "DELETE FROM conversations WHERE workspace_id = ?",
            (workspace_id,)
        )
