import logging
import uuid
import time
import datetime
import traceback
import asyncio
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any

from backend.services.document.extractors.extractor_factory import ExtractorFactory
from backend.services.document.text_cleaner import TextCleaner
from backend.services.document.chunking.recursive_chunker import RecursiveChunker
from backend.repositories.sqlite.document_repository import DocumentRepository
from backend.repositories.sqlite.chunk_repository import ChunkRepository
from backend.repositories.sqlite.workspace_repository import WorkspaceRepository
from backend.repositories.vector.vector_repository import VectorRepository
from backend.repositories.bm25.bm25_repository import BM25Repository
from backend.providers.embeddings.embedding_provider import get_embedding_provider
from backend.services.analytics.analytics_service import AnalyticsService
from backend.core.config.settings import get_settings

logger = logging.getLogger(__name__)

# --- SOLID Pipeline Stage Abstraction ---

class IngestionStage(ABC):
    @abstractmethod
    async def execute(self, payload: dict) -> dict:
        pass

class PipelineProcessor:
    def __init__(self, stages: List[IngestionStage]):
        self.stages = stages

    async def run(self, payload: dict) -> dict:
        for stage in self.stages:
            stage_name = stage.__class__.__name__
            logger.info(f"Running pipeline stage: {stage_name}")
            
            # Stage-level Retry Mechanism with Exponential Backoff
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    payload = await stage.execute(payload)
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Stage {stage_name} failed after {max_retries} attempts.")
                        raise
                    delay = 2 ** attempt
                    logger.warning(
                        f"Stage {stage_name} failed on attempt {attempt + 1}/{max_retries} with error: {str(e)}. "
                        f"Retrying in {delay} seconds..."
                    )
                    await asyncio.sleep(delay)
        return payload

# --- Concrete Ingestion Stages ---

class ExtractorStage(IngestionStage):
    def __init__(self):
        self.extractor_factory = ExtractorFactory()
        self.document_repo = DocumentRepository()

    async def execute(self, payload: dict) -> dict:
        doc = self.document_repo.get_document(payload["document_id"])
        if not doc:
            raise FileNotFoundError(f"Document {payload['document_id']} not found.")
            
        file_path = doc["file_path"]
        file_type = doc["file_type"]
        
        extractor = self.extractor_factory.get_extractor(file_type)
        
        # Offload file physical read and coordinate parse (CPU-heavy fitz/pdfplumber) to a background thread
        result = await asyncio.to_thread(extractor.extract, file_path)
        
        if not result.extraction_success:
            raise ValueError(f"Extraction failed for file: {file_path}")
            
        payload["raw_text"] = result.full_text
        payload["pages"] = result.pages
        payload["metadata"] = result.metadata
        payload["page_boundaries"] = result.page_boundaries
        payload["headings"] = result.headings
        payload["file_path"] = file_path
        
        logger.info("Extraction completed", extra={
            "document_id": payload["document_id"], 
            "page_count": len(result.pages) if result.pages else 0
        })
        return payload

class SanitizerStage(IngestionStage):
    def __init__(self):
        self.text_cleaner = TextCleaner()

    async def execute(self, payload: dict) -> dict:
        raw_text = payload["raw_text"]
        
        # Offload citation truncation and unicode-cleaning to thread
        core_text, references = await asyncio.to_thread(
            self.text_cleaner.truncate_references, 
            raw_text
        )
        cleaned_text = await asyncio.to_thread(self.text_cleaner.clean, core_text)
        
        payload["cleaned_text"] = cleaned_text
        payload["references_text"] = references
        return payload

class ChunkingStage(IngestionStage):
    def __init__(self, settings):
        self.chunker = RecursiveChunker(settings)

    async def execute(self, payload: dict) -> dict:
        # Offload recursive splitting and binary search page mappings to thread
        chunks = await asyncio.to_thread(
            self.chunker.chunk,
            payload["cleaned_text"],
            payload.get("page_boundaries"),
            payload.get("headings")
        )
        payload["chunks"] = chunks
        logger.info("Chunking completed", extra={
            "document_id": payload["document_id"], 
            "chunk_count": len(chunks)
        })
        return payload

class SQLCacheStage(IngestionStage):
    def __init__(self):
        self.chunk_repo = ChunkRepository()
        self.document_repo = DocumentRepository()
        self.workspace_repo = WorkspaceRepository()

    async def execute(self, payload: dict) -> dict:
        document_id = payload["document_id"]
        workspace_id = payload["workspace_id"]
        chunks = payload["chunks"]
        
        chunk_ids = []
        chunk_texts = []
        batch_tuples = []
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        for chunk_data in chunks:
            chunk_id = str(uuid.uuid4())
            batch_tuples.append((
                chunk_id,
                workspace_id,
                document_id,
                chunk_data.chunk_index,
                chunk_data.text,
                chunk_data.token_count,
                now,
                chunk_data.page_number,
                chunk_data.section_heading
            ))
            chunk_ids.append(chunk_id)
            chunk_texts.append(chunk_data.text)
            
        # Execute single-transaction batch insert
        await asyncio.to_thread(self.chunk_repo.create_chunks_batch, batch_tuples)
        
        payload["chunk_ids"] = chunk_ids
        payload["chunk_texts"] = chunk_texts
        
        self.document_repo.update_chunk_stats(document_id, total_chunks=len(chunks), embedding_status=False)
        self.workspace_repo.increment_chunk_count(workspace_id, len(chunks))
        self.workspace_repo.increment_document_count(workspace_id)
        
        return payload

class VectorIngestionStage(IngestionStage):
    def __init__(self):
        self.embedding_provider = get_embedding_provider()
        self.vector_repo = VectorRepository()
        self.document_repo = DocumentRepository()

    async def execute(self, payload: dict) -> dict:
        chunk_ids = payload.get("chunk_ids", [])
        chunk_texts = payload.get("chunk_texts", [])
        workspace_id = payload["workspace_id"]
        document_id = payload["document_id"]
        
        if chunk_texts:
            embed_start = time.time()
            # Batch embedding generation (CPU or GPU heavy)
            embeddings = await asyncio.to_thread(self.embedding_provider.embed_batch, chunk_texts)
            self.vector_repo.add_vectors(workspace_id, chunk_ids, embeddings)
            embed_time = int((time.time() - embed_start) * 1000)
            
            self.document_repo.update_chunk_stats(document_id, total_chunks=len(chunk_ids), embedding_status=True)
            logger.info("Embedding completed", extra={"document_id": document_id, "duration_ms": embed_time})
            
        return payload

class LexicalIngestionStage(IngestionStage):
    def __init__(self):
        self.bm25_repo = BM25Repository()

    async def execute(self, payload: dict) -> dict:
        workspace_id = payload["workspace_id"]
        document_id = payload["document_id"]
        
        # Offload BM25 indexing tasks to background thread
        await asyncio.to_thread(self.bm25_repo.rebuild_index, workspace_id)
        logger.info("BM25 indexed", extra={"document_id": document_id, "workspace_id": workspace_id})
        return payload

# --- Ingestion Service Facade Orchestrator ---

class IngestionService:
    def __init__(self):
        self.settings = get_settings()
        self.document_repo = DocumentRepository()
        self.chunk_repo = ChunkRepository()
        self.workspace_repo = WorkspaceRepository()
        self.analytics_service = AnalyticsService()
        
        # Instantiate stages
        self.pipeline = PipelineProcessor([
            ExtractorStage(),
            SanitizerStage(),
            ChunkingStage(self.settings),
            SQLCacheStage(),
            VectorIngestionStage(),
            LexicalIngestionStage()
        ])

    async def ingest_document(self, document_id: str, workspace_id: str) -> None:
        file_path = None
        chunks_count = 0
        try:
            self.document_repo.update_processing_status(document_id, "processing")
            
            # Fetch doc metadata to get filepath for cleanups
            doc = self.document_repo.get_document(document_id)
            if doc:
                file_path = doc["file_path"]
                
            payload = {
                "document_id": document_id,
                "workspace_id": workspace_id
            }
            
            # Execute pipeline stages (with retry loop inside)
            final_payload = await self.pipeline.run(payload)
            chunks_count = len(final_payload.get("chunks", []))
            
            self.document_repo.update_processing_status(document_id, "completed")
            self.analytics_service.update_document_stats(workspace_id)
            
        except Exception as e:
            logger.error(
                f"Ingestion crashed fatally for doc {document_id}: {str(e)}\n"
                f"{traceback.format_exc()}"
            )
            self._cleanup_failed_ingestion(document_id, workspace_id, file_path, chunks_count)
            self.document_repo.update_processing_status(document_id, "failed")
            self.analytics_service.update_document_stats(workspace_id)

    def _cleanup_failed_ingestion(self, document_id: str, workspace_id: str, file_path: str, chunks_count: int):
        """
        Transactional Cleanup: Purges orphaned SQLite chunks and physically deletes
        the corrupt/failed upload file to prevent server disk clutter.
        """
        logger.info(f"Cleaning up failed ingestion artifacts for doc {document_id}...")
        
        # 1. Delete SQLite chunks
        try:
            self.chunk_repo.delete_chunks_by_document(document_id)
        except Exception as sql_err:
            logger.error(f"SQL Cleanup failed: {str(sql_err)}")
            
        # 2. Delete corrupt/failed physical file
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Successfully deleted failed upload file: {file_path}")
            except Exception as io_err:
                logger.warning(f"Could not remove file {file_path}: {str(io_err)}")
                
        # 3. Restore workspace stats
        if chunks_count > 0:
            try:
                # Decrement counts back to pre-ingestion state
                self.workspace_repo.increment_chunk_count(workspace_id, -chunks_count)
                self.workspace_repo.increment_document_count(workspace_id, -1)  # FIX: was +1 (no delta arg)
            except Exception as stats_err:
                logger.warning(f"Failed to restore workspace statistics: {str(stats_err)}")
