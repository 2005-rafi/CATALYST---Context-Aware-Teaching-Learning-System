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
from backend.services.nlp.query_reformulator import QueryReformulatorPipeline

logger = logging.getLogger(__name__)

class RetrievalOrchestratorAgent:
    """
    Agent 1: Intelligent Research & Retrieval Orchestrator.
    Responsible for:
    1. Query Understanding & Corpus-Aware Spelling Recovery (via RapidFuzz against indexed vocabulary)
    2. Multi-Query Formulation ("Never trust correction alone - search original + canonical + concepts")
    3. Disambiguated Intent Classification (Distinguishing Book Structure TOC vs Subject Topics)
    4. Structural / Table-of-Contents Routing (for global book queries)
    5. Multi-Query Hybrid Dense (FAISS) + Sparse (BM25) Retrieval with Reciprocal Rank Fusion (RRF)
    6. Calibrated Sigmoid Cross-Encoder Reranking
    7. Adaptive Evidence Verification & Gap Recovery (auto-retrieves chapter body chunks if only TOC returned)
    8. Context Package Synthesis with Provenance Metadata
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
        self.reformulator = QueryReformulatorPipeline()

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
        # 1. Advanced NLP Query Understanding, Corpus-Aware Spelling & Intent Disambiguation
        nlp_res = self.reformulator.process_query(query, workspace_id)
        canonical_query = nlp_res["canonical_query"]
        intent = nlp_res["intent"]
        retrieval_queries = nlp_res["retrieval_queries"]
        corrections = nlp_res["corrections"]
        
        logger.info(
            f"[Agent 1: RetrievalOrchestrator] Processed query: '{query}' -> '{canonical_query}' "
            f"(intent={intent}, corrections={corrections})"
        )

        # 2. Retrieve Workspace Documents for Grounding Context
        workspace_docs = self.doc_repo.get_documents_by_workspace(workspace_id)
        
        # 3. Multi-Route Retrieval
        candidates: List[Tuple[str, float]] = []

        if intent in ("BOOK_STRUCTURE_TOC", "STRUCTURAL_OVERVIEW"):
            # Path A: Structural / TOC Exploration (strictly for book syllabus/chapter list outline)
            candidates = self._execute_structural_retrieval(workspace_id, canonical_query)
        else:
            # Path B: Multi-Query Hybrid Search (Dense + Sparse + RRF across original + canonical + concepts)
            candidates = self._execute_multi_query_hybrid_retrieval(workspace_id, retrieval_queries)

        # 4. Calibrated Cross-Encoder Reranking
        top_k_rerank = 6
        reranked_chunks: List[RetrievedChunk] = []
        if candidates:
            reranked_chunks = self.cross_encoder_service.rerank(
                query=canonical_query, 
                candidates=candidates, 
                top_n=top_k_rerank
            )

        # 4b. Anchor Primary Structural / TOC Chunks (ONLY for book structure outline queries)
        if intent in ("BOOK_STRUCTURE_TOC", "STRUCTURAL_OVERVIEW"):
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

        # 5. Intent-Guided Context Refinement & Deduplication
        engineered_chunks = self.context_decision_engine.decide(
            query=canonical_query, 
            chunks=reranked_chunks
        )

        # 6. Adaptive Evidence Verification & Gap Recovery Gate
        # If user asked about a specific topic (e.g. Chapter 13 or environmental issues)
        # but only TOC chunks were retrieved, adaptively fetch substantive chapter body chunks
        has_gap, target_query = self.reformulator.detect_evidence_gap(canonical_query, engineered_chunks)
        if has_gap and target_query:
            logger.warning(f"[Agent 1] Adaptive Recovery triggered for gap query: '{target_query}'")
            fallback_candidates = self._execute_multi_query_hybrid_retrieval(workspace_id, [target_query])
            if fallback_candidates:
                fallback_reranked = self.cross_encoder_service.rerank(target_query, fallback_candidates, top_n=5)
                existing_ids = {c.chunk_id for c in engineered_chunks}
                new_body_chunks = [c for c in fallback_reranked if c.chunk_id not in existing_ids]
                if new_body_chunks:
                    logger.info(f"[Agent 1] Adaptive Recovery added {len(new_body_chunks)} body chunks.")
                    engineered_chunks = self.context_decision_engine.decide(canonical_query, new_body_chunks + engineered_chunks)

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

    def _execute_structural_retrieval(self, workspace_id: str, query: str) -> List[Tuple[str, float]]:
        """
        Retrieves structural context (front matter, Table of Contents, chapter listings)
        alongside expanded hybrid keyword search for whole-book outlines.
        """
        candidates_map: Dict[str, float] = {}

        # 1. Fetch Front-Matter and TOC Chunks directly from SQLite
        toc_chunks = self.chunk_repo.get_front_matter_and_toc_chunks(workspace_id, limit=8)
        for rank, chunk in enumerate(toc_chunks):
            chunk_id = chunk["chunk_id"]
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

        sorted_candidates = sorted(candidates_map.items(), key=lambda x: x[1], reverse=True)
        return sorted_candidates[:25]

    def _execute_multi_query_hybrid_retrieval(self, workspace_id: str, queries: List[str]) -> List[Tuple[str, float]]:
        """
        Executes multi-query hybrid retrieval across BM25 and FAISS,
        fusing candidate rankings via Reciprocal Rank Fusion (RRF).
        Follows the core principle: 'Never trust correction alone - search original + canonical + concepts'.
        """
        candidates_map: Dict[str, float] = {}

        for q in queries:
            if not q.strip():
                continue

            # BM25 Lexical Search
            bm25_hits = self.bm25_repo.search(workspace_id, q, top_k=25)
            for rank, (cid, score) in enumerate(bm25_hits):
                rrf_score = 1.0 / (60 + rank + 1)
                candidates_map[cid] = candidates_map.get(cid, 0.0) + rrf_score

            # FAISS Dense Vector Search
            try:
                vec_hits = self.vector_repo.search(workspace_id, q, top_k=25)
                for rank, (cid, score) in enumerate(vec_hits):
                    rrf_score = 1.0 / (60 + rank + 1)
                    candidates_map[cid] = candidates_map.get(cid, 0.0) + rrf_score
            except Exception as e:
                logger.warning(f"[Agent 1] Vector search warning on '{q}': {e}")

        sorted_candidates = sorted(candidates_map.items(), key=lambda x: x[1], reverse=True)
        return sorted_candidates[:35]

    def _normalize_query(self, query: str) -> str:
        """Helper / backward-compatibility normalization for common educational typos."""
        q = query
        typo_map = {
            r'\blession\b': 'lesson',
            r'\blessions\b': 'lessons',
            r'\btihnk\b': 'think',
            r'\bchpater\b': 'chapter',
            r'\bpreventaion\b': 'prevention'
        }
        for pat, rep in typo_map.items():
            q = re.sub(pat, rep, q, flags=re.IGNORECASE)
        return self.reformulator._normalize_whitespace(q)

    def _classify_intent(self, query: str) -> str:
        """Helper / backward-compatibility method delegating to QueryReformulatorPipeline."""
        return self.reformulator.classify_intent(query)

