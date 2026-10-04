"""Session API schemas — Pydantic request/response models."""
from pydantic import BaseModel, Field
from typing import List


class CreateSessionRequest(BaseModel):
    session_name: str = Field(default="New Conversation", max_length=100)


class RenameSessionRequest(BaseModel):
    session_name: str = Field(..., min_length=1, max_length=100)


class SessionResponse(BaseModel):
    session_id: str
    workspace_id: str
    session_name: str
    created_at: str
    updated_at: str
    message_count: int
    is_active: bool


class SessionListResponse(BaseModel):
    sessions: List[SessionResponse]
    count: int
