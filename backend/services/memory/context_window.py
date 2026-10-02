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
        messages = self.conversation_repo.get_recent_messages(workspace_id, limit=self.window_size)
        # Reduce noise: truncate long prior assistant messages to first paragraph
        trimmed = []
        for msg in messages:
            if msg["role"] == "assistant" and len(msg.get("message", "")) > _ASSISTANT_TRUNCATE_CHARS:
                truncated = msg.copy()
                text = msg["message"]
                # Try to cut at a natural paragraph break first
                para_end = text.find("\n\n")
                if para_end > 0 and para_end < _ASSISTANT_TRUNCATE_CHARS * 2:
                    truncated["message"] = text[:para_end] + " [...]"
                else:
                    truncated["message"] = text[:_ASSISTANT_TRUNCATE_CHARS] + " [...]"
                trimmed.append(truncated)
            else:
                trimmed.append(msg)
        return trimmed
        
    def format_for_prompt(self, messages: list[dict]) -> str:
        if not messages:
            return ""
            
        formatted = []
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{role}: {msg['message']}")
            
        return "Recent Conversation:\n" + "\n".join(formatted)

