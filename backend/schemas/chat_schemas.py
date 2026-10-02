from pydantic import BaseModel, Field
from typing import List

class ChatRequest(BaseModel):
    # P18 FIX: added max_length to prevent token explosion / DoS via oversized queries
    query: str = Field(..., min_length=1, max_length=4096, description="User query, max 4096 characters")
    workspace_id: str = Field(..., min_length=1, max_length=64)
    model: str = Field(default="medium", pattern="^(medium|expert)$")

class SourceChunk(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    source_file: str = ""
    score: float
    
class ChatResponse(BaseModel):
    message_id: str
    response: str
    sources: List[SourceChunk]
    model_used: str

    model_config = {"protected_namespaces": ()}
