from pydantic import BaseModel
from typing import Optional

class AnalyticsResponse(BaseModel):
    workspace_id: str
    total_queries: int
    total_documents: int
    total_chunks: int
    storage_used_mb: float
    groq_requests: int
    local_model_requests: int
    last_updated: Optional[str] = None
