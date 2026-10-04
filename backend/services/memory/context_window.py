"""
ContextWindow — fetches recent conversation messages for context injection.
Updated to support both workspace-level (legacy) and session-scoped history.
"""
from backend.repositories.sqlite.conversation_repository import ConversationRepository
from backend.core.config.settings import get_settings

# Max characters to include from a prior assistant response in the context window
# Long prior responses are trimmed to their first "paragraph" to reduce noise
_ASSISTANT_TRUNCATE_CHARS = 250


class ContextWindow:

    def __init__(self):
        self.conversation_repo = ConversationRepository()
        self.window_size = get_settings().RECENT_CHAT_WINDOW

    def get_recent_context(self, workspace_id: str) -> list[dict]:
        """Workspace-level history (legacy path used by summarisation)."""
        messages = self.conversation_repo.get_recent_messages(
            workspace_id, limit=self.window_size
        )
        return self._trim_long_responses(messages)

    def get_recent_context_for_session(
        self, workspace_id: str, session_id: str, limit: int | None = None
    ) -> list[dict]:
        """Session-scoped history — primary path for CI-aware queries."""
        effective_limit = limit or (self.window_size * 2)  # allow more raw history for budget trimming
        messages = self.conversation_repo.get_recent_messages_for_session(
            workspace_id, session_id, limit=effective_limit
        )
        return self._trim_long_responses(messages)

    def format_for_prompt(self, messages: list[dict]) -> str:
        if not messages:
            return ""
        formatted = []
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{role}: {msg['message']}")
        return "Recent Conversation:\n" + "\n".join(formatted)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _trim_long_responses(self, messages: list[dict]) -> list[dict]:
        """Reduce noise: truncate long prior assistant messages to first paragraph."""
        trimmed = []
        for msg in messages:
            if msg["role"] == "assistant" and len(msg.get("message", "")) > _ASSISTANT_TRUNCATE_CHARS:
                truncated = msg.copy()
                text = msg["message"]
                para_end = text.find("\n\n")
                if 0 < para_end < _ASSISTANT_TRUNCATE_CHARS * 2:
                    truncated["message"] = text[:para_end] + " [...]"
                else:
                    truncated["message"] = text[:_ASSISTANT_TRUNCATE_CHARS] + " [...]"
                trimmed.append(truncated)
            else:
                trimmed.append(msg)
        return trimmed
