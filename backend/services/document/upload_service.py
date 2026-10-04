import uuid
from datetime import datetime, timezone
from backend.repositories.sqlite.document_repository import DocumentRepository
from backend.repositories.sqlite.workspace_repository import WorkspaceRepository
from backend.services.document.storage_service import StorageService
from backend.core.exceptions.exceptions import (
    InvalidFileTypeException,
    FileTooLargeException,
    WorkspaceNotFoundException,
)


class UploadService:
    def __init__(self):
        self.document_repo = DocumentRepository()
        self.workspace_repo = WorkspaceRepository()
        self.storage_service = StorageService()

    def validate_file(self, filename: str, content_type: str, size_bytes: int) -> None:
        valid_extensions = (".pdf", ".docx", ".txt", ".md")
        valid_mime_prefixes = (
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
            "text/markdown",
            "application/octet-stream",
        )

        fn = filename.lower()
        ct = (content_type or "").lower()

        has_valid_ext = any(fn.endswith(ext) for ext in valid_extensions)
        has_valid_mime = any(ct.startswith(m) for m in valid_mime_prefixes)

        if not (has_valid_ext or has_valid_mime):
            raise InvalidFileTypeException(
                f"Invalid file type: {content_type}. Supported formats: PDF, DOCX, TXT, MD."
            )

        # 50MB limit
        if size_bytes > 50 * 1024 * 1024:
            raise FileTooLargeException("File size exceeds 50MB limit.")

    def get_file_type(self, content_type: str, filename: str) -> str:
        fn = filename.lower()
        ct = (content_type or "").lower()

        if fn.endswith(".pdf") or "pdf" in ct:
            return "pdf"
        elif fn.endswith(".docx") or "wordprocessingml" in ct:
            return "docx"
        elif fn.endswith(".md") or "markdown" in ct:
            return "md"
        elif fn.endswith(".txt") or "text/plain" in ct:
            return "txt"
        return "txt"

    def upload_document(
        self,
        workspace_id: str,
        file_content: bytes,
        filename: str,
        content_type: str,
    ) -> dict:
        if not self.workspace_repo.workspace_exists(workspace_id):
            raise WorkspaceNotFoundException()

        size_bytes = len(file_content)
        self.validate_file(filename, content_type, size_bytes)

        document_id = str(uuid.uuid4())
        file_type = self.get_file_type(content_type, filename)
        now = datetime.now(timezone.utc).isoformat()

        # Create pending record
        self.document_repo.create_document(
            document_id=document_id,
            workspace_id=workspace_id,
            file_name=filename,
            file_type=file_type,
            file_size_mb=0.0,
            upload_time=now,
            file_path="",
        )

        try:
            # Save to disk
            file_path, file_size_mb = self.storage_service.save_file(
                workspace_id, document_id, file_content, filename
            )

            # Update record via repository interface
            self.document_repo.update_file_info(document_id, file_path, file_size_mb)

            return self.document_repo.get_document(document_id)

        except Exception as e:
            self.document_repo.update_processing_status(document_id, "failed")
            raise e
