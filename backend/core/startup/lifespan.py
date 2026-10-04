import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.core.config.settings import get_settings
from backend.core.logging.logger import setup_logging, get_logger

settings = get_settings()

# --- Memory Safety: Set ALL CPU thread limits as early as possible ---
# These must be set BEFORE numpy, torch, or any BLAS-backed library is imported.
# We use setdefault so that values already set in the OS environment (e.g., from
# Render Dashboard env vars) are not overwritten.
_THREAD_LIMITS = {
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "TORCH_NUM_THREADS": "1",
}
for _key, _val in _THREAD_LIMITS.items():
    os.environ.setdefault(_key, _val)

from backend.repositories.sqlite.database import initialize_database, db_connection
from backend.repositories.sqlite.schema import create_schema


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager — startup and shutdown hooks."""
    # ------------------------------------------------------------------ #
    # STARTUP                                                              #
    # ------------------------------------------------------------------ #
    setup_logging(settings.LOG_LEVEL, settings.ENVIRONMENT)
    logger = get_logger(__name__)
    logger.info("Application starting")

    # Ensure required storage directories exist
    directories = [
        settings.UPLOADS_PATH,
        settings.FAISS_PATH,
        settings.BM25_PATH,
        os.path.dirname(settings.DATABASE_PATH),
        settings.LOGS_PATH,
    ]
    for d in directories:
        os.makedirs(d, exist_ok=True)

    # Initialise SQLite schema
    initialize_database()
    with db_connection() as conn:
        create_schema(conn)

    # Sanitise legacy memory profiles at startup
    try:
        from backend.scripts.sanitize_memory_profiles import sanitize_database_memory_profiles
        sanitize_database_memory_profiles()
    except Exception as e:
        logger.warning(f"Startup memory profile sanitization notice: {e}")

    # ------------------------------------------------------------------ #
    # INTENTIONALLY NOT pre-loading the embedding model here.             #
    #                                                                      #
    # Rationale: all-MiniLM-L6-v2 costs ~90MB RAM. Combined with the      #
    # Python interpreter (~50MB), FastAPI (~40MB), numpy/faiss (~130MB),  #
    # and torch CPU (~250MB), eager loading would push startup RSS to      #
    # ~560MB — over Render's 512MB free-tier cap.                          #
    #                                                                      #
    # Instead, the EmbeddingProvider uses a lazy @property pattern:        #
    # the model is loaded on the FIRST real request (document ingestion    #
    # or chat). Subsequent requests hit the lru_cache singleton instantly. #
    # The trade-off is a ~3-5s delay on the very first request only.       #
    # ------------------------------------------------------------------ #
    logger.info(
        "All systems initialized — embedding model will load on first use "
        "(lazy loading active for Render free-tier memory safety)."
    )

    yield

    # ------------------------------------------------------------------ #
    # SHUTDOWN                                                             #
    # ------------------------------------------------------------------ #
    logger.info("Application shutting down")
