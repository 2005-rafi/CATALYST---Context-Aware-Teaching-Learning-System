"""
Persistence & Data Access Layer for CATALYST.
Access subpackages directly:
  from backend.repositories.sqlite import ...
  from backend.repositories.vector import ...
  from backend.repositories.bm25 import ...
"""
from backend.repositories.base_retriever import BaseRetriever

__all__ = ["BaseRetriever"]
