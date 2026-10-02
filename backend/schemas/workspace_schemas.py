from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class CreateWorkspaceRequest(BaseModel):
    workspace_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9 _\-]{0,99}$",
        description="Workspace name: 1–100 chars, alphanumeric, spaces, hyphens, underscores."
    )
    description: str = Field(default="", max_length=500)

class WorkspaceResponse(BaseModel):
    workspace_id: str
    workspace_name: str
    description: str
    created_at: str
    updated_at: str
    status: str
    total_documents: int
    total_chunks: int
    storage_used_mb: float

    model_config = ConfigDict(from_attributes=True)

class WorkspaceListResponse(BaseModel):
    workspaces: List[WorkspaceResponse]
    count: int

class DeleteWorkspaceResponse(BaseModel):
    success: bool
    message: str
