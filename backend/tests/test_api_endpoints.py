import os
import uuid
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.repositories.sqlite.database import initialize_database, db_connection
from backend.repositories.sqlite.schema import create_schema

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    os.makedirs("storage/sqlite", exist_ok=True)
    initialize_database()
    with db_connection() as conn:
        create_schema(conn)

@pytest.fixture
def client():
    return TestClient(app)

def test_health_endpoint(client):
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ok", "healthy", "degraded", "operational"]

def test_workspace_crud_flow(client):
    unique_name = f"API_Test_WS_{uuid.uuid4().hex[:8]}"
    
    # 1. Create Workspace
    create_resp = client.post("/api/v1/workspace/", json={
        "workspace_name": unique_name,
        "description": "Integration test workspace"
    })
    assert create_resp.status_code == 201
    ws = create_resp.json()
    ws_id = ws["workspace_id"]
    assert ws["workspace_name"] == unique_name

    # 2. Get Workspace
    get_resp = client.get(f"/api/v1/workspace/{ws_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["workspace_id"] == ws_id

    # 3. Duplicate name should fail (409 Conflict)
    dup_resp = client.post("/api/v1/workspace/", json={
        "workspace_name": unique_name,
        "description": "Duplicate"
    })
    assert dup_resp.status_code == 409

    # 4. List Workspaces
    list_resp = client.get("/api/v1/workspace/")
    assert list_resp.status_code == 200
    workspaces = list_resp.json()["workspaces"]
    assert any(w["workspace_id"] == ws_id for w in workspaces)

    # 5. Delete Workspace
    del_resp = client.delete(f"/api/v1/workspace/{ws_id}")
    assert del_resp.status_code in [200, 204]

def test_chat_query_validation(client):
    # Test min length validation
    empty_query_resp = client.post("/api/v1/chat/", json={
        "workspace_id": "nonexistent",
        "query": ""
    })
    assert empty_query_resp.status_code == 422

    # Test max length validation (query over 4096 chars)
    giant_query = "a" * 5000
    giant_query_resp = client.post("/api/v1/chat/", json={
        "workspace_id": "nonexistent",
        "query": giant_query
    })
    assert giant_query_resp.status_code == 422

    # Test invalid model mode
    invalid_mode_resp = client.post("/api/v1/chat/", json={
        "workspace_id": "nonexistent",
        "query": "Valid query",
        "model": "ultra_super_mode"
    })
    assert invalid_mode_resp.status_code == 422

    # Test valid modes (simple, medium, expert) do not trigger 422 on schema validation
    # (they will return 404 for nonexistent workspace, proving schema validation passed)
    for valid_mode in ["simple", "medium", "expert"]:
        resp = client.post("/api/v1/chat/", json={
            "workspace_id": "nonexistent_ws_123",
            "query": "Valid query",
            "model": valid_mode
        })
        assert resp.status_code == 404  # WorkspaceNotFoundException, NOT 422 Schema Validation Error!
