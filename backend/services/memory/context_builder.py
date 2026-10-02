import logging
import re
from backend.models.chat import RetrievedChunk
from backend.models.context import ContextPackage
from backend.services.retrieval.rrf_engine import RRFEngine
from backend.services.retrieval.cross_encoder_service import CrossEncoderService
from backend.services.retrieval.context_compressor import ContextCompressor
from backend.services.retrieval.confidence_engine import ConfidenceEngine
from backend.services.retrieval.source_attributor import SourceAttributor
from backend.services.retrieval.context_decision_engine import ContextDecisionEngine
from backend.services.memory.context_window import ContextWindow
from backend.repositories.sqlite.workspace_summary_repository import WorkspaceSummaryRepository
from backend.repositories.sqlite.workspace_repository import WorkspaceRepository
from backend.repositories.vector.vector_repository import VectorRepository
from backend.repositories.bm25.bm25_repository import BM25Repository
from backend.repositories.sqlite.chunk_repository import ChunkRepository
from backend.repositories.sqlite.document_repository import DocumentRepository
from backend.services.llm.failover_manager import FailoverManager
from backend.core.config.settings import get_settings

logger = logging.getLogger(__name__)

class ContextBuilder:
    def __init__(self):
        self.settings = get_settings()
        
        # Retrieval components
        self.rrf_engine = RRFEngine()
        self.cross_encoder = CrossEncoderService()
        self.compressor = ContextCompressor()
        self.confidence_engine = ConfidenceEngine()
        self.source_attributor = SourceAttributor()
        self.decision_engine = ContextDecisionEngine()
        self.failover_manager = FailoverManager()
        
        # Repositories
        self.vector_repo = VectorRepository()
        self.bm25_repo = BM25Repository()
        self.chunk_repo = ChunkRepository()
        self.doc_repo = DocumentRepository()
        self.workspace_repo = WorkspaceRepository()
        self.summary_repo = WorkspaceSummaryRepository()
        
        # Memory components
        self.context_window = ContextWindow()

    def build(self, workspace_id: str, query: str, mode: str) -> ContextPackage:
        # Get Workspace Info
        workspace = self.workspace_repo.get_workspace(workspace_id)
        workspace_name = workspace["workspace_name"] if workspace else "Unknown Workspace"
        
        # Fetch conversation history first (used for contextual query reformulation)
        recent_messages = self.context_window.get_recent_context(workspace_id)
        
        # Perform query reformulation to rewrite pronouns and references using LLM
        search_query = self._reformulate_query(query, recent_messages)
        logger.info(f"Query reformulated for retrieval: '{query}' -> '{search_query}'")
        
        # Retrieval Pipeline
        # FAISS Stage
        try:
            faiss_results = self.vector_repo.search(workspace_id, search_query, top_k=self.settings.FAISS_TOP_K)
        except Exception as e:
            logger.error(f"FAISS search failed: {e}")
            faiss_results = []
            
        # BM25 Stage (FTS5 SQLite backed)
        try:
            bm25_results = self.bm25_repo.search(workspace_id, search_query, top_k=self.settings.BM25_TOP_K)
        except Exception as e:
            logger.warning(f"BM25 search failed, using FAISS-only. Error: {e}")
            bm25_results = []
        
        # RRF Stage
        rrf_results = self.rrf_engine.fuse([faiss_results, bm25_results], top_n=20)
        
        # CrossEncoder Stage (using reformulated search query for deep correlation scoring)
        try:
            reranked_chunks = self.cross_encoder.rerank(search_query, rrf_results, top_n=5)
        except Exception as e:
            logger.warning(f"Cross-encoder reranking failed, using RRF results. Error: {e}")
            # Fallback: convert top-5 RRF results directly to RetrievedChunk objects
            reranked_chunks = []
            fallback_rrf = rrf_results[:5]
            if fallback_rrf:
                chunk_ids = [c[0] for c in fallback_rrf]
                chunks_data = self.chunk_repo.get_chunks_by_ids(chunk_ids)
                chunk_dict = {c["chunk_id"]: c for c in chunks_data}
                
                doc_cache = {}
                for chunk_id, score in fallback_rrf:
                    if chunk_id in chunk_dict:
                        c_data = chunk_dict[chunk_id]
                        doc_id = c_data["document_id"]
                        if doc_id not in doc_cache:
                            doc = self.doc_repo.get_document(doc_id)
                            doc_cache[doc_id] = doc["file_name"] if doc else "Unknown"
                            
                        reranked_chunks.append(
                            RetrievedChunk(
                                chunk_id=chunk_id,
                                document_id=doc_id,
                                source_file=doc_cache[doc_id],
                                chunk_text=c_data["chunk_text"],
                                score=float(score),
                                page_number=c_data.get("page_number"),
                                section_heading=c_data.get("section_heading")
                            )
                        )
        
        # Compression and Context Decision Engine (using original conversational query for downstream response rules)
        compressed_chunks = self.compressor.compress(reranked_chunks)
        engineered_chunks = self.decision_engine.decide(query, compressed_chunks)
        confidence = self.confidence_engine.evaluate(engineered_chunks)
        sources = self.source_attributor.extract_sources(engineered_chunks)
        
        summary_record = self.summary_repo.get_summary(workspace_id)
        workspace_summary = summary_record["summary_text"] if summary_record else ""
        
        return ContextPackage(
            query=query,
            workspace_id=workspace_id,
            workspace_name=workspace_name,
            retrieved_chunks=engineered_chunks,
            recent_messages=recent_messages,
            workspace_summary=workspace_summary,
            confidence=confidence,
            sources=sources,
            mode=mode
        )

    def _reformulate_query(self, query: str, recent_messages: list[dict]) -> str:
        """
        Reformulates conversational user query into a standalone query containing all necessary
        historical entities and context using a lightweight LLM.
        """
        if not recent_messages:
            return query
            
        system_instructions = (
            "You are a query reformulation assistant. Given the following conversation history and a follow-up query, "
            "rewrite the query to be a standalone search query that contains all necessary context, pronouns, and references. "
            "Do NOT answer the question. Only output the reformulated query text and nothing else."
        )
        
        # Format the last 3 turns of message context
        history_text = ""
        for msg in recent_messages[-3:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['message']}\n"
            
        user_prompt = f"History:\n{history_text}\nFollow-up query: {query}\nReformulated query:"
        
        messages = [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            # We call in simple/local mode for fast reformulation latency
            response, _ = self.failover_manager.generate(messages, mode="simple")
            cleaned_response = response.strip()
            # Safety check: if response returned is empty or matches error alerts, fallback to original query
            if cleaned_response and "unavailable" not in cleaned_response.lower() and len(cleaned_response) < 300:
                return cleaned_response
        except Exception:
            pass
            
        return query
