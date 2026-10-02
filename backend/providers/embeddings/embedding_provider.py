import os
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
        local_path = Path(self.settings.local_embedding_model_path())
        
        # Offline-first loading
        if local_path.exists() and (local_path / "config.json").exists():
            logger.info(f"Loading embedding model offline from local store: {local_path}")
            self.model = SentenceTransformer(str(local_path), local_files_only=True)
        else:
            logger.info(f"Local model not found at {local_path}. Fetching '{self.model_name}' and caching locally...")
            local_path.mkdir(parents=True, exist_ok=True)
            self.model = SentenceTransformer(self.model_name)
            self.model.save(str(local_path))
            logger.info(f"Embedding model cached locally at: {local_path}")
        
    def embed_text(self, text: str) -> list[float]:
        return self.model.encode(text, show_progress_bar=False).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

@lru_cache(maxsize=1)
def get_embedding_provider() -> EmbeddingProvider:
    """Return the singleton EmbeddingProvider. Loads model once at startup."""
    return EmbeddingProvider()
