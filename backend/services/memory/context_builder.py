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
from backend.repositories.sqlite.workspace_repository import WorkspaceRepository
from backend.repositories.vector.vector_repository import VectorRepository
from backend.repositories.bm25.bm25_repository import BM25Repository
from backend.repositories.sqlite.chunk_repository import ChunkRepository
from backend.repositories.sqlite.document_repository import DocumentRepository
from backend.services.llm.failover_manager import FailoverManager
from backend.services.memory.conversation_intelligence_manager import ConversationIntelligenceManager
from backend.services.memory.memory_profile_engine import MemoryProfileEngine
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

        # Conversational Intelligence (replaces direct ContextWindow + SummaryRepo)
        self.ci_manager = ConversationIntelligenceManager()
        self.profile_engine = MemoryProfileEngine()

    def build(self, workspace_id: str, query: str, mode: str) -> ContextPackage:
        # Get workspace metadata
        workspace = self.workspace_repo.get_workspace(workspace_id)
        workspace_name = workspace["workspace_name"] if workspace else "Unknown Workspace"

        # 1. Assemble CI memory package (session, history, profile, summary — all budgeted)
        memory = self.ci_manager.assemble_memory(workspace_id, mode)

        # 2. Query reformulation using session-scoped history
        search_query = self._reformulate_query(query, memory.recent_messages)
        logger.info(f"Query reformulated: '{query}' -> '{search_query}'")

        # 3. FAISS retrieval
        try:
            faiss_results = self.vector_repo.search(
                workspace_id, search_query, top_k=self.settings.FAISS_TOP_K
            )
        except Exception as e:
            logger.error(f"FAISS search failed: {e}")
            faiss_results = []

        # 4. BM25 retrieval (FTS5 SQLite backed)
        try:
            bm25_results = self.bm25_repo.search(
                workspace_id, search_query, top_k=self.settings.BM25_TOP_K
            )
        except Exception as e:
            logger.warning(f"BM25 search failed, using FAISS-only: {e}")
            bm25_results = []

        # 5. RRF fusion
        rrf_results = self.rrf_engine.fuse([faiss_results, bm25_results], top_n=20)

        # 6. Cross-encoder reranking
        try:
            reranked_chunks = self.cross_encoder.rerank(search_query, rrf_results, top_n=5)
        except Exception as e:
            logger.warning(f"Cross-encoder failed, using RRF fallback: {e}")
            reranked_chunks = self._rrf_fallback(rrf_results[:5])

        # 7. Context engineering pipeline
        compressed_chunks = self.compressor.compress(reranked_chunks)
        engineered_chunks = self.decision_engine.decide(query, compressed_chunks)
        confidence = self.confidence_engine.evaluate(engineered_chunks)
        sources = self.source_attributor.extract_sources(engineered_chunks)

        # 8. Extract topics from retrieved chunks (for profile update)
        detected_topics = self._extract_topics_from_chunks(engineered_chunks)

        return ContextPackage(
            query=query,
            workspace_id=workspace_id,
            workspace_name=workspace_name,
            retrieved_chunks=engineered_chunks,
            recent_messages=memory.recent_messages,
            workspace_summary=memory.workspace_summary,
            confidence=confidence,
            sources=sources,
            mode=mode,
            # CI fields
            session_id=memory.session_id,
            memory_profile_snippet=memory.profile_snippet,
            detected_topics=detected_topics,
        )

    def _reformulate_query(self, query: str, recent_messages: list[dict]) -> str:
        """
        Reformulates a conversational query into a standalone search query
        using a lightweight LLM call to resolve pronouns and references.
        """
        if not recent_messages:
            return query

        system_instructions = (
            "You are a query reformulation assistant. Given the following conversation history and a follow-up query, "
            "rewrite the query to be a standalone search query that contains all necessary context, pronouns, and references. "
            "Do NOT answer the question. Only output the reformulated query text and nothing else."
        )

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
            response, _ = self.failover_manager.generate(messages, mode="simple")
            cleaned = response.strip()
            if cleaned and "unavailable" not in cleaned.lower() and len(cleaned) < 300:
                return cleaned
        except Exception:
            pass

        return query

    def _rrf_fallback(self, rrf_results: list) -> list[RetrievedChunk]:
        """Fallback when cross-encoder fails — converts top RRF results directly."""
        if not rrf_results:
            return []
        chunk_ids = [c[0] for c in rrf_results]
        chunks_data = self.chunk_repo.get_chunks_by_ids(chunk_ids)
        chunk_dict = {c["chunk_id"]: c for c in chunks_data}
        doc_cache: dict[str, str] = {}
        result: list[RetrievedChunk] = []
        for chunk_id, score in rrf_results:
            if chunk_id not in chunk_dict:
                continue
            c_data = chunk_dict[chunk_id]
            doc_id = c_data["document_id"]
            if doc_id not in doc_cache:
                doc = self.doc_repo.get_document(doc_id)
                doc_cache[doc_id] = doc["file_name"] if doc else "Unknown"
            result.append(RetrievedChunk(
                chunk_id=chunk_id,
                document_id=doc_id,
                source_file=doc_cache[doc_id],
                chunk_text=c_data["chunk_text"],
                score=float(score),
                page_number=c_data.get("page_number"),
                section_heading=c_data.get("section_heading")
            ))
        return result

    def _extract_topics_from_chunks(self, chunks: list[RetrievedChunk]) -> list[str]:
        """Extract topic keywords from retrieved chunks for profile tagging."""
        if not chunks:
            return []
        combined = " ".join(c.chunk_text for c in chunks[:3])
        return self.profile_engine.extract_topics_from_text(combined, top_n=5)
