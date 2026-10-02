import numpy as np
import faiss
from backend.repositories.vector.faiss_manager import FAISSManager
from backend.repositories.sqlite.chunk_repository import ChunkRepository
from backend.services.retrieval.base_retriever import BaseRetriever

class VectorRepository(BaseRetriever):
    def __init__(self):
        self.faiss_manager = FAISSManager()
        self.chunk_repo = ChunkRepository()

    def add_vectors(self, workspace_id: str, chunk_ids: list[str], embeddings: list[list[float]]):
        if not chunk_ids or not embeddings:
            return
            
        index, ids_map = self.faiss_manager.get_or_create_index(workspace_id)
        
        embeddings_np = np.array(embeddings, dtype=np.float32)
        # Normalize for Inner Product (cosine similarity)
        faiss.normalize_L2(embeddings_np)
        
        index.add(embeddings_np)
        ids_map.extend(chunk_ids)
        
        self.faiss_manager.save_index(workspace_id, index, ids_map)
        
        # Update SQLite references
        for chunk_id in chunk_ids:
            self.chunk_repo.update_embedding_ref(chunk_id, "faiss")

    def search(self, workspace_id: str, query: str, top_k: int = 5) -> list[tuple[str, float]]:
        """
        Implements BaseRetriever interface for dense semantic search.
        """
        return self.search_similar(workspace_id, query, top_k)

    def search_similar(self, workspace_id: str, query: str, top_k: int = 5) -> list[tuple[str, float]]:
        from backend.providers.embeddings.embedding_provider import get_embedding_provider
        
        index, ids_map = self.faiss_manager.get_or_create_index(workspace_id)
        if index.ntotal == 0:
            return []
            
        provider = get_embedding_provider()
        query_embedding = provider.embed_text(query)
        
        query_np = np.array([query_embedding], dtype=np.float32)
        faiss.normalize_L2(query_np)
        
        k = min(top_k, index.ntotal)
        if k == 0:
            return []
            
        distances, indices = index.search(query_np, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(ids_map):
                results.append((ids_map[idx], float(distances[0][i])))
                
        return results
