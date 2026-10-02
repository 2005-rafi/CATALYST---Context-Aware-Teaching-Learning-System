from backend.repositories.sqlite.base_repository import BaseRepository

class DocumentRepository(BaseRepository):
    def create_document(self, document_id: str, workspace_id: str, file_name: str, file_type: str, file_size_mb: float, upload_time: str, file_path: str) -> dict:
        self._execute(
            "INSERT INTO documents (document_id, workspace_id, file_name, file_type, file_size_mb, upload_time, file_path) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (document_id, workspace_id, file_name, file_type, file_size_mb, upload_time, file_path)
        )
        return self.get_document(document_id)

    def get_document(self, document_id: str) -> dict | None:
        return self._execute(
            "SELECT * FROM documents WHERE document_id = ?",
            (document_id,),
            fetch_one=True
        )

    def get_documents_by_workspace(self, workspace_id: str) -> list[dict]:
        return self._execute(
            "SELECT * FROM documents WHERE workspace_id = ?",
            (workspace_id,),
            fetch_all=True
        )

    def update_processing_status(self, document_id: str, status: str):
        self._execute(
            "UPDATE documents SET processing_status = ? WHERE document_id = ?",
            (status, document_id)
        )

    def update_chunk_stats(self, document_id: str, total_chunks: int, embedding_status: bool = True):
        self._execute(
            "UPDATE documents SET total_chunks = ?, embedding_status = ? WHERE document_id = ?",
            (total_chunks, 1 if embedding_status else 0, document_id)
        )

    def update_file_info(self, document_id: str, file_path: str, file_size_mb: float) -> None:
        """Update the physical file path and size after successful disk write."""
        self._execute(
            "UPDATE documents SET file_path = ?, file_size_mb = ? WHERE document_id = ?",
            (file_path, file_size_mb, document_id)
        )

    def delete_document(self, document_id: str) -> bool:
        rowcount = self._execute(
            "DELETE FROM documents WHERE document_id = ?",
            (document_id,)
        )
        return rowcount > 0
