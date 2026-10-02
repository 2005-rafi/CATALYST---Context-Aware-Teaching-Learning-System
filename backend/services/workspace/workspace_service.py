import os
import uuid
import shutil
from datetime import datetime, timezone

from backend.repositories.sqlite.workspace_repository import WorkspaceRepository
from backend.repositories.sqlite.analytics_repository import AnalyticsRepository
from backend.services.document.storage_service import StorageService
from backend.repositories.vector.vector_repository import VectorRepository
from backend.repositories.bm25.bm25_repository import BM25Repository
from backend.core.config.settings import get_settings
from backend.core.exceptions.exceptions import WorkspaceAlreadyExistsException, WorkspaceNotFoundException, AppException

class WorkspaceService:
    def __init__(self):
        self.workspace_repo = WorkspaceRepository()
        self.analytics_repo = AnalyticsRepository()
        self.storage_service = StorageService()
        self.vector_repo = VectorRepository()
        self.bm25_repo = BM25Repository()
        self.settings = get_settings()

    def create_workspace(self, name: str, description: str = "") -> dict:
        if not name.strip():
            raise AppException("Workspace name cannot be empty", status_code=400)

        # P6 FIX: O(log N) indexed lookup instead of O(N) full-table scan
        if self.workspace_repo.workspace_exists_by_name(name):
            raise WorkspaceAlreadyExistsException(f"Workspace with name '{name}' already exists.")

        workspace_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        ws_dir = os.path.join(self.settings.UPLOADS_PATH, workspace_id)
        
        try:
            ws = self.workspace_repo.create_workspace(
                workspace_id=workspace_id,
                name=name,
                description=description,
                created_at=now,
                updated_at=now
            )
            self.analytics_repo.init_analytics(workspace_id)
            os.makedirs(ws_dir, exist_ok=True)
            return ws
        except Exception as e:
            # Cleanup if directory creation or analytics init fails
            self.workspace_repo.delete_workspace(workspace_id)
            raise e

    def get_workspace(self, workspace_id: str) -> dict:
        ws = self.workspace_repo.get_workspace(workspace_id)
        if not ws:
            raise WorkspaceNotFoundException()
        return ws

    def list_workspaces(self) -> list[dict]:
        return self.workspace_repo.get_all_workspaces()

    def delete_workspace(self, workspace_id: str) -> bool:
        if not self.workspace_exists(workspace_id):
            raise WorkspaceNotFoundException()

        success = self.workspace_repo.delete_workspace(workspace_id)
        if success:
            self.storage_service.delete_workspace_directory(workspace_id)
            self.vector_repo.faiss_manager.delete_index(workspace_id)
            self.bm25_repo.delete_workspace_index(workspace_id)
                
        return success

    def workspace_exists(self, workspace_id: str) -> bool:
        return self.workspace_repo.workspace_exists(workspace_id)
