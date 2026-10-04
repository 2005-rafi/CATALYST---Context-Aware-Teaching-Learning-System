"""
ConversationIntelligenceManager — Facade for the CI subsystem.

GoF Facade Pattern: Provides a single, clean interface over the complexity of
SessionManager, MemoryProfileEngine, TokenBudgetManager, and ContextWindow.

CIA Triad:
  - Confidentiality: session IDs are UUID4. Profile data stays local.
  - Integrity: all sub-calls use parameterised DB writes.
  - Availability: every sub-call wrapped in try/except. Failures return
    graceful fallbacks — the chat response is NEVER blocked by CI failures.

SOLID:
  - S: Only assembles/persists memory. Retrieval & LLM are handled elsewhere.
  - D: Depends on SessionManager, MemoryProfileEngine, etc. (abstractions),
       not on concrete repository classes directly.
"""
import uuid
import json
import logging
import datetime

from backend.models.conversation_session import ConversationMemoryPackage
from backend.services.memory.session_manager import SessionManager
from backend.services.memory.memory_profile_engine import MemoryProfileEngine
from backend.services.memory.token_budget_manager import TokenBudgetManager
from backend.services.memory.context_window import ContextWindow
from backend.repositories.sqlite.conversation_repository import ConversationRepository
from backend.repositories.sqlite.workspace_summary_repository import WorkspaceSummaryRepository

logger = logging.getLogger(__name__)


class ConversationIntelligenceManager:

    def __init__(self):
        self.session_manager = SessionManager()
        self.profile_engine = MemoryProfileEngine()
        self.token_budget = TokenBudgetManager()
        self.context_window = ContextWindow()
        self.conversation_repo = ConversationRepository()
        self.summary_repo = WorkspaceSummaryRepository()

    # ------------------------------------------------------------------
    # Public: assemble memory for incoming query
    # ------------------------------------------------------------------

    def assemble_memory(
        self,
        workspace_id: str,
        mode: str = "medium",
        session_id: str | None = None
    ) -> ConversationMemoryPackage:
        """
        Single call to assemble the full, token-budgeted memory context for a query.
        All sub-steps degrade gracefully on error.
        """
        target_session_id = session_id or ""
        recent_messages: list[dict] = []
        profile_snippet = ""
        workspace_summary = ""

        if not target_session_id:
            try:
                session = self.session_manager.get_or_create_active_session(workspace_id)
                target_session_id = session.get("session_id", "")
            except Exception as e:
                logger.warning(f"CIM: session lookup failed for {workspace_id}: {e}")

        try:
            budget = self.token_budget.get_budget(mode)
            if target_session_id:
                raw_history = self.conversation_repo.get_recent_messages_for_session(
                    workspace_id, target_session_id, limit=20
                )
            else:
                raw_history = self.context_window.get_recent_context(workspace_id)

            recent_messages = self.token_budget.allocate_history(
                raw_history, budget["history"]
            )
        except Exception as e:
            logger.warning(f"CIM: history assembly failed for {workspace_id}: {e}")

        try:
            profile_snippet = self.profile_engine.get_profile_context_snippet(workspace_id)
        except Exception as e:
            logger.warning(f"CIM: profile snippet failed for {workspace_id}: {e}")

        try:
            summary_record = self.summary_repo.get_summary(workspace_id)
            workspace_summary = summary_record["summary_text"] if summary_record else ""
        except Exception as e:
            logger.warning(f"CIM: summary fetch failed for {workspace_id}: {e}")

        total_tokens = self.token_budget.estimate_total(
            profile_snippet, workspace_summary,
            *[m.get("message", "") for m in recent_messages]
        )

        logger.debug(
            f"CIM: assembled memory for {workspace_id} session={target_session_id!r} "
            f"history={len(recent_messages)} msgs, tokens~{total_tokens}"
        )

        return ConversationMemoryPackage(
            session_id=target_session_id,
            recent_messages=recent_messages,
            profile_snippet=profile_snippet,
            workspace_summary=workspace_summary,
            total_tokens_estimated=total_tokens,
        )

    def get_workspace_user_queries(self, workspace_id: str) -> list[dict]:
        """Fetch all user-submitted queries across all sessions in this workspace."""
        try:
            return self.conversation_repo.get_all_user_queries_for_workspace(workspace_id)
        except Exception as e:
            logger.warning(f"CIM: failed to get workspace user queries for {workspace_id}: {e}")
            return []

    def build_workspace_memory_bank(self, workspace_id: str) -> str:
        """
        Builds a compact (~250 tokens) cross-session episodic memory bank for the workspace.
        Consolidates:
        - Total sessions and past conversation topics
        - Deduplicated queries asked across all sessions
        - Mastered topics and active study areas
        """
        try:
            sessions = self.conversation_repo.get_workspace_session_digests(workspace_id)
            user_queries = self.conversation_repo.get_all_user_queries_for_workspace(workspace_id)
            profile = self.profile_engine.get_or_create_profile(workspace_id)

            if not sessions and not user_queries and not profile.topic_familiarity:
                return ""

            parts = []
            # 1. Past Sessions Overview
            active_sessions = [s for s in sessions if s.get("message_count", 0) > 0]
            if active_sessions:
                session_lines = []
                for s in active_sessions[:5]:
                    name = s.get("session_name", "General")
                    cnt = s.get("message_count", 0)
                    init_q = s.get("initial_query") or ""
                    if init_q and init_q.lower() != name.lower():
                        session_lines.append(f"- \"{name}\" ({cnt} msgs, focus: {init_q[:40]})")
                    else:
                        session_lines.append(f"- \"{name}\" ({cnt} msgs)")
                parts.append("Previous Workspace Conversations:\n" + "\n".join(session_lines))

            # 2. Deduplicated Inquiries
            if user_queries:
                query_counts: dict[str, int] = {}
                for q in user_queries:
                    text = q.get("message", "").strip()
                    if text:
                        query_counts[text] = query_counts.get(text, 0) + 1

                unique_q_list = []
                for q_text, count in list(query_counts.items())[:8]:
                    suffix = f" (asked {count}x)" if count > 1 else ""
                    unique_q_list.append(f"• \"{q_text}\"{suffix}")

                parts.append(f"Past Questions Asked in this Workspace ({len(user_queries)} total inquiries):\n" + "\n".join(unique_q_list))

            # 3. Topic Mastery from Profile
            if profile.topic_familiarity:
                mastered = [t for t, score in profile.topic_familiarity.items() if score >= 0.5]
                if mastered:
                    parts.append(f"Mastered Topics: {', '.join(mastered[:6])}")

            return "\n\n".join(parts)
        except Exception as e:
            logger.warning(f"CIM: failed to build workspace memory bank for {workspace_id}: {e}")
            return ""

    # ------------------------------------------------------------------
    # Public: persist exchange after assistant response
    # ------------------------------------------------------------------

    def persist_exchange(
        self,
        workspace_id: str,
        session_id: str,
        user_query: str,
        assistant_response: str,
        model_used: str | None,
        retrieval_chunks: int,
        retrieved_topics: list[str],
        preferred_mode: str = "medium"
    ) -> None:
        """
        Save user + assistant messages for the session and evolve the memory profile.
        Does NOT block — all failures are logged and swallowed.
        """
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        user_msg_id = str(uuid.uuid4())
        asst_msg_id = str(uuid.uuid4())
        tags_json_list = retrieved_topics  # stored via ConversationRepository as JSON

        # --- Save user message ---
        try:
            turn_index = self.conversation_repo.get_message_count(workspace_id)
            self.conversation_repo.save_message(
                message_id=user_msg_id,
                workspace_id=workspace_id,
                role="user",
                message=user_query,
                created_at=now,
                model_used=None,
                retrieval_chunks=0,
                session_id=session_id,
                turn_index=turn_index,
                topic_tags=retrieved_topics,
                importance_score=0.5
            )
        except Exception as e:
            logger.warning(f"CIM: failed to save user message for {workspace_id}: {e}")

        # --- Save assistant message ---
        asst_msg: dict = {}
        try:
            # Score importance: longer, citation-rich responses are more important
            citations = assistant_response.count("[")
            importance = min(1.0, 0.5 + citations * 0.05 + (len(assistant_response) > 500) * 0.1)
            turn_index2 = self.conversation_repo.get_message_count(workspace_id)
            asst_row = self.conversation_repo.save_message(
                message_id=asst_msg_id,
                workspace_id=workspace_id,
                role="assistant",
                message=assistant_response,
                created_at=now,
                model_used=model_used,
                retrieval_chunks=retrieval_chunks,
                session_id=session_id,
                turn_index=turn_index2,
                topic_tags=retrieved_topics,
                importance_score=importance
            )
            asst_msg = asst_row or {}
        except Exception as e:
            logger.warning(f"CIM: failed to save assistant message for {workspace_id}: {e}")

        # --- Increment session message count ---
        try:
            if session_id:
                self.session_manager.increment_message_count(session_id)
        except Exception as e:
            logger.warning(f"CIM: session count update failed for session {session_id}: {e}")

        # --- Auto-name session from first user query ---
        try:
            if session_id:
                session = self.session_manager.repo.get_session(session_id)
                if session and session.get("session_name") == "New Conversation" \
                        and session.get("message_count", 0) <= 2:
                    auto_name = user_query[:50].strip()
                    if len(user_query) > 50:
                        auto_name += "…"
                    self.session_manager.rename_session(session_id, auto_name)
        except Exception as e:
            logger.debug(f"CIM: session auto-naming skipped: {e}")

        # --- Update memory profile ---
        try:
            self.profile_engine.update_profile_from_exchange(
                workspace_id=workspace_id,
                user_query=user_query,
                assistant_response=assistant_response,
                retrieved_topics=retrieved_topics,
                preferred_mode=preferred_mode
            )
        except Exception as e:
            logger.warning(f"CIM: profile update failed for {workspace_id}: {e}")

    def get_saved_message_pair(
        self, workspace_id: str, user_msg_id: str, asst_msg_id: str,
        response_text: str, model_used: str | None,
        retrieval_chunks: int, processing_time_ms: int
    ) -> dict:
        """
        Build the assistant message dict for the API response layer.
        Called from ChatService after persist_exchange.
        """
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return {
            "message_id": asst_msg_id,
            "workspace_id": workspace_id,
            "role": "assistant",
            "message": response_text,
            "created_at": now,
            "model_used": model_used,
            "retrieval_chunks": retrieval_chunks,
            "processing_time_ms": processing_time_ms,
        }
