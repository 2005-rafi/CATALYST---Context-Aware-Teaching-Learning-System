"""Document API schemas — Pydantic request/response models."""
from pydantic import BaseModel, ConfigDict
from typing import List


class DocumentUploadResponse(BaseModel):
    success: bool
    document_id: str
    status: str
    message: str


class DocumentStatusResponse(BaseModel):
    document_id: str
    workspace_id: str
    processing_status: str
    total_chunks: int
    embedding_status: bool
    file_name: str
    created_at: str
    file_size_mb: float

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    documents: List[DocumentStatusResponse]
    count: int
