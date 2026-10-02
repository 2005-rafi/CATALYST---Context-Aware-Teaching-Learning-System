from typing import List, Any
from pydantic import BaseModel, ConfigDict
from backend.models.chat import RetrievedChunk


class ContextPackage(BaseModel):
    """Immutable context bundle passed from ContextBuilder to PromptBuilder.

    P13 FIX: converted from dataclasses.dataclass to Pydantic BaseModel for
    consistency with RetrievedChunk and all other domain models.
    arbitrary_types_allowed is required for ConfidenceResult (non-Pydantic type).
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    query: str
    workspace_id: str
    workspace_name: str
    retrieved_chunks: List[RetrievedChunk]
    recent_messages: List[dict]
    workspace_summary: str
    confidence: Any  # ConfidenceResult dataclass
    sources: List[Any]  # SourceDocument dataclass
    mode: str
