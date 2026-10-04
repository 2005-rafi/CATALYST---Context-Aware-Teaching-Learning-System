import os
import faiss
import numpy as np
import json
from backend.core.config.settings import get_settings
import logging

logger = logging.getLogger(__name__)

class FAISSManager:
    def __init__(self):
        self.settings = get_settings()
        # P3 FIX: dimension is now derived lazily from the embedding provider.
        # Hard-coding 384 would silently corrupt FAISS if EMBEDDING_MODEL is changed.
        self._dimension: int | None = None

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            from backend.providers.embeddings.embedding_provider import get_embedding_provider
            self._dimension = get_embedding_provider().dimension
        return self._dimension


    def _get_index_path(self, workspace_id: str) -> str:
        return f"{self.settings.FAISS_PATH}/{workspace_id}.index"
        
    def _get_ids_path(self, workspace_id: str) -> str:
        return f"{self.settings.FAISS_PATH}/{workspace_id}_ids.json"

    def get_or_create_index(self, workspace_id: str) -> tuple[faiss.Index, list[str]]:
        index_path = self._get_index_path(workspace_id)
        ids_path = self._get_ids_path(workspace_id)
        
        if os.path.exists(index_path) and os.path.exists(ids_path):
            index = faiss.read_index(index_path)
            with open(ids_path, "r") as f:
                ids_map = json.load(f)
            return index, ids_map
            
        # Use HNSW vector graph search index to guarantee O(log N) search complexity under high scale (50+ books)
        # 32 is the number of connections per node (M), a standard balance between precision and graph size
        index = faiss.IndexHNSWFlat(self.dimension, 32, faiss.METRIC_INNER_PRODUCT)
        return index, []

    def save_index(self, workspace_id: str, index: faiss.Index, ids_map: list[str]):
        index_path = self._get_index_path(workspace_id)
        ids_path = self._get_ids_path(workspace_id)
        
        faiss.write_index(index, index_path)
        with open(ids_path, "w") as f:
            json.dump(ids_map, f)

    def delete_index(self, workspace_id: str):
        index_path = self._get_index_path(workspace_id)
        ids_path = self._get_ids_path(workspace_id)
        
        if os.path.exists(index_path):
            os.remove(index_path)
        if os.path.exists(ids_path):
            os.remove(ids_path)
