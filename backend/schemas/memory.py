"""Memory Profile API schemas — Pydantic request/response models."""
from pydantic import BaseModel
from typing import Dict, List, Any


class ProfileResponse(BaseModel):
    workspace_id: str
    preferred_mode: str
    topic_familiarity: Dict[str, Any]
    learning_style: str
    struggle_topics: List[str]
    session_count: int
    last_active: str
    profile_snippet: str
