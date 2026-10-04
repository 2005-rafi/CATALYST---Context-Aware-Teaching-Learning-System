"""System API schemas — Pydantic request/response models."""
from pydantic import BaseModel
from typing import Dict, Any


class HealthResponse(BaseModel):
    status: str
    version: str
    subsystems: Dict[str, Any]
