import traceback
import logging
from backend.repositories.sqlite.conversation_repository import ConversationRepository
from backend.providers.llm.groq_provider import GroqProvider
from backend.core.config.settings import get_settings

logger = logging.getLogger(__name__)

# Max messages to include in summarization input — prevents token explosion
MAX_MESSAGES_FOR_SUMMARY = 40

class SummarizationService:
    def __init__(self):
        self.conversation_repo = ConversationRepository()
        self.groq_provider = GroqProvider()
        self.settings = get_settings()
        self.interval = self.settings.SUMMARY_UPDATE_INTERVAL
        
    def should_summarize(self, workspace_id: str) -> bool:
        message_count = self.conversation_repo.get_message_count(workspace_id)
        return message_count > 0 and message_count % self.interval == 0
        
    def generate_summary(self, workspace_id: str) -> str | None:
        try:
            # Use bounded recent messages, not unbounded full history
            messages = self.conversation_repo.get_recent_messages(
                workspace_id, limit=MAX_MESSAGES_FOR_SUMMARY
            )
            if not messages:
                return None
            
            # Deduplicate consecutive same-role messages (noise reduction)
            deduped = []
            for msg in messages:
                if deduped and deduped[-1]["role"] == msg["role"] and \
                   deduped[-1]["message"] == msg["message"]:
                    continue  # skip exact duplicates
                deduped.append(msg)
                
            formatted = []
            for msg in deduped:
                role = "User" if msg["role"] == "user" else "Assistant"
                # Truncate very long individual messages to avoid token bloat
                text = msg["message"][:800] if len(msg["message"]) > 800 else msg["message"]
                formatted.append(f"{role}: {text}")
                
            conversation_text = "\n".join(formatted)
            
            system_prompt = (
                "You are a conversation summarizer for a RAG document assistant. "
                "Summarize the conversation below. Be concise. Structure your summary as:\n"
                "- **Key Topics**: main subjects discussed\n"
                "- **Documents Referenced**: any specific documents or sections mentioned\n"
                "- **Key Findings**: important answers or information provided\n"
                "- **Open Questions**: any unresolved questions or follow-ups\n"
                "Keep the total summary under 200 words. Omit filler and small talk."
            )
            prompt_msgs = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Conversation:\n{conversation_text}"}
            ]
            
            # Use medium model for cost-efficiency on internal summarization
            summary = self.groq_provider.generate(
                prompt_msgs, model=self.settings.GROQ_MODEL_MEDIUM
            )
            return summary
        except Exception as e:
            logger.error(f"Summarization failed for workspace {workspace_id}: {str(e)}\n{traceback.format_exc()}")
            return None

