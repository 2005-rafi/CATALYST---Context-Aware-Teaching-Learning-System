from backend.repositories.sqlite.base_repository import BaseRepository
from datetime import datetime, timezone, timedelta
import json
import logging

logger = logging.getLogger(__name__)

class AnalyticsRepository(BaseRepository):
    def init_analytics(self, workspace_id: str) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        self._execute(
            "INSERT INTO analytics (analytics_id, workspace_id, last_updated) VALUES (?, ?, ?)",
            (workspace_id, workspace_id, now) # Using workspace_id as analytics_id since it's 1:1
        )
        return self.get_analytics(workspace_id)

    def get_analytics(self, workspace_id: str) -> dict | None:
        return self._execute(
            "SELECT * FROM analytics WHERE workspace_id = ?",
            (workspace_id,),
            fetch_one=True
        )

    def increment_query_count(self, workspace_id: str):
        now = datetime.now(timezone.utc).isoformat()
        self._execute(
            "UPDATE analytics SET total_queries = total_queries + 1, last_updated = ? WHERE workspace_id = ?",
            (now, workspace_id)
        )

    def increment_groq_requests(self, workspace_id: str):
        now = datetime.now(timezone.utc).isoformat()
        self._execute(
            "UPDATE analytics SET groq_requests = groq_requests + 1, last_updated = ? WHERE workspace_id = ?",
            (now, workspace_id)
        )

    def increment_local_requests(self, workspace_id: str):
        now = datetime.now(timezone.utc).isoformat()
        self._execute(
            "UPDATE analytics SET local_model_requests = local_model_requests + 1, last_updated = ? WHERE workspace_id = ?",
            (now, workspace_id)
        )

    def update_storage_stats(self, workspace_id: str, total_documents: int, total_chunks: int, total_storage_mb: float):
        now = datetime.now(timezone.utc).isoformat()
        self._execute(
            "UPDATE analytics SET total_documents = ?, total_chunks = ?, total_storage_mb = ?, last_updated = ? WHERE workspace_id = ?",
            (total_documents, total_chunks, total_storage_mb, now, workspace_id)
        )

    def get_daily_activity(self, workspace_id: str, days: int = 14) -> list[dict]:
        """
        Aggregates daily conversation and query count for the last N days.
        Guarantees contiguous date entries even if some days had 0 activity.
        """
        now = datetime.now(timezone.utc)
        date_map = {}
        for i in range(days - 1, -1, -1):
            dt = now - timedelta(days=i)
            d_str = dt.strftime("%Y-%m-%d")
            d_label = dt.strftime("%b %d")
            date_map[d_str] = {
                "date": d_str,
                "label": d_label,
                "query_count": 0,
                "message_count": 0,
            }

        cutoff_date = (now - timedelta(days=days)).strftime("%Y-%m-%d")
        
        rows = self._execute(
            """
            SELECT 
                substr(created_at, 1, 10) as day_str,
                SUM(CASE WHEN role = 'user' THEN 1 ELSE 0 END) as user_queries,
                COUNT(*) as total_msgs
            FROM conversations
            WHERE workspace_id = ? AND substr(created_at, 1, 10) >= ?
            GROUP BY substr(created_at, 1, 10)
            ORDER BY substr(created_at, 1, 10) ASC
            """,
            (workspace_id, cutoff_date),
            fetch_all=True
        ) or []

        for row in rows:
            day_str = row.get("day_str")
            if day_str in date_map:
                date_map[day_str]["query_count"] = int(row.get("user_queries") or 0)
                date_map[day_str]["message_count"] = int(row.get("total_msgs") or 0)

        return list(date_map.values())

    def get_deep_telemetry(self, workspace_id: str) -> dict:
        """
        Aggregates session totals, retrieval stats, cognitive memory profile,
        documents list with figures, and figure categorization.
        """
        # 1. Total sessions and total messages
        sessions_row = self._execute(
            "SELECT COUNT(*) as total_sessions FROM conversation_sessions WHERE workspace_id = ?",
            (workspace_id,),
            fetch_one=True
        )
        total_sessions = int(sessions_row.get("total_sessions") or 0) if sessions_row else 0

        msgs_row = self._execute(
            """
            SELECT 
                COUNT(*) as total_msgs,
                AVG(CASE WHEN role = 'assistant' AND retrieval_chunks > 0 THEN retrieval_chunks ELSE NULL END) as avg_chunks
            FROM conversations 
            WHERE workspace_id = ?
            """,
            (workspace_id,),
            fetch_one=True
        )
        total_messages = int(msgs_row.get("total_msgs") or 0) if msgs_row else 0
        avg_chunks = float(msgs_row.get("avg_chunks") or 0.0) if msgs_row else 0.0

        # 2. Cognitive Memory Profile
        profile_row = self._execute(
            "SELECT * FROM user_memory_profiles WHERE workspace_id = ?",
            (workspace_id,),
            fetch_one=True
        )
        
        topic_mastery = []
        struggle_topics = []
        learning_style = "balanced"
        preferred_mode = "medium"

        if profile_row:
            learning_style = profile_row.get("learning_style") or "balanced"
            preferred_mode = profile_row.get("preferred_mode") or "medium"
            
            # Parse topic familiarity JSON
            raw_fam = profile_row.get("topic_familiarity")
            if raw_fam:
                try:
                    fam_dict = json.loads(raw_fam) if isinstance(raw_fam, str) else raw_fam
                    if isinstance(fam_dict, dict):
                        from backend.services.nlp.topic_knowledge_extractor import TopicKnowledgeExtractor
                        extractor = TopicKnowledgeExtractor()
                        for topic, data in fam_dict.items():
                            if not extractor.is_valid_topic(topic):
                                continue
                            canonical_topic = extractor.canonicalize_topic(topic)
                            score = float(data.get("familiarity_score", 0.5) if isinstance(data, dict) else data or 0.5)
                            q_count = int(data.get("query_count", 1) if isinstance(data, dict) else 1)
                            is_struggling = bool(data.get("struggling", False) if isinstance(data, dict) else False)
                            
                            percent = int(min(max(score * 100, 5), 100))
                            level = "Mastered" if percent >= 80 else "Proficient" if percent >= 50 else "Beginner"
                            
                            topic_mastery.append({
                                "topic": canonical_topic,
                                "familiarity_score": round(score, 2),
                                "familiarity_percent": percent,
                                "level": level,
                                "query_count": q_count,
                                "is_struggling": is_struggling,
                            })
                except Exception as e:
                    logger.warning(f"Error parsing topic_familiarity: {e}")

            # Parse struggle topics JSON
            raw_struggle = profile_row.get("struggle_topics")
            if raw_struggle:
                try:
                    struggle_list = json.loads(raw_struggle) if isinstance(raw_struggle, str) else raw_struggle
                    if isinstance(struggle_list, list):
                        from backend.services.nlp.topic_knowledge_extractor import TopicKnowledgeExtractor
                        extractor = TopicKnowledgeExtractor()
                        struggle_topics = [extractor.canonicalize_topic(s) for s in struggle_list if extractor.is_valid_topic(s)]
                    else:
                        struggle_topics = []
                except Exception:
                    struggle_topics = []

        # Sort topics by query count and familiarity
        topic_mastery.sort(key=lambda x: (x["query_count"], x["familiarity_percent"]), reverse=True)

        # 3. Documents with Figures Count
        docs_rows = self._execute(
            """
            SELECT 
                d.document_id,
                d.file_name,
                d.file_type,
                d.file_size_mb,
                d.total_chunks,
                d.upload_time,
                d.processing_status,
                (SELECT COUNT(*) FROM figure_chunks f WHERE f.document_id = d.document_id) as figures_count
            FROM documents d
            WHERE d.workspace_id = ?
            ORDER BY d.upload_time DESC
            """,
            (workspace_id,),
            fetch_all=True
        ) or []

        documents = []
        for d in docs_rows:
            documents.append({
                "document_id": d.get("document_id"),
                "file_name": d.get("file_name"),
                "file_type": d.get("file_type") or "pdf",
                "file_size_mb": float(d.get("file_size_mb") or 0.0),
                "total_chunks": int(d.get("total_chunks") or 0),
                "figures_count": int(d.get("figures_count") or 0),
                "upload_time": d.get("upload_time") or "",
                "processing_status": d.get("processing_status") or "completed",
            })

        # 4. Figures Summary
        figures_rows = self._execute(
            """
            SELECT figure_type, caption_text
            FROM figure_chunks
            WHERE workspace_id = ?
            """,
            (workspace_id,),
            fetch_all=True
        ) or []

        by_type = {}
        sample_captions = []
        for f in figures_rows:
            f_type = (f.get("figure_type") or "diagram").capitalize()
            by_type[f_type] = by_type.get(f_type, 0) + 1
            caption = f.get("caption_text", "").strip()
            if caption and len(sample_captions) < 5:
                sample_captions.append(caption)

        figures_summary = {
            "total_figures": len(figures_rows),
            "by_type": by_type,
            "sample_captions": sample_captions,
        }

        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "avg_chunks_per_query": round(avg_chunks, 1),
            "learning_style": learning_style,
            "preferred_mode": preferred_mode,
            "topic_mastery": topic_mastery,
            "struggle_topics": struggle_topics,
            "documents": documents,
            "figures_summary": figures_summary,
        }
