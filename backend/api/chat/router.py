from fastapi import APIRouter, HTTPException, status, Depends
from backend.schemas.chat_schemas import ChatRequest, ChatResponse, SourceChunk
from backend.services.llm.chat_service import ChatService
from backend.repositories.sqlite.conversation_repository import ConversationRepository
from backend.core.dependencies import get_chat_service, get_conversation_repository
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
def chat_endpoint(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
):
    """Submit a query to the RAG pipeline. Returns the LLM response and source chunks."""
    asst_msg, context_chunks = service.chat(
        workspace_id=request.workspace_id,
        query=request.query,
        model_type=request.model
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

    return ChatResponse(
        message_id=asst_msg["message_id"],
        response=asst_msg["message"],
        sources=sources,
        model_used=asst_msg["model_used"] or "unknown"
    )


@router.get("/history/{workspace_id}")
def get_chat_history(
    workspace_id: str,
    repo: ConversationRepository = Depends(get_conversation_repository),
):
    """Retrieve full conversation history for a workspace."""
    return repo.get_all_messages(workspace_id)

