"""User learning memory profile API endpoints."""
from fastapi import APIRouter, status
from backend.services.memory.memory_profile_engine import MemoryProfileEngine
from backend.schemas.memory import ProfileResponse

router = APIRouter(prefix="/memory", tags=["Memory"])

_engine = MemoryProfileEngine()


@router.get("/workspace/{workspace_id}/profile", response_model=ProfileResponse)
def get_profile(workspace_id: str):
    """Get the current user learning profile for a workspace."""
    profile = _engine.get_or_create_profile(workspace_id)
    return ProfileResponse(
        workspace_id=profile.workspace_id,
        preferred_mode=profile.preferred_mode,
        topic_familiarity=profile.topic_familiarity,
        learning_style=profile.learning_style,
        struggle_topics=profile.struggle_topics,
        session_count=profile.session_count,
        last_active=profile.last_active,
        profile_snippet=profile.build_context_snippet()
    )


@router.delete(
    "/workspace/{workspace_id}/profile",
    status_code=status.HTTP_204_NO_CONTENT
)
def reset_profile(workspace_id: str):
    """Reset the user's learning profile for a workspace."""
    _engine.reset_profile(workspace_id)
