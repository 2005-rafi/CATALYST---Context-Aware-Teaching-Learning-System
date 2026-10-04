"""
Vector Indexing Persistence Layer (FAISS).
"""
from backend.repositories.vector.faiss_manager import FAISSManager
from backend.repositories.vector.vector_repository import VectorRepository

__all__ = [
    "FAISSManager",
    "VectorRepository",
]
