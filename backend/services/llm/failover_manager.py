import logging
from backend.providers.groq.groq_provider import GroqProvider
from backend.providers.qwen.qwen_provider import QwenProvider
from backend.core.exceptions.exceptions import GroqUnavailableException, QwenUnavailableException
from backend.core.config.settings import get_settings

logger = logging.getLogger(__name__)

class FailoverManager:
    def __init__(self):
        self.groq = GroqProvider()
        self.qwen = QwenProvider()
        self.settings = get_settings()
        
    def generate(self, messages: list[dict], mode: str) -> tuple[str, str]:
        system_prompt = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_prompt = next((m["content"] for m in messages if m["role"] == "user"), "")
        
        if mode == "simple":
            try:
                response = self.qwen.generate(system_prompt, user_prompt)
                return response, self.settings.LOCAL_MODEL_NAME
            except QwenUnavailableException as e:
                logger.warning(f"Qwen unavailable in simple mode, falling back to Groq. Error: {e}")
                try:
                    response = self.groq.generate(messages, model=self.settings.GROQ_MODEL_MEDIUM)
                    return response, self.settings.GROQ_MODEL_MEDIUM
                except Exception:
                    return "Both AI models are currently unavailable. Please try again later.", "none"
                    
        else:
            target_model = self.settings.GROQ_MODEL_EXPERT if mode == "expert" else self.settings.GROQ_MODEL_MEDIUM
            try:
                response = self.groq.generate(messages, model=target_model)
                return response, target_model
            except GroqUnavailableException as e:
                logger.warning(f"Groq unavailable, falling back to Qwen. Error: {e}")
                try:
                    response = self.qwen.generate(system_prompt, user_prompt)
                    return response, self.settings.LOCAL_MODEL_NAME
                except QwenUnavailableException:
                    return "Both AI models are currently unavailable. Please try again later.", "none"
