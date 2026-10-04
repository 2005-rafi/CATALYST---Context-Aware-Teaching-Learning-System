import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.core.config.settings import get_settings
from backend.core.logging.logger import setup_logging, get_logger

settings = get_settings()

from backend.repositories.sqlite.database import initialize_database, db_connection
from backend.repositories.sqlite.schema import create_schema
from backend.providers.embeddings.embedding_provider import get_embedding_provider
from backend.providers.embeddings.cross_encoder_provider import get_cross_encoder_provider

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging(settings.LOG_LEVEL, settings.ENVIRONMENT)
    logger = get_logger(__name__)
    logger.info("Application starting")
    
    # Optimize PyTorch CPU threading for low-memory cloud containers (e.g. Render 512MB RAM)
    try:
        import torch
        torch.set_num_threads(1)
    except Exception:
        pass
    
    directories = [
        settings.UPLOADS_PATH,
        settings.FAISS_PATH,
        settings.BM25_PATH,
        os.path.dirname(settings.DATABASE_PATH),
        settings.LOGS_PATH
    ]
    
    for d in directories:
        os.makedirs(d, exist_ok=True)
        
    initialize_database()
    with db_connection() as conn:
        create_schema(conn)

    # Sanitize legacy memory profiles to ensure no conversational fluff
    try:
        from backend.scripts.sanitize_memory_profiles import sanitize_database_memory_profiles
        sanitize_database_memory_profiles()
    except Exception as e:
        logger.warning(f"Startup memory profile sanitization notice: {e}")
        
    logger.info("Preloading embedding models...")
    get_embedding_provider()
    get_cross_encoder_provider()
        
    logger.info("All systems initialized")
    
    yield
    
    # Shutdown
    logger.info("Application shutting down")
