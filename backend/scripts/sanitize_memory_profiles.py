import sqlite3
import json
import logging
from backend.core.config.settings import get_settings
from backend.services.nlp.topic_knowledge_extractor import TopicKnowledgeExtractor

logger = logging.getLogger(__name__)

def sanitize_database_memory_profiles(db_path: str = "") -> dict:
    """
    Cleanses corrupted legacy topic records from SQLite database:
    1. user_memory_profiles: topic_familiarity and struggle_topics
    2. conversations: topic_tags
    Removes conversational fluff, stop words, and sub-tokens.
    """
    settings = get_settings()
    path = db_path or settings.DATABASE_PATH
    extractor = TopicKnowledgeExtractor()

    conn = sqlite3.connect(path)
    c = conn.cursor()

    stats = {
        "profiles_cleaned": 0,
        "topics_removed": 0,
        "topics_retained": 0,
        "conversations_cleaned": 0
    }

    try:
        # 1. Cleanse user_memory_profiles
        c.execute("SELECT workspace_id, topic_familiarity, struggle_topics FROM user_memory_profiles")
        rows = c.fetchall()

        for workspace_id, raw_fam, raw_struggle in rows:
            fam_dict = {}
            if raw_fam:
                try:
                    fam_dict = json.loads(raw_fam) if isinstance(raw_fam, str) else raw_fam
                except Exception:
                    fam_dict = {}

            cleaned_fam = {}
            if isinstance(fam_dict, dict):
                for k, v in fam_dict.items():
                    if extractor.is_valid_topic(k):
                        canonical = extractor.canonicalize_topic(k)
                        cleaned_fam[canonical] = v
                        stats["topics_retained"] += 1
                    else:
                        stats["topics_removed"] += 1

            struggle_list = []
            if raw_struggle:
                try:
                    struggle_list = json.loads(raw_struggle) if isinstance(raw_struggle, str) else raw_struggle
                except Exception:
                    struggle_list = []

            cleaned_struggles = []
            if isinstance(struggle_list, list):
                for s in struggle_list:
                    if extractor.is_valid_topic(s):
                        cleaned_struggles.append(extractor.canonicalize_topic(s))

            # Update row in database
            c.execute(
                "UPDATE user_memory_profiles SET topic_familiarity = ?, struggle_topics = ? WHERE workspace_id = ?",
                (json.dumps(cleaned_fam), json.dumps(cleaned_struggles), workspace_id)
            )
            stats["profiles_cleaned"] += 1

        # 2. Cleanse conversations topic_tags
        c.execute("SELECT message_id, topic_tags FROM conversations WHERE topic_tags IS NOT NULL")
        msg_rows = c.fetchall()
        for msg_id, raw_tags in msg_rows:
            try:
                tags = json.loads(raw_tags) if isinstance(raw_tags, str) else raw_tags
                if isinstance(tags, list):
                    cleaned_tags = [extractor.canonicalize_topic(t) for t in tags if extractor.is_valid_topic(t)]
                    c.execute(
                        "UPDATE conversations SET topic_tags = ? WHERE message_id = ?",
                        (json.dumps(cleaned_tags), msg_id)
                    )
                    stats["conversations_cleaned"] += 1
            except Exception:
                pass

        conn.commit()
        logger.info(f"[DB Sanitization] Completed: {stats}")
    except Exception as e:
        logger.error(f"[DB Sanitization] Error cleaning database: {e}")
        conn.rollback()
    finally:
        conn.close()

    return stats

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    res = sanitize_database_memory_profiles()
    print("Database Sanitization Result:", res)
