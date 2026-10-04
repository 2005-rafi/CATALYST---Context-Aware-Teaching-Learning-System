"""Chat orchestration and message retrieval API endpoints."""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query
from backend.schemas.chat import (
    ChatRequest,
    ChatResponse,
    SourceChunk,
    FigureReference,
)
from backend.services.llm.chat_service import ChatService
from backend.repositories.sqlite.conversation_repository import ConversationRepository
from backend.core.dependencies import get_chat_service, get_conversation_repository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
def chat_endpoint(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
):
    """Submit a query to the multi-agent RAG pipeline. Returns the synthesis and citations."""
    asst_msg, context_chunks = service.chat(
        workspace_id=request.workspace_id,
        query=request.query,
        model_type=request.model,
        session_id=request.session_id
    )

    sources = [
        SourceChunk(
            chunk_id=c["chunk_id"],
            document_id=c["document_id"],
            text=c["chunk_text"],
            source_file=c.get("source_file", ""),
            score=c["score"]
        )
        for c in context_chunks
    ]

    # Visual RAG: attach retrieved figure references to response
    figures = [
        FigureReference(**fig_data)
        for fig_data in asst_msg.get("figures", [])
    ]

    return ChatResponse(
        message_id=asst_msg["message_id"],
        response=asst_msg["message"],
        sources=sources,
        model_used=asst_msg.get("model_used") or "unknown",
        session_id=asst_msg.get("session_id", ""),
        figures=figures,
    )


@router.get("/history/{workspace_id}")
def get_chat_history(
    workspace_id: str,
    session_id: Optional[str] = Query(default=None, description="Filter history by session ID"),
    repo: ConversationRepository = Depends(get_conversation_repository),
):
    """
    Retrieve conversation history for a workspace.
    Optionally filter by session_id to get session-scoped history.
    """
    if session_id:
        return repo.get_all_messages_for_session(workspace_id, session_id)
    return repo.get_all_messages(workspace_id)
