"""
ConversationRepository — CRUD for the conversations table.
Upgraded with session_id, turn_index, topic_tags, and importance_score support.
"""
import json
from backend.repositories.sqlite.base_repository import BaseRepository


class ConversationRepository(BaseRepository):

    def save_message(
        self,
        message_id: str,
        workspace_id: str,
        role: str,
        message: str,
        created_at: str,
        model_used: str | None = None,
        retrieval_chunks: int = 0,
        session_id: str | None = None,
        turn_index: int = 0,
        topic_tags: list[str] | None = None,
        importance_score: float = 0.5
    ) -> dict:
        tags_json = json.dumps(topic_tags or [])
        self._execute(
            """
            INSERT INTO conversations
                (message_id, workspace_id, role, message, model_used, created_at,
                 retrieval_chunks, session_id, turn_index, topic_tags, importance_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (message_id, workspace_id, role, message, model_used, created_at,
             retrieval_chunks, session_id, turn_index, tags_json, importance_score)
        )
        return self._execute(
            "SELECT * FROM conversations WHERE message_id = ?",
            (message_id,),
            fetch_one=True
        )

    def get_recent_messages(self, workspace_id: str, limit: int = 5) -> list[dict]:
        """Get recent messages across all sessions (legacy path — still used for summarisation)."""
        rows = self._execute(
            "SELECT * FROM conversations WHERE workspace_id = ? ORDER BY created_at DESC LIMIT ?",
            (workspace_id, limit),
            fetch_all=True
        )
        return list(reversed(rows or []))

    def get_recent_messages_for_session(
        self, workspace_id: str, session_id: str, limit: int = 10
    ) -> list[dict]:
        """Get recent messages scoped to a specific conversation session."""
        rows = self._execute(
            """
            SELECT * FROM conversations
            WHERE workspace_id = ? AND session_id = ?
            ORDER BY created_at DESC LIMIT ?
            """,
            (workspace_id, session_id, limit),
            fetch_all=True
        )
        return list(reversed(rows or []))

    def get_all_messages(self, workspace_id: str) -> list[dict]:
        return self._execute(
            "SELECT * FROM conversations WHERE workspace_id = ? ORDER BY created_at ASC",
            (workspace_id,),
            fetch_all=True
        ) or []

    def get_all_messages_for_session(self, workspace_id: str, session_id: str) -> list[dict]:
        return self._execute(
            """
            SELECT * FROM conversations
            WHERE workspace_id = ? AND session_id = ?
            ORDER BY created_at ASC
            """,
            (workspace_id, session_id),
            fetch_all=True
        ) or []

    def get_all_user_queries_for_workspace(self, workspace_id: str) -> list[dict]:
        """Returns all past user queries across all sessions in a workspace with session metadata."""
        return self._execute(
            """
            SELECT c.message_id, c.session_id, c.message, c.created_at, c.topic_tags,
                   COALESCE(s.session_name, 'Default Session') as session_name
            FROM conversations c
            LEFT JOIN conversation_sessions s ON c.session_id = s.session_id
            WHERE c.workspace_id = ? AND c.role = 'user'
            ORDER BY c.created_at ASC
            """,
            (workspace_id,),
            fetch_all=True
        ) or []

    def get_workspace_session_digests(self, workspace_id: str) -> list[dict]:
        """
        Returns a concise digest of all sessions in a workspace, including session name,
        message count, and sample queries discussed.
        """
        return self._execute(
            """
            SELECT s.session_id, s.session_name, s.message_count, s.updated_at, s.created_at,
                   (
                       SELECT c.message FROM conversations c
                       WHERE c.session_id = s.session_id AND c.role = 'user'
                       ORDER BY c.created_at ASC LIMIT 1
                   ) as initial_query
            FROM conversation_sessions s
            WHERE s.workspace_id = ?
            ORDER BY s.updated_at DESC
            """,
            (workspace_id,),
            fetch_all=True
        ) or []

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

    def delete_session_messages(self, session_id: str):
        self._execute(
            "DELETE FROM conversations WHERE session_id = ?",
            (session_id,)
        )
