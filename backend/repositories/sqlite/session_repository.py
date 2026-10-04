"""
SessionRepository — CRUD for conversation_sessions table.
All writes use parameterised queries (CIA: Integrity).
session_id values are UUID4 — opaque, non-enumerable (CIA: Confidentiality).
"""
import uuid
import datetime
from backend.repositories.sqlite.base_repository import BaseRepository


class SessionRepository(BaseRepository):

    def create_session(self, workspace_id: str, session_name: str = "New Conversation") -> dict:
        """Create a new session and mark it as the active one for this workspace."""
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        session_id = str(uuid.uuid4())
        # Deactivate any existing active sessions first
        self._execute(
            "UPDATE conversation_sessions SET is_active = 0 WHERE workspace_id = ?",
            (workspace_id,)
        )
        self._execute(
            """
            INSERT INTO conversation_sessions
                (session_id, workspace_id, session_name, created_at, updated_at, message_count, is_active)
            VALUES (?, ?, ?, ?, ?, 0, 1)
            """,
            (session_id, workspace_id, session_name, now, now)
        )
        return self.get_session(session_id)

    def get_session(self, session_id: str) -> dict | None:
        return self._execute(
            "SELECT * FROM conversation_sessions WHERE session_id = ?",
            (session_id,),
            fetch_one=True
        )

    def get_active_session(self, workspace_id: str) -> dict | None:
        """Returns the currently active session for a workspace, or None."""
        return self._execute(
            """
            SELECT * FROM conversation_sessions
            WHERE workspace_id = ? AND is_active = 1
            ORDER BY updated_at DESC LIMIT 1
            """,
            (workspace_id,),
            fetch_one=True
        )

    def list_sessions(self, workspace_id: str) -> list[dict]:
        """Return all sessions for a workspace, most recently updated first."""
        return self._execute(
            """
            SELECT * FROM conversation_sessions
            WHERE workspace_id = ?
            ORDER BY updated_at DESC
            """,
            (workspace_id,),
            fetch_all=True
        ) or []

    def rename_session(self, session_id: str, new_name: str) -> dict | None:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self._execute(
            "UPDATE conversation_sessions SET session_name = ?, updated_at = ? WHERE session_id = ?",
            (new_name, now, session_id)
        )
        return self.get_session(session_id)

    def activate_session(self, session_id: str, workspace_id: str) -> dict | None:
        """Deactivate all sessions in workspace, then activate the specified one."""
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self._execute(
            "UPDATE conversation_sessions SET is_active = 0 WHERE workspace_id = ?",
            (workspace_id,)
        )
        self._execute(
            "UPDATE conversation_sessions SET is_active = 1, updated_at = ? WHERE session_id = ?",
            (now, session_id)
        )
        return self.get_session(session_id)

    def delete_session(self, session_id: str) -> int:
        return self._execute(
            "DELETE FROM conversation_sessions WHERE session_id = ?",
            (session_id,)
        )

    def increment_message_count(self, session_id: str, count: int = 2) -> None:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self._execute(
            """
            UPDATE conversation_sessions
            SET message_count = message_count + ?, updated_at = ?
            WHERE session_id = ?
            """,
            (count, now, session_id)
        )
