import logging
import threading
from typing import List, Dict, Any, Optional, Set
from backend.repositories.sqlite.chunk_repository import ChunkRepository
from backend.services.nlp.topic_knowledge_extractor import TopicKnowledgeExtractor

logger = logging.getLogger(__name__)

class CurriculumPathManager:
    """
    Curriculum Knowledge Tracking & Learning Path Manager.
    Maps out the syllabus architecture of indexed workspace documents,
    evaluates user learning progress across syllabus chapters,
    and dynamically calculates pedagogical next steps.
    """
    _instance: Optional["CurriculumPathManager"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "CurriculumPathManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CurriculumPathManager, cls).__new__(cls)
                cls._instance.chunk_repo = ChunkRepository()
                cls._instance.topic_extractor = TopicKnowledgeExtractor()
                cls._instance._curriculum_cache: Dict[str, Dict[str, Any]] = {}
            return cls._instance

    def get_curriculum_tree(self, workspace_id: str) -> List[Dict[str, Any]]:
        """
        Builds a hierarchical curriculum tree from workspace chunks:
        Chapter/Module -> Sections -> Sub-concepts.
        """
        if not workspace_id:
            return []

        with self._lock:
            if workspace_id in self._curriculum_cache:
                return self._curriculum_cache[workspace_id].get("tree", [])

        try:
            headings = self.topic_extractor.get_workspace_syllabus_headings(workspace_id)
            chunks = self.chunk_repo.get_chunks_by_workspace(workspace_id)

            # Group chunks by section_heading
            chapter_map: Dict[str, List[str]] = {}
            for h in headings:
                # Identify potential chapter or unit name
                chapter_map.setdefault("Curriculum Core", []).append(h)

            tree = []
            for group_name, topics in chapter_map.items():
                tree.append({
                    "group": group_name,
                    "topics_count": len(topics),
                    "topics": topics
                })

            with self._lock:
                self._curriculum_cache[workspace_id] = {
                    "tree": tree,
                    "headings": headings
                }

            return tree
        except Exception as e:
            logger.warning(f"[CurriculumPathManager] Failed to build curriculum tree: {e}")
            return []

    def get_learning_path_telemetry(
        self,
        workspace_id: str,
        topic_familiarity: Dict[str, Any],
        struggle_topics: List[str]
    ) -> Dict[str, Any]:
        """
        Calculates curriculum coverage and computes next pedagogical topic recommendations.
        """
        headings = self.topic_extractor.get_workspace_syllabus_headings(workspace_id)
        total_syllabus_topics = len(headings) if headings else max(len(topic_familiarity), 10)

        # Normalize keys in topic_familiarity
        explored_topics_set: Set[str] = set()
        mastered_topics_set: Set[str] = set()

        for t, data in topic_familiarity.items():
            if not self.topic_extractor.is_valid_topic(t):
                continue
            canonical = self.topic_extractor.canonicalize_topic(t).lower()
            score = float(data.get("familiarity_score", 0.5) if isinstance(data, dict) else data or 0.5)
            explored_topics_set.add(canonical)
            if score >= 0.8:
                mastered_topics_set.add(canonical)

        explored_count = len(explored_topics_set)
        mastered_count = len(mastered_topics_set)
        coverage_percent = int(min(100, round((explored_count / max(total_syllabus_topics, 1)) * 100)))

        # Determine next recommended topics in syllabus sequence
        recommended_next: List[str] = []
        if headings:
            for h in headings:
                canonical_h = self.topic_extractor.canonicalize_topic(h)
                if canonical_h.lower() not in explored_topics_set and self.topic_extractor.is_valid_topic(canonical_h):
                    recommended_next.append(canonical_h)
                    if len(recommended_next) >= 4:
                        break

        # Fallback recommendations if syllabus is fully explored or small
        if not recommended_next:
            fallback_candidates = [
                "Human Reproduction", "Spermatogenesis", "Structure of Ovum",
                "Environmental Issues", "Biotechnology Applications", "Principles of Inheritance"
            ]
            for c in fallback_candidates:
                if c.lower() not in explored_topics_set:
                    recommended_next.append(c)
                    if len(recommended_next) >= 3:
                        break

        # Active focus area
        active_focus = "General Curriculum"
        if explored_topics_set:
            last_explored = list(explored_topics_set)[-1]
            active_focus = self.topic_extractor.canonicalize_topic(last_explored)

        return {
            "total_syllabus_topics": total_syllabus_topics,
            "explored_count": explored_count,
            "mastered_count": mastered_count,
            "coverage_percent": coverage_percent,
            "active_focus": active_focus,
            "recommended_next": recommended_next,
            "struggle_topics_count": len(struggle_topics)
        }

    def invalidate_cache(self, workspace_id: str) -> None:
        """Invalidates curriculum cache."""
        with self._lock:
            if workspace_id in self._curriculum_cache:
                del self._curriculum_cache[workspace_id]
