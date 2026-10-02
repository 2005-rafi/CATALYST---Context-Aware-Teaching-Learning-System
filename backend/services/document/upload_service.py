import uuid
from datetime import datetime, timezone
from backend.repositories.sqlite.document_repository import DocumentRepository
from backend.repositories.sqlite.workspace_repository import WorkspaceRepository
from backend.services.document.storage_service import StorageService
from backend.core.exceptions.exceptions import InvalidFileTypeException, FileTooLargeException, WorkspaceNotFoundException

class UploadService:
    def __init__(self):
        self.document_repo = DocumentRepository()
        self.workspace_repo = WorkspaceRepository()
        self.storage_service = StorageService()

    def validate_file(self, filename: str, content_type: str, size_bytes: int) -> None:
        valid_types = [
            "application/pdf", 
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        
        if content_type not in valid_types:
            # Check by extension if content-type is generic
            if not (filename.endswith(".pdf") or filename.endswith(".docx")):
                raise InvalidFileTypeException(f"Invalid file type: {content_type}. Only PDF and DOCX are supported.")
                
        # 50MB limit
        if size_bytes > 50 * 1024 * 1024:
            raise FileTooLargeException(f"File size exceeds 50MB limit.")

    def get_file_type(self, content_type: str, filename: str) -> str:
        if "pdf" in content_type.lower() or filename.lower().endswith(".pdf"):
            return "pdf"
        elif "wordprocessingml" in content_type.lower() or filename.lower().endswith(".docx"):
            return "docx"
        return "unknown"

    def upload_document(self, workspace_id: str, file_content: bytes, filename: str, content_type: str) -> dict:
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
            file_path=""
        )
        
        try:
            # Save to disk
            file_path, file_size_mb = self.storage_service.save_file(
                workspace_id, document_id, file_content, filename
            )
            
            # Update record via repository interface (not _execute directly)
            self.document_repo.update_file_info(document_id, file_path, file_size_mb)
            
            return self.document_repo.get_document(document_id)
            
        except Exception as e:
            self.document_repo.update_processing_status(document_id, "failed")
            raise e
