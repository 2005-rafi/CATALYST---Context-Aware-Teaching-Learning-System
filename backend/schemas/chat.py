"""Chat API schemas — Pydantic request/response models."""
from pydantic import BaseModel, Field
from typing import List, Optional


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4096, description="User query, max 4096 characters")
    workspace_id: str = Field(..., min_length=1, max_length=64)
    model: str = Field(default="medium", pattern="^(simple|medium|expert)$")
    session_id: Optional[str] = Field(default=None, description="Optional conversation session ID")
    api_key: Optional[str] = Field(default=None, description="Optional BYOK API key for LLM provider")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0, description="Optional sampling temperature")
    system_prompt: Optional[str] = Field(default=None, max_length=4096, description="Optional system prompt override")


class SourceChunk(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    source_file: str = ""
    score: float


class FigureReference(BaseModel):
    """
    Minimal figure descriptor returned in chat responses.
    The frontend uses `url` to fetch the PNG and display it as a figure card.
    """
    figure_id: str
    caption: str = ""
    figure_type: str = "unknown"
    page_number: int = 0
    document_name: str = ""
    url: str = ""  # /api/v1/figures/{figure_id}?workspace_id={workspace_id}


class ChatResponse(BaseModel):
    message_id: str
    response: str
    sources: List[SourceChunk]
    model_used: str
    session_id: str = ""
    figures: List[FigureReference] = []   # Visual RAG: retrieved figure references

    model_config = {"protected_namespaces": ()}
