import os
import uuid
from datetime import datetime, timezone
from backend.repositories.sqlite.database import initialize_database, db_connection
from backend.repositories.sqlite.schema import create_schema
from backend.repositories.sqlite.workspace_repository import WorkspaceRepository
from backend.repositories.sqlite.document_repository import DocumentRepository

# Note: Settings defaults DATABASE_PATH to storage/sqlite/app.db which will be used

def setup_module(module):
    # Ensure storage exists
    os.makedirs("storage/sqlite", exist_ok=True)
    initialize_database()
    with db_connection() as conn:
        create_schema(conn)

def test_workspace_and_document_cascade():
    ws_repo = WorkspaceRepository()
    doc_repo = DocumentRepository()

    ws_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    # 1. Create Workspace
    ws = ws_repo.create_workspace(
        workspace_id=ws_id,
        name=f"Test WS {ws_id}",
        description="Test description",
        created_at=now,
        updated_at=now
    )
    assert ws is not None
    assert ws["workspace_id"] == ws_id

    # 2. Update Workspace
    ws_repo.update_workspace(ws_id, description="Updated desc")
    updated_ws = ws_repo.get_workspace(ws_id)
    assert updated_ws["description"] == "Updated desc"

    # 3. Create Document
    doc_id = str(uuid.uuid4())
    doc = doc_repo.create_document(
        document_id=doc_id,
        workspace_id=ws_id,
        file_name="test.pdf",
        file_type="pdf",
        file_size_mb=1.5,
        upload_time=now,
        file_path="some/path.pdf"
    )
    assert doc is not None

    # 4. Verify Document exists in workspace
    docs = doc_repo.get_documents_by_workspace(ws_id)
    assert len(docs) == 1
    assert docs[0]["document_id"] == doc_id

    # 5. Delete Workspace
    deleted = ws_repo.delete_workspace(ws_id)
    assert deleted is True

    # 6. Verify Cascade Deletion
    docs_after = doc_repo.get_documents_by_workspace(ws_id)
    assert len(docs_after) == 0
    assert doc_repo.get_document(doc_id) is None
