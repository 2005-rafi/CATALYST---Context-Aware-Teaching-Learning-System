from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form, BackgroundTasks, Depends
from backend.schemas.document_schemas import (
    DocumentUploadResponse,
    DocumentStatusResponse,
    DocumentListResponse
)
from backend.services.document.upload_service import UploadService
from backend.services.document.document_deletion_service import DocumentDeletionService
from backend.services.document.ingestion_service import IngestionService
from backend.repositories.sqlite.document_repository import DocumentRepository
from backend.core.dependencies import (
    get_upload_service,
    get_ingestion_service,
    get_document_deletion_service,
    get_document_repository,
)
from backend.core.exceptions.exceptions import DocumentNotFoundException
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/document", tags=["Document"])

@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    background_tasks: BackgroundTasks,
    workspace_id: str = Form(...),
    file: UploadFile = File(...),
    us: UploadService = Depends(get_upload_service),
    is_: IngestionService = Depends(get_ingestion_service),
):
    """Upload a document file. Ingestion runs asynchronously in the background."""
    file_content = await file.read()
    doc = us.upload_document(
        workspace_id=workspace_id,
        file_content=file_content,
        filename=file.filename,
        content_type=file.content_type
    )

    background_tasks.add_task(
        is_.ingest_document,
        doc["document_id"],
        workspace_id
    )

    return DocumentUploadResponse(
        success=True,
        document_id=doc["document_id"],
        status="processing",
        message="Document uploaded and ingestion started"
    )

@router.get("/status/{document_id}", response_model=DocumentStatusResponse)
def get_document_status(
    document_id: str,
    doc_repo: DocumentRepository = Depends(get_document_repository),
):
    """Get processing status for a specific document."""
    doc = doc_repo.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    return DocumentStatusResponse(
        document_id=doc["document_id"],
        workspace_id=doc["workspace_id"],
        processing_status=doc["processing_status"],
        total_chunks=doc["total_chunks"],
        embedding_status=bool(doc["embedding_status"]),
        file_name=doc["file_name"],
        created_at=doc["upload_time"],
        file_size_mb=doc.get("file_size_mb", 0.0)
    )


@router.get("/workspace/{workspace_id}", response_model=DocumentListResponse)
def get_workspace_documents(
    workspace_id: str,
    doc_repo: DocumentRepository = Depends(get_document_repository),
):
    """List all documents in a workspace."""
    docs = doc_repo.get_documents_by_workspace(workspace_id)
    responses = [
        DocumentStatusResponse(
            document_id=doc["document_id"],
            workspace_id=doc["workspace_id"],
            processing_status=doc["processing_status"],
            total_chunks=doc["total_chunks"],
            embedding_status=bool(doc["embedding_status"]),
            file_name=doc["file_name"],
            created_at=doc["upload_time"],
            file_size_mb=doc.get("file_size_mb", 0.0)
        )
        for doc in docs
    ]

    return DocumentListResponse(documents=responses, count=len(responses))

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: str,
    deletion_service: DocumentDeletionService = Depends(get_document_deletion_service),
):
    """Delete a document and all associated artifacts (file, chunks, FAISS, counters)."""
    try:
        deletion_service.delete_document(document_id)
    except DocumentNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return
