from dataclasses import dataclass
from typing import Optional

@dataclass
class Workspace:
    workspace_id: str
    workspace_name: str
    description: str
    created_at: str
    updated_at: str
    status: str
    total_documents: int
    total_chunks: int
    storage_used_mb: float

    @classmethod
    def from_dict(cls, data: dict) -> 'Workspace':
        return cls(
            workspace_id=data.get("workspace_id"),
            workspace_name=data.get("workspace_name"),
            description=data.get("description", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            status=data.get("status", "active"),
            total_documents=data.get("total_documents", 0),
            total_chunks=data.get("total_chunks", 0),
            storage_used_mb=data.get("storage_used_mb", 0.0)
        )
