from functools import lru_cache
from pathlib import Path
from sentence_transformers import CrossEncoder
from backend.core.config.settings import get_settings
import logging

logger = logging.getLogger(__name__)

class CrossEncoderProvider:
    def __init__(self):
        settings = get_settings()
        self.model_name = settings.CROSS_ENCODER_MODEL
        local_path = Path(settings.local_cross_encoder_path())
        
        # Offline-first loading
        if local_path.exists() and (local_path / "config.json").exists():
            logger.info(f"Loading cross-encoder model offline from local store: {local_path}")
            self.model = CrossEncoder(str(local_path), local_files_only=True)
        else:
            logger.info(f"Local cross-encoder not found at {local_path}. Fetching '{self.model_name}' and caching locally...")
            local_path.mkdir(parents=True, exist_ok=True)
            self.model = CrossEncoder(self.model_name)
            self.model.save(str(local_path))
            logger.info(f"Cross-encoder model cached locally at: {local_path}")
        
    def predict(self, query: str, texts: list[str]) -> list[float]:
        if not texts:
            return []
        pairs = [[query, text] for text in texts]
        scores = self.model.predict(pairs)
        return scores.tolist() if hasattr(scores, 'tolist') else list(scores)

@lru_cache(maxsize=1)
def get_cross_encoder_provider() -> CrossEncoderProvider:
    return CrossEncoderProvider()
