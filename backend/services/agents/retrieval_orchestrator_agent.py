import re
import logging
from typing import List, Tuple, Dict, Any, Optional

from backend.models.context import ContextPackage
from backend.models.chat import RetrievedChunk
from backend.repositories.sqlite.chunk_repository import ChunkRepository
from backend.repositories.sqlite.document_repository import DocumentRepository
from backend.repositories.sqlite.workspace_repository import WorkspaceRepository
from backend.repositories.bm25.bm25_repository import BM25Repository
from backend.repositories.vector.vector_repository import VectorRepository
from backend.services.retrieval.cross_encoder_service import CrossEncoderService
from backend.services.retrieval.context_decision_engine import ContextDecisionEngine
from backend.services.retrieval.confidence_engine import ConfidenceEngine
from backend.services.retrieval.source_attributor import SourceAttributor
from backend.services.memory.context_window import ContextWindow

logger = logging.getLogger(__name__)

class RetrievalOrchestratorAgent:
    """
    Agent 1: Intelligent Research & Retrieval Orchestrator.
    Responsible for:
    1. Query Intent Classification & Deconstruction
    2. Typo Normalization & Multi-Query Expansion
    3. Structural / Table-of-Contents Routing (for global book queries)
    4. Hybrid Dense (FAISS) + Sparse (BM25) Retrieval with Reciprocal Rank Fusion (RRF)
    5. Calibrated Cross-Encoder Reranking
    6. Context Package Synthesis with Provenance Metadata
    """
    def __init__(self):
        self.chunk_repo = ChunkRepository()
        self.doc_repo = DocumentRepository()
        self.workspace_repo = WorkspaceRepository()
        self.bm25_repo = BM25Repository()
        self.vector_repo = VectorRepository()
        self.cross_encoder_service = CrossEncoderService()
        self.context_decision_engine = ContextDecisionEngine()
        self.confidence_engine = ConfidenceEngine()
        self.source_attributor = SourceAttributor()
        self.context_window = ContextWindow()

    def orchestrate(
        self, 
        workspace_id: str, 
        query: str, 
        mode: str = "expert", 
        session_id: Optional[str] = None
    ) -> ContextPackage:
        """
        Executes end-to-end multi-stage agentic retrieval and evidence structuring.
        """
        # 1. Query Normalization & Typo Repair
        normalized_query = self._normalize_query(query)
        logger.info(f"[Agent 1: RetrievalOrchestrator] Normalized query: '{query}' -> '{normalized_query}'")

        # 2. Intent Classification
        intent = self._classify_intent(normalized_query)
        logger.info(f"[Agent 1: RetrievalOrchestrator] Detected Query Intent: {intent}")

        # 3. Retrieve Workspace Documents for Grounding Context
        workspace_docs = self.doc_repo.get_documents_by_workspace(workspace_id)
        
        # 4. Multi-Route Retrieval
        candidates: List[Tuple[str, float]] = []

        if intent == "STRUCTURAL_OVERVIEW":
            # Path A: Structural / TOC Exploration
            candidates = self._execute_structural_retrieval(workspace_id, normalized_query)
        else:
            # Path B: Standard Hybrid Search (Dense + Sparse + RRF)
            candidates = self._execute_hybrid_retrieval(workspace_id, normalized_query)

        # 5. Calibrated Cross-Encoder Reranking
        top_k_rerank = 6
        reranked_chunks: List[RetrievedChunk] = []
        if candidates:
            reranked_chunks = self.cross_encoder_service.rerank(
                query=normalized_query, 
                candidates=candidates, 
                top_n=top_k_rerank
            )

        # 5b. Anchor Primary Structural / TOC Chunks (for global book overview queries)
        if intent == "STRUCTURAL_OVERVIEW":
            raw_toc_chunks = self.chunk_repo.get_front_matter_and_toc_chunks(workspace_id, limit=8)
            for c in raw_toc_chunks:
                text = c["chunk_text"]
                if "CONTENTS" in text or "Table of Contents" in text or "Chapter 1" in text:
                    doc = self.doc_repo.get_document(c["document_id"])
                    doc_name = doc["file_name"] if doc else "Document"
                    anchor_chunk = RetrievedChunk(
                        chunk_id=c["chunk_id"],
                        document_id=c["document_id"],
                        source_file=doc_name,
                        chunk_text=text,
                        score=0.98,
                        page_number=c.get("page_number", 1),
                        section_heading=c.get("section_heading") or "Table of Contents"
                    )
                    reranked_chunks = [ch for ch in reranked_chunks if ch.chunk_id != c["chunk_id"]]
                    reranked_chunks.insert(0, anchor_chunk)
                    break

        # 6. Intent-Guided Context Refinement & Deduplication
        engineered_chunks = self.context_decision_engine.decide(
            query=normalized_query, 
            chunks=reranked_chunks
        )

        # 7. Confidence & Grounding Evaluation
        confidence = self.confidence_engine.evaluate(engineered_chunks)
        logger.info(
            f"[Agent 1: RetrievalOrchestrator] Confidence: {confidence.level} "
            f"(chunks={confidence.chunk_count}, sufficient={confidence.sufficient})"
        )

        # 8. Workspace Summary & Session Context
        workspace = self.workspace_repo.get_workspace(workspace_id)
        workspace_summary = ""
        if workspace:
            doc_summaries = [f"- {d['file_name']} ({d.get('total_chunks', 0)} chunks)" for d in workspace_docs]
            docs_text = "\n".join(doc_summaries) if doc_summaries else "None"
            workspace_name = workspace.get("workspace_name", "Default")
            workspace_summary = (
                f"Workspace: {workspace_name}\n"
                f"Uploaded Workspace Files:\n{docs_text}"
            )

        recent_messages = self.context_window.get_recent_context(workspace_id)
        sources = self.source_attributor.extract_sources(engineered_chunks)

        return ContextPackage(
            workspace_id=workspace_id,
            workspace_name=workspace_name,
            query=query,
            retrieved_chunks=engineered_chunks,
            confidence=confidence,
            sources=sources,
            workspace_summary=workspace_summary,
            recent_messages=recent_messages,
            mode=mode
        )

    def _normalize_query(self, query: str) -> str:
        """
        Normalizes common academic and typographic errors in queries.
        """
        q = query.strip()
        # Common typos in academic student inquiries
        replacements = [
            (r'\blession\b', 'lesson'),
            (r'\blessions\b', 'lessons'),
            (r'\bchater\b', 'chapter'),
            (r'\bchaters\b', 'chapters'),
            (r'\bsylabus\b', 'syllabus'),
            (r'\btopicss\b', 'topics'),
            (r'\bzoologyy\b', 'zoology'),
            (r'\bbiologi\b', 'biology')
        ]
        for pattern, repl in replacements:
            q = re.sub(pattern, repl, q, flags=re.IGNORECASE)
        return q

    def _classify_intent(self, query: str) -> str:
        """
        Classifies intent into structural, factoid, conceptual, comparative, or quantitative.
        """
        q_lower = query.lower()

        # Structural & Overview queries (TOC, lesson lists, chapter counts, syllabus)
        structural_keywords = [
            "lesson", "lessons", "chapter", "chapters", "table of contents", "contents", 
            "index", "syllabus", "curriculum", "all topics", "list all", "how many chapter", 
            "how many lesson", "book overview", "units", "unit i", "unit 1"
        ]
        if any(kw in q_lower for kw in structural_keywords):
            return "STRUCTURAL_OVERVIEW"

        comparative_keywords = ["vs", "versus", "difference between", "compare", "contrast", "distinguish"]
        if any(kw in q_lower for kw in comparative_keywords):
            return "COMPARATIVE"

        quantitative_keywords = ["count", "number of", "percentage", "formula", "ratio", "how many", "total"]
        if any(kw in q_lower for kw in quantitative_keywords):
            return "QUANTITATIVE"

        pedagogical_keywords = ["explain", "mechanism", "how does", "why does", "describe", "steps", "process", "pathway"]
        if any(kw in q_lower for kw in pedagogical_keywords):
            return "CONCEPTUAL"

        return "FACTOID"

    def _execute_structural_retrieval(self, workspace_id: str, query: str) -> List[Tuple[str, float]]:
        """
        Retrieves structural context (front matter, Table of Contents, chapter listings)
        alongside expanded hybrid keyword search.
        """
        candidates_map: Dict[str, float] = {}

        # 1. Fetch Front-Matter and TOC Chunks directly from SQLite
        toc_chunks = self.chunk_repo.get_front_matter_and_toc_chunks(workspace_id, limit=8)
        for rank, chunk in enumerate(toc_chunks):
            chunk_id = chunk["chunk_id"]
            # Structural chunks get strong initial baseline prior
            candidates_map[chunk_id] = 1.0 / (20 + rank)

        # 2. Query expansion tailored for structural retrieval
        structural_queries = [
            query,
            "CONTENTS Chapters Units",
            "Table of Contents Reproduction Genetics Evolution",
            "Chapter 1 Chapter 2 Chapter 3"
        ]

        # 3. Sparse & Dense Search on structural queries
        for sq in structural_queries:
            bm25_hits = self.bm25_repo.search(workspace_id, sq, top_k=15)
            for rank, (cid, score) in enumerate(bm25_hits):
                rrf_score = 1.0 / (60 + rank + 1)
                candidates_map[cid] = candidates_map.get(cid, 0.0) + rrf_score

            try:
                vec_hits = self.vector_repo.search(workspace_id, sq, top_k=15)
                for rank, (cid, score) in enumerate(vec_hits):
                    rrf_score = 1.0 / (60 + rank + 1)
                    candidates_map[cid] = candidates_map.get(cid, 0.0) + rrf_score
            except Exception as e:
                logger.warning(f"[Agent 1] Vector search warning: {e}")

        # Sort combined candidates descending by fusion score
        sorted_candidates = sorted(candidates_map.items(), key=lambda x: x[1], reverse=True)
        return sorted_candidates[:25]

    def _execute_hybrid_retrieval(self, workspace_id: str, query: str) -> List[Tuple[str, float]]:
        """
        Standard hybrid retrieval using BM25, FAISS, and Reciprocal Rank Fusion (RRF).
        """
        candidates_map: Dict[str, float] = {}

        # BM25 Lexical Search
        bm25_hits = self.bm25_repo.search(workspace_id, query, top_k=25)
        for rank, (cid, score) in enumerate(bm25_hits):
            rrf_score = 1.0 / (60 + rank + 1)
            candidates_map[cid] = candidates_map.get(cid, 0.0) + rrf_score

        # FAISS Dense Vector Search
        try:
            vec_hits = self.vector_repo.search(workspace_id, query, top_k=25)
            for rank, (cid, score) in enumerate(vec_hits):
                rrf_score = 1.0 / (60 + rank + 1)
                candidates_map[cid] = candidates_map.get(cid, 0.0) + rrf_score
        except Exception as e:
            logger.warning(f"[Agent 1] Vector search warning: {e}")

        sorted_candidates = sorted(candidates_map.items(), key=lambda x: x[1], reverse=True)
        return sorted_candidates[:30]
