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

    def remove_vectors_by_ids(self, workspace_id: str, chunk_ids_to_remove: set[str]):
        """
        Rebuilds the FAISS index for the workspace without the specified deleted chunk IDs,
        preventing ghost vector pollution in dense semantic search.
        """
        index, ids_map = self.faiss_manager.get_or_create_index(workspace_id)
        if not ids_map or not chunk_ids_to_remove:
            return
        
        remaining_indices = [i for i, cid in enumerate(ids_map) if cid not in chunk_ids_to_remove]
        if len(remaining_indices) == len(ids_map):
            return  # Nothing to remove
            
        dim = index.d
        new_index = faiss.IndexFlatIP(dim)
        new_ids_map = []
        
        if remaining_indices:
            remaining_vectors = np.empty((len(remaining_indices), dim), dtype=np.float32)
            for new_i, old_i in enumerate(remaining_indices):
                remaining_vectors[new_i] = index.reconstruct(old_i)
                new_ids_map.append(ids_map[old_i])
            new_index.add(remaining_vectors)
            
        self.faiss_manager.save_index(workspace_id, new_index, new_ids_map)
