from fastapi import APIRouter, HTTPException, status, Depends
from backend.schemas.workspace_schemas import (
    CreateWorkspaceRequest,
    WorkspaceResponse,
    WorkspaceListResponse,
    DeleteWorkspaceResponse
)
from backend.services.workspace.workspace_service import WorkspaceService
from backend.core.dependencies import get_workspace_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/workspace", tags=["Workspace"])


@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    request: CreateWorkspaceRequest,
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Create a new workspace. AppException subclasses are caught by the global handler."""
    ws = service.create_workspace(
        name=request.workspace_name,
        description=request.description
    )
    return ws


@router.get("/", response_model=WorkspaceListResponse)
def list_workspaces(service: WorkspaceService = Depends(get_workspace_service)):
    workspaces = service.list_workspaces()
    return WorkspaceListResponse(workspaces=workspaces, count=len(workspaces))


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(
    workspace_id: str,
    service: WorkspaceService = Depends(get_workspace_service),
):
    # WorkspaceNotFoundException (AppException, 404) handled by global handler
    return service.get_workspace(workspace_id)


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(
    workspace_id: str,
    service: WorkspaceService = Depends(get_workspace_service),
):
    # WorkspaceNotFoundException (AppException, 404) handled by global handler
    service.delete_workspace(workspace_id)
    return
