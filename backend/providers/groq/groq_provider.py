import time
import threading
import logging
from groq import Groq
from backend.core.config.settings import get_settings
from backend.core.exceptions.exceptions import GroqUnavailableException

logger = logging.getLogger(__name__)

class GroqProvider:
    _cache_lock = threading.Lock()
    _cached_availability: bool | None = None
    _cached_detail: str | None = None
    _last_checked: float = 0.0
    _CACHE_TTL_SECS = 120

    def __init__(self):
        self.settings = get_settings()
        self.api_key = (self.settings.GROQ_API_KEY or "").strip()
        self._client: Groq | None = None

    @property
    def client(self) -> Groq:
        if self._client is None:
            self._client = Groq(api_key=self.api_key)
        return self._client

    def _get_active_model(self, requested_model: str = None) -> str:
        fallback_candidates = [
            requested_model,
            self.settings.GROQ_MODEL_MEDIUM,
            self.settings.GROQ_MODEL_EXPERT,
            "qwen/qwen3.8-27b",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "allam-2-7b",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant"
        ]
        return [m for m in fallback_candidates if m][0]

    def generate(self, messages: list[dict], model: str = None, temperature: float = 0.1, max_tokens: int = 2048) -> str:
        candidates = [
            model,
            self.settings.GROQ_MODEL_MEDIUM,
            self.settings.GROQ_MODEL_EXPERT,
            "qwen/qwen3.8-27b",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "allam-2-7b",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant"
        ]
        unique_models = list(dict.fromkeys([m for m in candidates if m]))
        
        last_error = None
        for candidate_model in unique_models:
            try:
                effective_max_tokens = min(max_tokens, 800) if "qwen" in candidate_model.lower() else max_tokens
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=candidate_model,
                    temperature=temperature,
                    max_tokens=effective_max_tokens,
                )
                return response.choices[0].message.content
            except Exception as e:
                err_msg = str(e)
                last_error = err_msg
                logger.warning(f"Groq model '{candidate_model}' failed ({err_msg[:120]}), trying fallback...")
                continue
                    
        raise GroqUnavailableException(f"Groq API error: {last_error}")

    def stream(self, messages: list[dict], model: str = None, temperature: float = 0.1, max_tokens: int = 2048):
        candidates = [
            model,
            self.settings.GROQ_MODEL_MEDIUM,
            self.settings.GROQ_MODEL_EXPERT,
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "qwen/qwen3.8-27b",
            "allam-2-7b",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant"
        ]
        unique_models = list(dict.fromkeys([m for m in candidates if m]))
        
        for candidate_model in unique_models:
            try:
                effective_max_tokens = min(max_tokens, 800) if "qwen" in candidate_model.lower() else max_tokens
                completion = self.client.chat.completions.create(
                    messages=messages,
                    model=candidate_model,
                    temperature=temperature,
                    max_tokens=effective_max_tokens,
                    stream=True
                )
                for chunk in completion:
                    delta = chunk.choices[0].delta.content if chunk.choices else ""
                    if delta:
                        yield delta
                return
            except Exception as e:
                logger.warning(f"Groq streaming failed on '{candidate_model}': {e}")
                continue
        raise GroqUnavailableException("Groq streaming failed across all candidate models.")

    def get_diagnostics(self) -> dict:
        """
        Returns rich diagnostic reasoning for Groq API availability.
        """
        now = time.time()
        with GroqProvider._cache_lock:
            if (GroqProvider._cached_availability is not None and
                    now - GroqProvider._last_checked < GroqProvider._CACHE_TTL_SECS):
                return {
                    "status": "ok" if GroqProvider._cached_availability else "error",
                    "detail": GroqProvider._cached_detail
                }

        # Step 1: Pre-validation of API Key
        if not self.api_key or self.api_key == "your_groq_api_key_here":
            diag = {
                "status": "unconfigured",
                "detail": "GROQ_API_KEY is not configured in secrets/.env"
            }
            self._set_cache(False, diag["detail"])
            return diag

        if not self.api_key.startswith("gsk_"):
            prefix = self.api_key[:4] if len(self.api_key) >= 4 else self.api_key
            diag = {
                "status": "error",
                "detail": f"Invalid Groq API key format (keys must start with 'gsk_', found prefix '{prefix}')."
            }
            self._set_cache(False, diag["detail"])
            return diag

        # Step 2: Live validation probe
        candidates = [
            self.settings.GROQ_MODEL_MEDIUM,
            self.settings.GROQ_MODEL_EXPERT,
            "qwen/qwen3.8-27b",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant"
        ]
        unique_models = list(dict.fromkeys([m for m in candidates if m]))

        last_err = None
        for candidate_model in unique_models:
            try:
                self.client.chat.completions.create(
                    messages=[{"role": "user", "content": "ping"}],
                    model=candidate_model,
                    max_tokens=1
                )
                diag = {
                    "status": "ok",
                    "detail": f"Groq API connected and verified with model '{candidate_model}'."
                }
                self._set_cache(True, diag["detail"])
                return diag
            except Exception as e:
                err_str = str(e)
                last_err = err_str
                if "401" in err_str or "Invalid API Key" in err_str or "authentication" in err_str.lower():
                    detail = "Groq API key is invalid, expired, or revoked (401 Unauthorized)."
                    self._set_cache(False, detail)
                    return {"status": "error", "detail": detail}
                if "does not exist" in err_str or "model_not_found" in err_str or "404" in err_str:
                    continue
                break

        err_str = last_err or "Unknown error"
        if "429" in err_str or "rate limit" in err_str.lower() or "quota" in err_str.lower():
            detail = "Groq API rate limit or organization token quota exceeded (429 Too Many Requests)."
        elif "connection" in err_str.lower() or "timeout" in err_str.lower():
            detail = f"Network connection timeout while connecting to api.groq.com: {err_str}"
        else:
            detail = f"Groq API error: {err_str}"

        logger.warning(f"Groq availability check failed: {detail}")
        diag = {
            "status": "error",
            "detail": detail
        }
        self._set_cache(False, detail)
        return diag

    def _set_cache(self, is_available: bool, detail: str) -> None:
        with GroqProvider._cache_lock:
            GroqProvider._cached_availability = is_available
            GroqProvider._cached_detail = detail
            GroqProvider._last_checked = time.time()

    def is_available(self) -> bool:
        diag = self.get_diagnostics()
        return diag["status"] == "ok"
