"""
ContextPackage — immutable context bundle passed from ContextBuilder to PromptBuilder.
Extended with CI fields: session_id, memory_profile_snippet, detected_topics.
Extended with Visual RAG fields: retrieved_figures.
"""
from typing import List, Any
from pydantic import BaseModel, ConfigDict
from backend.models.chat import RetrievedChunk


class ContextPackage(BaseModel):
    """
    Immutable context bundle passed from ContextBuilder to PromptBuilder.
    arbitrary_types_allowed is required for ConfidenceResult (non-Pydantic type).
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    query: str
    workspace_id: str
    workspace_name: str
    retrieved_chunks: List[RetrievedChunk]
    recent_messages: List[dict]
    workspace_summary: str
    confidence: Any           # ConfidenceResult dataclass
    sources: List[Any]        # SourceDocument dataclass
    mode: str

    # --- Conversational Intelligence fields ---
    session_id: str = ""
    memory_profile_snippet: str = ""
    workspace_memory_bank: str = ""
    detected_topics: List[str] = []

    # --- Visual RAG fields ---
    retrieved_figures: List[dict] = []  # List of FigureReference dicts

    # --- Out-of-Box Context Hybridization fields ---
    is_out_of_box: bool = False
    uncovered_topics: List[str] = []
