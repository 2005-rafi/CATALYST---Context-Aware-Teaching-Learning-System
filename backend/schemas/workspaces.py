"""Workspace API schemas — Pydantic request/response models."""
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional


class CreateWorkspaceRequest(BaseModel):
    workspace_name: Optional[str] = Field(default=None, max_length=100)
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default="", max_length=500)

    @model_validator(mode="after")
    def validate_name(self):
        target_name = (self.workspace_name or self.name or "").strip()
        if not target_name:
            raise ValueError("workspace_name or name must be provided")
        self.workspace_name = target_name
        self.name = target_name
        return self


class WorkspaceResponse(BaseModel):
    workspace_id: str
    workspace_name: str
    description: Optional[str] = ""
    created_at: str
    updated_at: str
    status: Optional[str] = "active"
    total_documents: Optional[int] = 0
    total_chunks: Optional[int] = 0
    storage_used_mb: Optional[float] = 0.0


class WorkspaceListResponse(BaseModel):
    workspaces: List[WorkspaceResponse]
    count: int = 0
    total_count: Optional[int] = None

    @model_validator(mode="after")
    def populate_counts(self):
        if self.count == 0 and self.workspaces:
            self.count = len(self.workspaces)
        if self.total_count is None:
            self.total_count = self.count
        return self


class DeleteWorkspaceResponse(BaseModel):
    workspace_id: str
    status: str
    message: str
