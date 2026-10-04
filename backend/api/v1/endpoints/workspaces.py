"""Workspace management API endpoints."""
import logging
from fastapi import APIRouter, Depends, status
from backend.schemas.workspaces import (
    CreateWorkspaceRequest,
    WorkspaceResponse,
    WorkspaceListResponse,
)
from backend.services.workspace.workspace_service import WorkspaceService
from backend.core.dependencies import get_workspace_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workspace", tags=["Workspace"])


@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    request: CreateWorkspaceRequest,
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Create a new workspace. AppException subclasses are caught by the global handler."""
    ws = service.create_workspace(
        name=request.workspace_name or request.name or "",
        description=request.description or ""
    )
    return ws


@router.get("/", response_model=WorkspaceListResponse)
def list_workspaces(service: WorkspaceService = Depends(get_workspace_service)):
    """List all available workspaces."""
    workspaces = service.list_workspaces()
    return WorkspaceListResponse(workspaces=workspaces, count=len(workspaces))


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(
    workspace_id: str,
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Get metadata for a single workspace."""
    return service.get_workspace(workspace_id)


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(
    workspace_id: str,
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Delete a workspace and all nested documents and vector indices."""
    service.delete_workspace(workspace_id)
    return
