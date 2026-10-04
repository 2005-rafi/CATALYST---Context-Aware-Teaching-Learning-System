"""
SessionManager — manages named conversation sessions within a workspace.

SOLID:
  - S: Only manages session lifecycle. No retrieval, no LLM, no token counting.
  - O: Extension points via repository abstraction.
CIA:
  - Confidentiality: session_id = UUID4 — opaque, non-enumerable, non-guessable.
  - Integrity: all writes via parameterised queries through SessionRepository.
  - Availability: all methods wrapped with graceful error logging.
"""
import logging
from backend.repositories.sqlite.session_repository import SessionRepository

logger = logging.getLogger(__name__)


class SessionManager:

    def __init__(self):
        self.repo = SessionRepository()

    def create_session(self, workspace_id: str, name: str = "New Conversation") -> dict:
        """Create a new named session and make it the active one."""
        try:
            return self.repo.create_session(workspace_id, name)
        except Exception as e:
            logger.error(f"SessionManager: failed to create session for workspace {workspace_id}: {e}")
            raise

    def get_active_session(self, workspace_id: str) -> dict | None:
        """Return the currently active session, or None if none exists."""
        try:
            return self.repo.get_active_session(workspace_id)
        except Exception as e:
            logger.warning(f"SessionManager: failed to get active session for {workspace_id}: {e}")
            return None

    def get_or_create_active_session(self, workspace_id: str) -> dict:
        """
        Return the active session, creating a default one if none exists.
        Ensures every workspace always has an active session before chat begins.
        """
        session = self.get_active_session(workspace_id)
        if session:
            return session
        logger.info(f"SessionManager: no active session found for {workspace_id} — auto-creating default.")
        return self.create_session(workspace_id, "New Conversation")

    def list_sessions(self, workspace_id: str) -> list[dict]:
        """Return all sessions for a workspace, most recently updated first."""
        try:
            return self.repo.list_sessions(workspace_id)
        except Exception as e:
            logger.warning(f"SessionManager: failed to list sessions for {workspace_id}: {e}")
            return []

    def rename_session(self, session_id: str, new_name: str) -> dict | None:
        try:
            return self.repo.rename_session(session_id, new_name)
        except Exception as e:
            logger.error(f"SessionManager: failed to rename session {session_id}: {e}")
            return None

    def activate_session(self, session_id: str, workspace_id: str) -> dict | None:
        """Set a session as active (deactivates all others in workspace)."""
        try:
            return self.repo.activate_session(session_id, workspace_id)
        except Exception as e:
            logger.error(f"SessionManager: failed to activate session {session_id}: {e}")
            return None

    def delete_session(self, session_id: str) -> bool:
        try:
            rows = self.repo.delete_session(session_id)
            return rows > 0
        except Exception as e:
            logger.error(f"SessionManager: failed to delete session {session_id}: {e}")
            return False

    def increment_message_count(self, session_id: str, count: int = 2) -> None:
        try:
            self.repo.increment_message_count(session_id, count=count)
        except Exception as e:
            logger.warning(f"SessionManager: failed to increment count for session {session_id}: {e}")
