from backend.repositories.sqlite.base_repository import BaseRepository

class WorkspaceRepository(BaseRepository):
    def create_workspace(self, workspace_id: str, name: str, description: str, created_at: str, updated_at: str) -> dict:
        self._execute(
            "INSERT INTO workspaces (workspace_id, workspace_name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (workspace_id, name, description, created_at, updated_at)
        )
        return self.get_workspace(workspace_id)

    def get_workspace(self, workspace_id: str) -> dict | None:
        return self._execute(
            "SELECT * FROM workspaces WHERE workspace_id = ?",
            (workspace_id,),
            fetch_one=True
        )

    def get_all_workspaces(self) -> list[dict]:
        return self._execute(
            "SELECT * FROM workspaces ORDER BY created_at DESC",
            fetch_all=True
        )

    def update_workspace(self, workspace_id: str, **fields):
        if not fields:
            return
        
        set_clause = ", ".join([f"{k} = ?" for k in fields.keys()])
        values = tuple(fields.values()) + (workspace_id,)
        
        self._execute(
            f"UPDATE workspaces SET {set_clause} WHERE workspace_id = ?",
            values
        )

    def delete_workspace(self, workspace_id: str) -> bool:
        rowcount = self._execute(
            "DELETE FROM workspaces WHERE workspace_id = ?",
            (workspace_id,)
        )
        return rowcount > 0

    def workspace_exists(self, workspace_id: str) -> bool:
        row = self._execute(
            "SELECT 1 FROM workspaces WHERE workspace_id = ?",
            (workspace_id,),
            fetch_one=True
        )
        return row is not None

    def increment_document_count(self, workspace_id: str, delta: int = 1):
        self._execute(
            "UPDATE workspaces SET total_documents = total_documents + ? WHERE workspace_id = ?",
            (delta, workspace_id)
        )

    def increment_chunk_count(self, workspace_id: str, delta: int):
        self._execute(
            "UPDATE workspaces SET total_chunks = total_chunks + ? WHERE workspace_id = ?",
            (delta, workspace_id)
        )

    def workspace_exists_by_name(self, name: str) -> bool:
        """O(log N) indexed check — replaces the previous O(N) full-scan in WorkspaceService."""
        row = self._execute(
            "SELECT 1 FROM workspaces WHERE workspace_name = ?",
            (name,),
            fetch_one=True
        )
        return row is not None
