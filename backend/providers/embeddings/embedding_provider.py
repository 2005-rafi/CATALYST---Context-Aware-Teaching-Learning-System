import os
import gc
from functools import lru_cache
from pathlib import Path
from sentence_transformers import SentenceTransformer
from backend.core.config.settings import get_settings
import logging

logger = logging.getLogger(__name__)

class EmbeddingProvider:
    def __init__(self):
        self.settings = get_settings()
        self.model_name = self.settings.EMBEDDING_MODEL
        self._model = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            local_path = Path(self.settings.local_embedding_model_path())
            if local_path.exists() and (local_path / "config.json").exists():
                logger.info(f"Loading embedding model offline from local store: {local_path}")
                self._model = SentenceTransformer(str(local_path), local_files_only=True, device="cpu")
            else:
                logger.info(f"Fetching '{self.model_name}' on CPU...")
                local_path.mkdir(parents=True, exist_ok=True)
                self._model = SentenceTransformer(self.model_name, device="cpu")
                try:
                    self._model.save(str(local_path))
                    logger.info(f"Embedding model cached locally at: {local_path}")
                except Exception as e:
                    logger.warning(f"Could not cache embedding model locally: {e}")
            gc.collect()
        return self._model
        
    def embed_text(self, text: str) -> list[float]:
        return self.model.encode(text, show_progress_bar=False).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

@lru_cache(maxsize=1)
def get_embedding_provider() -> EmbeddingProvider:
    """Return the singleton EmbeddingProvider."""
    return EmbeddingProvider()
