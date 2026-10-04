import time
import requests
import logging
from backend.core.config.settings import get_settings
from backend.core.exceptions.exceptions import QwenUnavailableException

logger = logging.getLogger(__name__)

class QwenProvider:
    _cached_availability: bool | None = None
    _cached_detail: str | None = None
    _cached_model: str | None = None
    _last_checked: float = 0.0
    _CACHE_TTL_SECS = 15

    def __init__(self):
        self.settings = get_settings()
        self.base_url = "http://localhost:11434"
        self.chat_url = f"{self.base_url}/api/chat"
        self.tags_url = f"{self.base_url}/api/tags"
        self.configured_model = self.settings.LOCAL_MODEL_NAME

    def _resolve_active_model(self) -> str:
        """
        Returns the configured model if installed in Ollama, or auto-selects
        the best available local model from Ollama.
        """
        if QwenProvider._cached_model:
            return QwenProvider._cached_model
        return self.configured_model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        active_model = self._resolve_active_model()
        payload = {
            "model": active_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 1000
            }
        }

        try:
            response = requests.post(self.chat_url, json=payload, timeout=120)
            if response.status_code == 404:
                raise QwenUnavailableException(f"Model '{active_model}' not found in Ollama.")
            response.raise_for_status()
            return response.json()["message"]["content"]
        except requests.exceptions.ConnectionError:
            raise QwenUnavailableException("Ollama service is offline on http://localhost:11434.")
        except Exception as e:
            raise QwenUnavailableException(f"Ollama inference error: {e}")

    def get_diagnostics(self) -> dict:
        """
        Deep diagnostics for Ollama service availability and model verification.
        """
        now = time.time()
        if (QwenProvider._cached_availability is not None and 
                now - QwenProvider._last_checked < QwenProvider._CACHE_TTL_SECS):
            return {
                "status": "ok" if QwenProvider._cached_availability else "error",
                "detail": QwenProvider._cached_detail
            }

        try:
            # Query Ollama installed models
            tags_resp = requests.get(self.tags_url, timeout=3)
            if tags_resp.status_code != 200:
                diag = {
                    "status": "error",
                    "detail": f"Ollama returned HTTP {tags_resp.status_code} on /api/tags."
                }
                self._set_cache(False, diag["detail"], None)
                return diag

            installed_models = [m.get("name") for m in tags_resp.json().get("models", [])]
            
            if not installed_models:
                diag = {
                    "status": "error",
                    "detail": "Ollama is running, but no models are installed. Run 'ollama pull qwen2.5:3b' to install a model."
                }
                self._set_cache(False, diag["detail"], None)
                return diag

            # Check if configured model is installed (exact or prefix match)
            matched_model = None
            for m in installed_models:
                if m == self.configured_model or m.startswith(self.configured_model.split(":")[0]):
                    matched_model = m
                    break

            if matched_model is None:
                # Fallback to first available model
                matched_model = installed_models[0]
                detail = (
                    f"Configured model '{self.configured_model}' not found in Ollama. "
                    f"Auto-selected installed model '{matched_model}'. "
                    f"Available local models: {installed_models}"
                )
            else:
                detail = f"Ollama connected with model '{matched_model}'. Available: {installed_models}"

            self._set_cache(True, detail, matched_model)
            return {
                "status": "ok",
                "detail": detail
            }

        except requests.exceptions.ConnectionError:
            detail = "Ollama is not running on http://localhost:11434. Please start Ollama or run start.bat."
            self._set_cache(False, detail, None)
            return {"status": "error", "detail": detail}
        except Exception as e:
            detail = f"Ollama health check error: {e}"
            self._set_cache(False, detail, None)
            return {"status": "error", "detail": detail}

    def _set_cache(self, is_available: bool, detail: str, active_model: str | None) -> None:
        QwenProvider._cached_availability = is_available
        QwenProvider._cached_detail = detail
        QwenProvider._cached_model = active_model
        QwenProvider._last_checked = time.time()

    def is_available(self) -> bool:
        diag = self.get_diagnostics()
        return diag["status"] == "ok"
