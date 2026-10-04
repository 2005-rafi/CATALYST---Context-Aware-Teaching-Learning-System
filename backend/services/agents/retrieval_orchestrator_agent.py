import re
import logging
from typing import List, Tuple, Dict, Any, Optional

from backend.models.context import ContextPackage
from backend.models.chat import RetrievedChunk
from backend.repositories.sqlite.chunk_repository import ChunkRepository
from backend.repositories.sqlite.document_repository import DocumentRepository
from backend.repositories.sqlite.workspace_repository import WorkspaceRepository
from backend.repositories.sqlite.figure_repository import FigureRepository
from backend.repositories.bm25.bm25_repository import BM25Repository
from backend.repositories.vector.vector_repository import VectorRepository
from backend.services.retrieval.cross_encoder_service import CrossEncoderService
from backend.services.retrieval.context_decision_engine import ContextDecisionEngine
from backend.services.retrieval.confidence_engine import ConfidenceEngine
from backend.services.retrieval.source_attributor import SourceAttributor
from backend.services.retrieval.chunk_evaluator_engine import ChunkEvaluatorEngine
from backend.services.memory.context_window import ContextWindow
from backend.services.memory.conversation_intelligence_manager import ConversationIntelligenceManager
from backend.services.memory.token_budget_manager import TokenBudgetManager
from backend.repositories.sqlite.conversation_repository import ConversationRepository
from backend.services.nlp.query_reformulator import QueryReformulatorPipeline

logger = logging.getLogger(__name__)

class RetrievalOrchestratorAgent:
    """
    Agent 1: Intelligent Research & Retrieval Orchestrator.
    Responsible for:
    1. Query Understanding & Corpus-Aware Spelling Recovery
    2. Multi-Query Formulation (Original + Canonical + Concepts)
    3. Disambiguated Intent Classification (Structural/TOC vs Substantive Topic vs Exam Prep vs User History Meta)
    4. Multi-Route Retrieval (Structural TOC Indexing + Dense FAISS + Sparse BM25 + Meta-Conversation History)
    5. Reciprocal Rank Fusion (RRF) & Neural Cross-Encoder Reranking
    6. Multi-Dimensional Quality & Coverage Chunk Evaluation (via ChunkEvaluatorEngine)
    7. Adaptive Recovery, Dynamic Topic Extraction & Strict Free-Tier Token Budgeting
    """
    def __init__(self):
        self.chunk_repo = ChunkRepository()
        self.doc_repo = DocumentRepository()
        self.workspace_repo = WorkspaceRepository()
        self.conversation_repo = ConversationRepository()
        self.figure_repo = FigureRepository()
        self.bm25_repo = BM25Repository()
        self.vector_repo = VectorRepository()
        self.cross_encoder_service = CrossEncoderService()
        self.context_decision_engine = ContextDecisionEngine()
        self.confidence_engine = ConfidenceEngine()
        self.chunk_evaluator = ChunkEvaluatorEngine()
        self.source_attributor = SourceAttributor()
        self.context_window = ContextWindow()
        self.ci_manager = ConversationIntelligenceManager()
        self.token_budget = TokenBudgetManager()
        self.reformulator = QueryReformulatorPipeline()

    def orchestrate(
        self, 
        workspace_id: str, 
        query: str, 
        mode: str = "expert", 
        session_id: Optional[str] = None
    ) -> ContextPackage:
        """
        Executes end-to-end multi-stage agentic retrieval, quality scoring, and evidence structuring.
        """
        # 1. Advanced NLP Query Understanding & Spelling Recovery
        nlp_res = self.reformulator.process_query(query, workspace_id)
        canonical_query = nlp_res["canonical_query"]
        intent = nlp_res["intent"]
        retrieval_queries = nlp_res["retrieval_queries"]
        corrections = nlp_res["corrections"]
        
        logger.info(
            f"[Agent 1: RetrievalOrchestrator] Processed query: '{query}' -> '{canonical_query}' "
            f"(intent={intent}, corrections={corrections})"
        )

        # 2. Retrieve Workspace Documents
        workspace_docs = self.doc_repo.get_documents_by_workspace(workspace_id)
        
        engineered_chunks: List[RetrievedChunk] = []

        if intent == "USER_META_CONVERSATION":
            # Path S: Meta-Conversation & User Learning History Query
            user_queries = self.conversation_repo.get_all_user_queries_for_workspace(workspace_id)
            profile = self.ci_manager.profile_engine.get_or_create_profile(workspace_id)
            sessions = self.conversation_repo.get_workspace_session_digests(workspace_id)

            history_lines = ["=== Workspace User Query History & Learning Log ==="]
            if user_queries:
                history_lines.append(f"Total Questions Submitted Across All Sessions: {len(user_queries)}")
                
                # Deduplicate queries while preserving chronological order of first appearance
                query_counts: dict[str, dict] = {}
                for uq in user_queries:
                    msg = uq.get("message", "").strip()
                    if not msg:
                        continue
                    if msg not in query_counts:
                        query_counts[msg] = {
                            "count": 1,
                            "session_name": uq.get("session_name", "General"),
                            "created_at": uq.get("created_at", "")[:16].replace("T", " ")
                        }
                    else:
                        query_counts[msg]["count"] += 1

                history_lines.append("Past Inquiries by User:")
                for idx, (q_text, meta) in enumerate(list(query_counts.items())[:15]):
                    suffix = f" (asked {meta['count']}x)" if meta['count'] > 1 else ""
                    history_lines.append(f"{idx+1}. [{meta['session_name']} | {meta['created_at']}] \"{q_text}\"{suffix}")
            else:
                history_lines.append("No previous questions have been asked in this workspace yet. This is your first interaction.")

            # Add Sessions and Topic Summary
            if sessions:
                history_lines.append("\nConversation Threads in Workspace:")
                for s in sessions[:5]:
                    history_lines.append(f"- \"{s.get('session_name', 'General')}\" ({s.get('message_count', 0)} messages)")

            if profile.topic_familiarity:
                topics_summary = [f"{t} ({int(score*100)}% familiarity)" for t, score in list(profile.topic_familiarity.items())[:8]]
                history_lines.append(f"\nExplored Topics & Mastery: {', '.join(topics_summary)}")
            if profile.struggle_topics:
                history_lines.append(f"Flagged Review Areas: {', '.join(profile.struggle_topics[:5])}")

            meta_text = "\n".join(history_lines)
            meta_chunk = RetrievedChunk(
                chunk_id="user-meta-history-summary",
                document_id="conversation-history",
                source_file="Workspace Memory Profile",
                chunk_text=meta_text,
                score=1.0,
                page_number=1,
                section_heading="User Activity & Learning Log"
            )
            engineered_chunks = [meta_chunk]
        elif intent in ("BOOK_STRUCTURE_TOC", "STRUCTURAL_OVERVIEW"):
            # Path A: Structural / TOC Exploration (strictly for book syllabus/chapter list outline)
            candidates = self._execute_structural_retrieval(workspace_id, canonical_query)
            top_k_rerank = 8
            reranked_chunks: List[RetrievedChunk] = []
            if candidates:
                reranked_chunks = self.cross_encoder_service.rerank(
                    query=canonical_query, 
                    candidates=candidates, 
                    top_n=top_k_rerank
                )

            # Anchor Primary Structural / TOC Chunks
            raw_toc_chunks = self.chunk_repo.get_front_matter_and_toc_chunks(workspace_id, limit=8)
            for c in raw_toc_chunks:
                text = c["chunk_text"]
                if "CONTENTS" in text or "Table of Contents" in text or "Chapter 1" in text or "UNIT I" in text:
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

            engineered_chunks = self.context_decision_engine.decide(
                query=canonical_query, 
                chunks=reranked_chunks
            )
        else:
            # Path B: Multi-Query Hybrid Search (Dense + Sparse + RRF across queries)
            candidates = self._execute_multi_query_hybrid_retrieval(workspace_id, retrieval_queries)
            top_k_rerank = 8
            reranked_chunks: List[RetrievedChunk] = []
            if candidates:
                reranked_chunks = self.cross_encoder_service.rerank(
                    query=canonical_query, 
                    candidates=candidates, 
                    top_n=top_k_rerank
                )

            engineered_chunks = self.context_decision_engine.decide(
                query=canonical_query, 
                chunks=reranked_chunks
            )

            # Quality Scoring & Chunk Evaluation
            eval_result = self.chunk_evaluator.evaluate(
                query=canonical_query,
                intent=intent,
                chunks=engineered_chunks,
                workspace_docs_count=len(workspace_docs)
            )

            # Adaptive Recovery Loop if Gap Detected
            if eval_result.suggested_action == "RETRY_STRUCTURAL":
                logger.warning("[Agent 1] Chunk Evaluator detected missing TOC. Triggering Structural Recovery...")
                raw_toc_chunks = self.chunk_repo.get_front_matter_and_toc_chunks(workspace_id, limit=8)
                for c in raw_toc_chunks:
                    text = c["chunk_text"]
                    if "CONTENTS" in text or "Chapter 1" in text or "UNIT" in text:
                        doc = self.doc_repo.get_document(c["document_id"])
                        doc_name = doc["file_name"] if doc else "Document"
                        toc_chunk = RetrievedChunk(
                            chunk_id=c["chunk_id"],
                            document_id=c["document_id"],
                            source_file=doc_name,
                            chunk_text=text,
                            score=0.95,
                            page_number=c.get("page_number", 1),
                            section_heading=c.get("section_heading") or "Table of Contents"
                        )
                        engineered_chunks.insert(0, toc_chunk)
                        break

            elif eval_result.suggested_action == "RETRY_BODY_EXPANSION":
                has_gap, target_query = self.reformulator.detect_evidence_gap(canonical_query, engineered_chunks)
                if has_gap and target_query:
                    logger.warning(f"[Agent 1] Adaptive Recovery triggered for body gap query: '{target_query}'")
                    fallback_candidates = self._execute_multi_query_hybrid_retrieval(workspace_id, [target_query])
                    if fallback_candidates:
                        fallback_reranked = self.cross_encoder_service.rerank(target_query, fallback_candidates, top_n=5)
                        existing_ids = {c.chunk_id for c in engineered_chunks}
                        new_body_chunks = [c for c in fallback_reranked if c.chunk_id not in existing_ids]
                        if new_body_chunks:
                            logger.info(f"[Agent 1] Adaptive Recovery added {len(new_body_chunks)} body chunks.")
                            engineered_chunks = self.context_decision_engine.decide(canonical_query, new_body_chunks + engineered_chunks)

        # 4. Confidence & Grounding Evaluation
        confidence = self.confidence_engine.evaluate(engineered_chunks)
        if eval_result and eval_result.is_out_of_box:
            confidence.level = "LOW"
            confidence.sufficient = False
            confidence.message = (
                f"Out-of-box context required: query topics {eval_result.uncovered_topics} "
                f"are not covered in uploaded workspace documents."
            )
        elif intent == "USER_META_CONVERSATION":
            confidence.sufficient = True
            confidence.level = "HIGH"

        logger.info(
            f"[Agent 1: RetrievalOrchestrator] Confidence: {confidence.level} "
            f"(chunks={confidence.chunk_count}, sufficient={confidence.sufficient}, is_out_of_box={eval_result.is_out_of_box if eval_result else False})"
        )

        # 5. Extract Dynamic Domain Topics for Memory Profile Tracking
        query_topics = self.reformulator.extract_topics(canonical_query, workspace_id)
        chunk_topics: list[str] = []
        for c in engineered_chunks[:3]:
            chunk_topics.extend(self.reformulator.extract_topics(c.chunk_text, workspace_id))
        detected_topics = list(dict.fromkeys(query_topics + chunk_topics))[:6]

        # 6. Strict Free-Tier Token Budgeting
        budget = self.token_budget.get_budget(mode)
        budgeted_chunks = self.token_budget.allocate_evidence(engineered_chunks, budget["evidence"])

        # 7. Workspace Summary & Session Context
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

        if session_id:
            raw_messages = self.context_window.get_recent_context_for_session(workspace_id, session_id)
        else:
            raw_messages = self.context_window.get_recent_context(workspace_id)

        budgeted_messages = self.token_budget.allocate_history(raw_messages, budget["history"])
        profile_snippet = self.ci_manager.profile_engine.get_profile_context_snippet(workspace_id)
        workspace_memory_bank = self.ci_manager.build_workspace_memory_bank(workspace_id)

        is_oob = bool(eval_result and eval_result.is_out_of_box)
        uncovered = eval_result.uncovered_topics if eval_result else []
        sources = self.source_attributor.extract_sources(budgeted_chunks) if not is_oob else []
        retrieved_figures = self._resolve_figure_references(workspace_id, canonical_query, budgeted_chunks) if not is_oob else []

        return ContextPackage(
            workspace_id=workspace_id,
            workspace_name=workspace_name,
            query=query,
            retrieved_chunks=budgeted_chunks if not is_oob else [],
            confidence=confidence,
            sources=sources,
            workspace_summary=workspace_summary,
            recent_messages=budgeted_messages,
            session_id=session_id or "",
            memory_profile_snippet=profile_snippet,
            workspace_memory_bank=workspace_memory_bank,
            detected_topics=detected_topics,
            mode=mode,
            retrieved_figures=retrieved_figures,
            is_out_of_box=is_oob,
            uncovered_topics=uncovered,
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
            "Chapter 1 Chapter 2 Chapter 3",
            "Chapter 10 Applications of Biotechnology Environmental Issues"
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
        return self.reformulator._apply_pre_typo_fixes(query)

    def _classify_intent(self, query: str) -> str:
        return self.reformulator.classify_intent(query)

    def _resolve_figure_references(
        self,
        workspace_id: str,
        query: str,
        chunks: List[RetrievedChunk],
    ) -> List[dict]:
        """
        Visual RAG: Resolves relevant figure crops from the workspace figure repository.
        Enforces strict semantic/keyword relevance so unrelated figures (e.g. reproductive
        anatomy diagrams for digestive queries) are NEVER attached to answers.
        """
        if not chunks:
            return []

        # Extract specific substantive query terms (excluding generic structural filler)
        q_words = re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())
        generic_stopwords = {
            "explain", "what", "tell", "give", "show", "describe", "with", "from",
            "this", "that", "your", "have", "diagram", "diagrams", "figure", "figures",
            "image", "images", "chart", "charts", "illustration", "illustrations",
            "system", "systems", "human", "body", "living", "organism", "organisms",
            "biology", "science", "structure", "function", "functions", "process", "overview"
        }
        specific_keywords = {w for w in q_words if w not in generic_stopwords}
        target_keywords = specific_keywords if specific_keywords else {w for w in q_words if len(w) > 3}

        retrieved_ids = {c.chunk_id for c in chunks}
        # Only consider pages from chunks with meaningful relevance score
        retrieved_pages = {
            (c.document_id, c.page_number) 
            for c in chunks 
            if c.page_number and getattr(c, 'score', 0) >= 0.35
        }
        figures: List[dict] = []
        seen_figure_ids: set = set()

        try:
            workspace_figures = self.figure_repo.get_figures_by_workspace(workspace_id)
            for fig in workspace_figures:
                figure_id = fig.get("figure_id", "")
                embedding_ref = fig.get("embedding_ref", "")
                doc_id = fig.get("document_id", "")
                page_num = fig.get("page_number", 0)

                caption = fig.get("caption_text", "").strip() or fig.get("context_text", "").strip()
                caption_lower = caption.lower()

                # Semantic & keyword relevance check:
                # Figure MUST match at least one specific query keyword
                has_keyword_match = any(kw in caption_lower for kw in target_keywords) if target_keywords else True

                # Direct match: vector/lexical hit on figure
                is_direct_hit = (figure_id in retrieved_ids or (embedding_ref and embedding_ref in retrieved_ids)) and has_keyword_match
                # Spatial match: figure on same page as a relevant retrieved text chunk AND keyword matches
                is_spatial_hit = (doc_id, page_num) in retrieved_pages and has_keyword_match

                if is_direct_hit or is_spatial_hit:
                    if figure_id in seen_figure_ids:
                        continue
                    seen_figure_ids.add(figure_id)

                    doc = self.doc_repo.get_document(doc_id)
                    doc_name = doc["file_name"] if doc else "Document"

                    figures.append({
                        "figure_id": figure_id,
                        "caption": caption[:300] if caption else f"Figure on page {page_num}",
                        "figure_type": fig.get("figure_type", "unknown"),
                        "page_number": page_num,
                        "document_name": doc_name,
                        "url": f"/api/v1/figures/{figure_id}?workspace_id={workspace_id}",
                    })

                    if len(figures) >= 5:  # Cap at 5 figures per response
                        break

        except Exception as e:
            logger.warning(f"[Agent 1] Figure resolution failed: {e}")

        return figures
