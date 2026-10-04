"""
MemoryProfileRepository — CRUD for user_memory_profiles table.
Stores per-workspace behavioural memory (topic familiarity, learning style, struggles).
All fields serialized via json.dumps / json.loads — no raw string injection.
"""
import uuid
import json
import datetime
from backend.repositories.sqlite.base_repository import BaseRepository


class MemoryProfileRepository(BaseRepository):

    def get_profile(self, workspace_id: str) -> dict | None:
        return self._execute(
            "SELECT * FROM user_memory_profiles WHERE workspace_id = ?",
            (workspace_id,),
            fetch_one=True
        )

    def upsert_profile(
        self,
        workspace_id: str,
        preferred_mode: str = "medium",
        topic_familiarity: dict | None = None,
        learning_style: str = "balanced",
        struggle_topics: list | None = None,
        session_count: int = 0
    ) -> dict:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        existing = self.get_profile(workspace_id)
        profile_id = existing["profile_id"] if existing else str(uuid.uuid4())

        tf_json = json.dumps(topic_familiarity or {})
        st_json = json.dumps(struggle_topics or [])

        self._execute(
            """
            INSERT OR REPLACE INTO user_memory_profiles
                (profile_id, workspace_id, preferred_mode, topic_familiarity,
                 learning_style, struggle_topics, session_count, last_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (profile_id, workspace_id, preferred_mode, tf_json,
             learning_style, st_json, session_count, now)
        )
        return self.get_profile(workspace_id)

    def delete_profile(self, workspace_id: str) -> int:
        return self._execute(
            "DELETE FROM user_memory_profiles WHERE workspace_id = ?",
            (workspace_id,)
        )
