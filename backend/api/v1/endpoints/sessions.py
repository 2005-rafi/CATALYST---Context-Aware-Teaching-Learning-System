"""Conversation session API endpoints."""
from fastapi import APIRouter, HTTPException, status
from backend.schemas.sessions import (
    CreateSessionRequest,
    RenameSessionRequest,
    SessionResponse,
    SessionListResponse,
)
from backend.services.memory.session_manager import SessionManager
from backend.repositories.sqlite.conversation_repository import ConversationRepository

router = APIRouter(prefix="/session", tags=["Session"])

_sm = SessionManager()
_conv_repo = ConversationRepository()


def _to_response(row: dict) -> SessionResponse:
    return SessionResponse(
        session_id=row["session_id"],
        workspace_id=row["workspace_id"],
        session_name=row["session_name"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        message_count=row.get("message_count", 0),
        is_active=bool(row.get("is_active", 0))
    )


@router.get("/workspace/{workspace_id}", response_model=SessionListResponse)
def list_sessions(workspace_id: str):
    """List all conversation sessions for a workspace, most recent first."""
    sessions = _sm.list_sessions(workspace_id)
    return SessionListResponse(
        sessions=[_to_response(s) for s in sessions],
        count=len(sessions)
    )


@router.post("/workspace/{workspace_id}", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(workspace_id: str, body: CreateSessionRequest = CreateSessionRequest()):
    """Create a new named conversation session for a workspace."""
    session = _sm.create_session(workspace_id, body.session_name)
    if not session:
        raise HTTPException(status_code=500, detail="Failed to create session.")
    return _to_response(session)


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str):
    """Get details for a single session."""
    session = _sm.repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return _to_response(session)


@router.patch("/{session_id}", response_model=SessionResponse)
def rename_session(session_id: str, body: RenameSessionRequest):
    """Rename a conversation session."""
    session = _sm.rename_session(session_id, body.session_name)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return _to_response(session)


@router.post("/{session_id}/activate", response_model=SessionResponse)
def activate_session(session_id: str, workspace_id: str):
    """Set a session as active (deactivates all other sessions in the workspace)."""
    session = _sm.activate_session(session_id, workspace_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return _to_response(session)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: str):
    """Delete a session and all its messages."""
    try:
        _conv_repo.delete_session_messages(session_id)
    except Exception:
        pass
    deleted = _sm.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found.")
