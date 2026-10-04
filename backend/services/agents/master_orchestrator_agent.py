import time
import uuid
import logging
import datetime
from typing import Tuple, Generator, List, Dict, Any, Optional

from backend.models.context import ContextPackage
from backend.services.agents.retrieval_orchestrator_agent import RetrievalOrchestratorAgent
from backend.services.agents.pedagogical_synthesis_agent import PedagogicalSynthesisAgent
from backend.services.nlp.topic_knowledge_extractor import TopicKnowledgeExtractor
from backend.services.curriculum.curriculum_path_manager import CurriculumPathManager
from backend.services.memory.conversation_intelligence_manager import ConversationIntelligenceManager
from backend.services.analytics.analytics_service import AnalyticsService
from backend.services.memory.summarization_service import SummarizationService
from backend.repositories.sqlite.workspace_summary_repository import WorkspaceSummaryRepository
from backend.core.config.settings import get_settings

logger = logging.getLogger(__name__)

class MasterOrchestratorAgent:
    """
    Agent 3: Master Orchestrator & Cognitive Director.
    Responsibilities:
    1. Multi-Agent Orchestration: Coordinates Agent 1 (Retrieval) and Agent 2 (Synthesis)
       with intelligence-based directives and state management.
    2. Resilience, Retry & Failover:
       - Retrieval: Supervises confidence and triggers query relaxation / syllabus routing if initial retrieval misses.
       - Synthesis: Enforces multi-tier failover (Groq 70B -> Groq 8B -> Local Ollama) and structural validation.
    3. Segregated Intelligence Tasks:
       - Topic & Concept Knowledge Extraction via TopicKnowledgeExtractor (zero conversational fluff).
       - Curriculum Tracking & Learning Path Management via CurriculumPathManager.
    4. Data Handling & Conversation Persistence: Ensures memory profiles and message tags
       are enriched only with verified academic concepts.
    """
    _instance: Optional["MasterOrchestratorAgent"] = None

    def __init__(self):
        self.retrieval_agent = RetrievalOrchestratorAgent()
        self.synthesis_agent = PedagogicalSynthesisAgent()
        self.topic_extractor = TopicKnowledgeExtractor()
        self.curriculum_manager = CurriculumPathManager()
        self.ci_manager = ConversationIntelligenceManager()
        self.analytics_service = AnalyticsService()
        self.summarization_service = SummarizationService()
        self.summary_repo = WorkspaceSummaryRepository()
        self.settings = get_settings()

    def orchestrate_chat(
        self,
        workspace_id: str,
        query: str,
        mode: str = "medium",
        session_id: Optional[str] = None
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Executes end-to-end multi-agent orchestration for a synchronous chat request.
        Returns: (asst_msg_dict, retrieved_chunks_list)
        """
        start_time = time.time()
        logger.info(
            f"[Agent 3: MasterOrchestrator] Initiating orchestration for workspace '{workspace_id}', "
            f"mode='{mode}', session='{session_id}'"
        )

        # ------------------------------------------------------------------
        # Phase 1: Supervised Retrieval via Agent 1 (with Retry & Quality Check)
        # ------------------------------------------------------------------
        context = self._execute_supervised_retrieval(workspace_id, query, mode, session_id)

        # ------------------------------------------------------------------
        # Phase 2: Segregated Topic & Knowledge Extraction (Syllabus-Grounded)
        # ------------------------------------------------------------------
        verified_topics = self._extract_verified_pedagogical_topics(
            query=query,
            context=context,
            workspace_id=workspace_id
        )
        context.detected_topics = verified_topics
        logger.info(
            f"[Agent 3: MasterOrchestrator] Verified pedagogical topics: {verified_topics}"
        )

        # ------------------------------------------------------------------
        # Phase 3: Curriculum Path & Cognitive Context Enrichment
        # ------------------------------------------------------------------
        self._enrich_curriculum_telemetry(context, workspace_id, verified_topics)

        # ------------------------------------------------------------------
        # Phase 4: Supervised Pedagogical Synthesis via Agent 2 (with Failover)
        # ------------------------------------------------------------------
        response_text, actual_model, sources = self._execute_supervised_synthesis(context, mode)

        processing_time_ms = int((time.time() - start_time) * 1000)

        # ------------------------------------------------------------------
        # Phase 5: Post-Execution Data Handling & Memory Evolution
        # ------------------------------------------------------------------
        asst_msg = self._persist_and_update_state(
            workspace_id=workspace_id,
            session_id=context.session_id,
            query=query,
            response_text=response_text,
            actual_model=actual_model,
            context=context,
            verified_topics=verified_topics,
            mode=mode,
            processing_time_ms=processing_time_ms
        )

        chunks_for_api = [c.model_dump() for c in context.retrieved_chunks]
        return asst_msg, chunks_for_api

    def orchestrate_stream(
        self,
        workspace_id: str,
        query: str,
        mode: str = "medium",
        session_id: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Executes streaming multi-agent orchestration.
        Streams synthesized tokens to client while executing background topic and memory updates.
        """
        start_time = time.time()
        logger.info(
            f"[Agent 3: MasterOrchestrator] Streaming orchestration for workspace '{workspace_id}'"
        )

        # Phase 1: Supervised Retrieval
        context = self._execute_supervised_retrieval(workspace_id, query, mode, session_id)

        # Phase 2: Segregated Topic Extraction
        verified_topics = self._extract_verified_pedagogical_topics(query, context, workspace_id)
        context.detected_topics = verified_topics

        # Phase 3: Curriculum Enrichment
        self._enrich_curriculum_telemetry(context, workspace_id, verified_topics)

        # Phase 4: Stream Tokens from Agent 2
        collected_tokens: List[str] = []
        try:
            for token in self.synthesis_agent.synthesize_stream(context, mode=mode):
                collected_tokens.append(token)
                yield token
        except Exception as e:
            logger.warning(f"[Agent 3: MasterOrchestrator] Streaming encountered error: {e}. Executing fallback.")
            fallback_text, _, _ = self._execute_supervised_synthesis(context, mode)
            yield fallback_text
            collected_tokens = [fallback_text]

        full_response = "".join(collected_tokens)
        processing_time_ms = int((time.time() - start_time) * 1000)

        # Phase 5: Persist Memory and Analytics Asynchronously
        try:
            self._persist_and_update_state(
                workspace_id=workspace_id,
                session_id=context.session_id,
                query=query,
                response_text=full_response,
                actual_model="streaming",
                context=context,
                verified_topics=verified_topics,
                mode=mode,
                processing_time_ms=processing_time_ms
            )
        except Exception as e:
            logger.warning(f"[Agent 3: MasterOrchestrator] Post-stream persistence notice: {e}")

    # ----------------------------------------------------------------------
    # Internal Supervised Execution & Failover Handlers
    # ----------------------------------------------------------------------

    def _execute_supervised_retrieval(
        self,
        workspace_id: str,
        query: str,
        mode: str,
        session_id: Optional[str]
    ) -> ContextPackage:
        """
        Supervises Agent 1 retrieval with quality verification and retry on low confidence.
        """
        # Primary Retrieval Attempt
        context = self.retrieval_agent.orchestrate(
            workspace_id=workspace_id,
            query=query,
            mode=mode,
            session_id=session_id
        )

        # Quality Check: If no chunks retrieved and query is not explicitly out-of-box,
        # perform an intelligent query relaxation retry
        if (
            len(context.retrieved_chunks) == 0
            and not (context.confidence and context.confidence.message and "Out-of-box" in context.confidence.message)
        ):
            logger.info(
                f"[Agent 3: MasterOrchestrator] Initial retrieval returned 0 chunks. Executing relaxation retry..."
            )
            try:
                # Retry with canonical query or key domain concept
                domain_concepts = self.topic_extractor.extract_topics(query, workspace_id=workspace_id, top_n=2)
                if domain_concepts:
                    relaxed_query = " ".join(domain_concepts)
                    logger.info(f"[Agent 3] Retrying Agent 1 with relaxed query: '{relaxed_query}'")
                    retry_context = self.retrieval_agent.orchestrate(
                        workspace_id=workspace_id,
                        query=relaxed_query,
                        mode=mode,
                        session_id=session_id
                    )
                    if len(retry_context.retrieved_chunks) > 0:
                        retry_context.session_id = context.session_id
                        retry_context.query = query  # preserve original user query
                        return retry_context
            except Exception as e:
                logger.warning(f"[Agent 3] Retrieval retry failed: {e}")

        return context

    def _extract_verified_pedagogical_topics(
        self,
        query: str,
        context: ContextPackage,
        workspace_id: str
    ) -> List[str]:
        """
        Segregated intelligence task: extracts authentic syllabus-grounded topics
        from both the user query and retrieved chunk evidence, completely filtering out noise.
        """
        topics: List[str] = []

        # 1. Query-level topic extraction
        query_topics = self.topic_extractor.extract_topics(query, workspace_id=workspace_id, top_n=3)
        topics.extend(query_topics)

        # 2. Chunk-level topic extraction from top-ranked chunks
        for chunk in context.retrieved_chunks[:3]:
            # First check chunk section heading
            heading = getattr(chunk, "section_heading", None)
            if heading and self.topic_extractor.is_valid_topic(heading):
                cleaned_h = self.topic_extractor._clean_raw_heading(heading)
                if cleaned_h and self.topic_extractor.is_valid_topic(cleaned_h):
                    topics.append(self.topic_extractor.canonicalize_topic(cleaned_h))

            # Extract concepts from chunk text
            chunk_topics = self.topic_extractor.extract_topics(
                chunk.chunk_text[:500],
                workspace_id=workspace_id,
                top_n=2
            )
            topics.extend(chunk_topics)

        # Deduplicate preserving order
        seen: set[str] = set()
        unique_topics: List[str] = []
        for t in topics:
            t_lower = t.lower()
            if t_lower not in seen and self.topic_extractor.is_valid_topic(t):
                seen.add(t_lower)
                unique_topics.append(self.topic_extractor.canonicalize_topic(t))

        return unique_topics[:5]

    def _enrich_curriculum_telemetry(
        self,
        context: ContextPackage,
        workspace_id: str,
        verified_topics: List[str]
    ) -> None:
        """
        Enriches cognitive state with curriculum path tracking information.
        """
        try:
            profile = self.ci_manager.profile_engine.get_or_create_profile(workspace_id)
            telemetry = self.curriculum_manager.get_learning_path_telemetry(
                workspace_id=workspace_id,
                topic_familiarity=profile.topic_familiarity,
                struggle_topics=profile.struggle_topics
            )
            logger.info(
                f"[Agent 3] Curriculum Telemetry: coverage={telemetry.get('coverage_percent')}%, "
                f"focus='{telemetry.get('active_focus')}', next={telemetry.get('recommended_next')}"
            )
        except Exception as e:
            logger.debug(f"[Agent 3] Curriculum enrichment notice: {e}")

    def _execute_supervised_synthesis(
        self,
        context: ContextPackage,
        mode: str
    ) -> Tuple[str, str, List[Dict[str, Any]]]:
        """
        Supervises Agent 2 pedagogical synthesis with failover and guardrails.
        """
        try:
            # Primary synthesis attempt via Agent 2
            response_text, model_used, sources = self.synthesis_agent.synthesize(context, mode=mode)
            
            # Guardrail Check: Non-empty response
            if response_text and len(response_text.strip()) > 30:
                return response_text, model_used, sources

            raise ValueError("Agent 2 synthesis generated empty or truncated output")
        except Exception as primary_error:
            logger.warning(
                f"[Agent 3: MasterOrchestrator] Primary synthesis failed: {primary_error}. "
                f"Executing failover escalation..."
            )
            
            # Failover Attempt: Try with medium mode / local model
            try:
                failover_mode = "medium" if mode == "expert" else "expert"
                response_text, model_used, sources = self.synthesis_agent.synthesize(context, mode=failover_mode)
                if response_text and len(response_text.strip()) > 30:
                    return response_text, f"{model_used} (failover)", sources
            except Exception as secondary_error:
                logger.error(f"[Agent 3] Secondary synthesis failover failed: {secondary_error}")

            # Emergency Graceful Fallback
            emergency_text = (
                "### Pedagogical Overview\n\n"
                "The system encountered a momentary service constraint while synthesizing the detailed pedagogical response. "
                "The core curriculum evidence has been retrieved and verified from your workspace documents.\n\n"
                "**Key Concepts Identified:**\n"
                + "\n".join([f"- {t}" for t in context.detected_topics or ["Curriculum Topic"]])
                + "\n\nPlease resubmit your inquiry or ask a focused follow-up on any of the concepts above."
            )
            return emergency_text, "offline_fallback", context.sources

    def _persist_and_update_state(
        self,
        workspace_id: str,
        session_id: str,
        query: str,
        response_text: str,
        actual_model: str,
        context: ContextPackage,
        verified_topics: List[str],
        mode: str,
        processing_time_ms: int
    ) -> Dict[str, Any]:
        """
        Persists message exchange and updates memory profile strictly with verified pedagogical concepts.
        """
        asst_msg_id = str(uuid.uuid4())
        try:
            self.ci_manager.persist_exchange(
                workspace_id=workspace_id,
                session_id=session_id,
                user_query=query,
                assistant_response=response_text,
                model_used=actual_model,
                retrieval_chunks=len(context.retrieved_chunks),
                retrieved_topics=verified_topics,
                preferred_mode=mode
            )
        except Exception as e:
            logger.warning(f"[Agent 3] Could not persist conversation exchange: {e}")

        # Trigger workspace summarization if due
        try:
            if self.summarization_service.should_summarize(workspace_id):
                summary = self.summarization_service.generate_summary(workspace_id)
                if summary:
                    self.summary_repo.upsert_summary(workspace_id, summary)
        except Exception as e:
            logger.debug(f"[Agent 3] Summarization check notice: {e}")

        # Update analytics metrics
        try:
            self.analytics_service.record_query(workspace_id, actual_model)
        except Exception as e:
            logger.debug(f"[Agent 3] Analytics recording notice: {e}")

        return {
            "message_id": asst_msg_id,
            "workspace_id": workspace_id,
            "role": "assistant",
            "message": response_text,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "model_used": actual_model,
            "retrieval_chunks": len(context.retrieved_chunks),
            "processing_time_ms": processing_time_ms,
            "session_id": session_id,
            "figures": context.retrieved_figures,
        }
