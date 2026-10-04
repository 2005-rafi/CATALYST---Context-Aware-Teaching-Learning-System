"""
MemoryProfileEngine — tracks and evolves user behavioural memory per workspace.

SOLID:
  - S: Only responsible for profile tracking. No session management, no token counting.
  - O: Topic extraction and struggle detection are private strategies — swappable.

CIA:
  - Integrity: all DB writes via MemoryProfileRepository (parameterised queries).
  - Availability: all public methods have try/except with graceful fallback.
"""
import json
import logging
import re

from backend.models.conversation_session import UserMemoryProfile
from backend.repositories.sqlite.memory_profile_repository import MemoryProfileRepository
from backend.services.nlp.topic_knowledge_extractor import TopicKnowledgeExtractor

logger = logging.getLogger(__name__)

# Keywords that signal the user is struggling with a topic
_STRUGGLE_PATTERNS = re.compile(
    r"\b(don'?t understand|confused|unclear|explain again|what do you mean"
    r"|can you repeat|i don'?t get|not clear|help me understand|re-?explain)\b",
    re.IGNORECASE
)


class MemoryProfileEngine:

    def __init__(self):
        self.repo = MemoryProfileRepository()
        self.topic_extractor = TopicKnowledgeExtractor()

    def get_or_create_profile(self, workspace_id: str) -> UserMemoryProfile:
        """Return the existing profile, or initialise a fresh default one."""
        try:
            row = self.repo.get_profile(workspace_id)
            if row:
                return self._row_to_model(row)
            # Initialise with defaults
            self.repo.upsert_profile(workspace_id)
            row = self.repo.get_profile(workspace_id)
            return self._row_to_model(row)
        except Exception as e:
            logger.warning(f"MemoryProfileEngine: could not load profile for {workspace_id}: {e}")
            return UserMemoryProfile(workspace_id=workspace_id)

    def get_profile_context_snippet(self, workspace_id: str) -> str:
        """
        Returns a compact, ~150-token profile summary for LLM prompt injection.
        Returns empty string on any error — graceful degradation (CIA: Availability).
        """
        try:
            profile = self.get_or_create_profile(workspace_id)
            if profile.session_count == 0:
                return ""  # No history yet — nothing meaningful to inject
            return profile.build_context_snippet()
        except Exception as e:
            logger.warning(f"MemoryProfileEngine: could not build snippet for {workspace_id}: {e}")
            return ""

    def update_profile_from_exchange(
        self,
        workspace_id: str,
        user_query: str,
        assistant_response: str,
        retrieved_topics: list[str],
        preferred_mode: str = "medium"
    ) -> None:
        """
        Update the user's profile based on a completed Q&A exchange.
        Called after every successful assistant response.
        """
        try:
            existing = self.get_or_create_profile(workspace_id)

            # Detect struggle signals
            is_struggling = self._detect_struggle_signals(user_query)

            # Update topic familiarity strictly with validated domain topics
            tf = dict(existing.topic_familiarity)
            valid_new_topics = []
            for topic in retrieved_topics:
                if not self.topic_extractor.is_valid_topic(topic):
                    continue
                canonical = self.topic_extractor.canonicalize_topic(topic)
                valid_new_topics.append(canonical)
                # Successful retrieval → increase familiarity gradually
                current = tf.get(canonical, 0.3)
                tf[canonical] = min(1.0, current + 0.05)

            # Add struggle topics
            struggles = list(existing.struggle_topics)
            if is_struggling and valid_new_topics:
                for topic in valid_new_topics:
                    if topic not in struggles and self.topic_extractor.is_valid_topic(topic):
                        struggles.append(topic)
                struggles = struggles[-10:]  # cap at 10 to avoid noise

            self.repo.upsert_profile(
                workspace_id=workspace_id,
                preferred_mode=preferred_mode,
                topic_familiarity=tf,
                learning_style=existing.learning_style,
                struggle_topics=struggles,
                session_count=existing.session_count + 1
            )
        except Exception as e:
            logger.warning(
                f"MemoryProfileEngine: profile update failed for {workspace_id}: {e}"
            )
            # Do NOT raise — profile update failure must not block the chat response

    def reset_profile(self, workspace_id: str) -> None:
        """Reset all learned profile data for a workspace."""
        try:
            self.repo.delete_profile(workspace_id)
        except Exception as e:
            logger.error(f"MemoryProfileEngine: failed to reset profile for {workspace_id}: {e}")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _detect_struggle_signals(self, query: str) -> bool:
        """Returns True if the query contains explicit confusion/re-ask signals."""
        return bool(_STRUGGLE_PATTERNS.search(query))

    def extract_topics_from_text(self, text: str, top_n: int = 5) -> list[str]:
        """
        Extracts verified syllabus/pedagogical topics using TopicKnowledgeExtractor.
        Eliminates conversational fluff and naive capitalized token matching.
        """
        return self.topic_extractor.extract_topics(text, top_n=top_n)

    def _row_to_model(self, row: dict) -> UserMemoryProfile:
        return UserMemoryProfile(
            workspace_id=row["workspace_id"],
            preferred_mode=row.get("preferred_mode", "medium"),
            topic_familiarity=row.get("topic_familiarity", "{}"),
            learning_style=row.get("learning_style", "balanced"),
            struggle_topics=row.get("struggle_topics", "[]"),
            session_count=row.get("session_count", 0),
            last_active=row.get("last_active", "")
        )
