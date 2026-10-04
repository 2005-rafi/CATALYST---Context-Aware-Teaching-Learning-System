import gc
import os
import logging
from functools import lru_cache
from pathlib import Path

from sentence_transformers import SentenceTransformer
from backend.core.config.settings import get_settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Batch cap for embed_batch().
# Limits the number of text chunks embedded in one forward pass.
# Prevents memory spikes during large PDF ingestion (e.g. a 200-page PDF
# produces ~400 chunks; embedding them all at once can spike RSS by ~300MB).
# Default: 32 chunks per batch.  Override via EMBEDDING_BATCH_SIZE env var.
# ---------------------------------------------------------------------------
_MAX_BATCH_SIZE: int = int(os.environ.get("EMBEDDING_BATCH_SIZE", "32"))


class EmbeddingProvider:
    """
    Singleton embedding provider with lazy model loading and batch-capped
    encoding, designed for Render.com 512MB free-tier constraints.

    The underlying SentenceTransformer model is loaded only on the first call
    to self.model (the @property). This keeps startup RSS under ~150MB.
    """

    def __init__(self):
        self.settings = get_settings()
        self.model_name = self.settings.EMBEDDING_MODEL
        self._model: SentenceTransformer | None = None

    @property
    def model(self) -> SentenceTransformer:
        """Lazy-load the embedding model on first access."""
        if self._model is None:
            local_path = Path(self.settings.local_embedding_model_path())
            if local_path.exists() and (local_path / "config.json").exists():
                logger.info(
                    f"Loading embedding model from local cache: {local_path}"
                )
                self._model = SentenceTransformer(
                    str(local_path),
                    local_files_only=True,
                    device="cpu",
                )
            else:
                logger.info(
                    f"Downloading embedding model '{self.model_name}' (CPU)..."
                )
                local_path.mkdir(parents=True, exist_ok=True)
                self._model = SentenceTransformer(
                    self.model_name,
                    device="cpu",
                )
                try:
                    self._model.save(str(local_path))
                    logger.info(
                        f"Embedding model cached at: {local_path}"
                    )
                except Exception as e:
                    logger.warning(
                        f"Could not cache embedding model locally: {e}"
                    )
            # Force a GC pass after load to reclaim any temporary allocations
            gc.collect()
            logger.info("Embedding model ready.")
        return self._model

    def embed_text(self, text: str) -> list[float]:
        """Embed a single string. Returns a flat list of floats."""
        return self.model.encode(
            text,
            show_progress_bar=False,
            convert_to_numpy=True,
        ).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Embed a list of strings in memory-capped micro-batches.

        Processes at most _MAX_BATCH_SIZE chunks per forward pass, then
        calls gc.collect() to allow Python to reclaim intermediate tensors
        before the next batch. This trades slightly more wall-clock time for
        a flat, predictable RSS profile during large document ingestion.
        """
        if not texts:
            return []

        results: list[list[float]] = []
        for i in range(0, len(texts), _MAX_BATCH_SIZE):
            batch = texts[i : i + _MAX_BATCH_SIZE]
            batch_embeddings = self.model.encode(
                batch,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=False,
            )
            results.extend(batch_embeddings.tolist())
            gc.collect()

        return results


@lru_cache(maxsize=1)
def get_embedding_provider() -> EmbeddingProvider:
    """Return the process-wide EmbeddingProvider singleton."""
    return EmbeddingProvider()
