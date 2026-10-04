import gc
from functools import lru_cache
from pathlib import Path
from backend.core.config.settings import get_settings
import logging

logger = logging.getLogger(__name__)

class CrossEncoderProvider:
    def __init__(self):
        self.settings = get_settings()
        self.model_name = self.settings.CROSS_ENCODER_MODEL
        self._model = None

    @property
    def model(self):
        if not self.settings.ENABLE_CROSS_ENCODER:
            return None
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
                local_path = Path(self.settings.local_cross_encoder_path())
                if local_path.exists() and (local_path / "config.json").exists():
                    logger.info(f"Loading cross-encoder offline from local store: {local_path}")
                    self._model = CrossEncoder(str(local_path), local_files_only=True, device="cpu")
                else:
                    logger.info(f"Fetching '{self.model_name}' on CPU...")
                    local_path.mkdir(parents=True, exist_ok=True)
                    self._model = CrossEncoder(self.model_name, device="cpu")
                    try:
                        self._model.save(str(local_path))
                        logger.info(f"Cross-encoder cached locally at: {local_path}")
                    except Exception as e:
                        logger.warning(f"Could not cache cross-encoder locally: {e}")
                gc.collect()
            except Exception as e:
                logger.warning(f"CrossEncoder unavailable or disabled: {e}")
                self._model = None
        return self._model

    def predict(self, query: str, texts: list[str]) -> list[float]:
        if not texts:
            return []
        if not self.settings.ENABLE_CROSS_ENCODER or self.model is None:
            # Fallback to neutral 1.0 ranking when cross-encoder is disabled for low-memory cloud free tiers
            return [1.0] * len(texts)
        pairs = [[query, text] for text in texts]
        scores = self.model.predict(pairs)
        return scores.tolist() if hasattr(scores, 'tolist') else list(scores)

@lru_cache(maxsize=1)
def get_cross_encoder_provider() -> CrossEncoderProvider:
    return CrossEncoderProvider()
