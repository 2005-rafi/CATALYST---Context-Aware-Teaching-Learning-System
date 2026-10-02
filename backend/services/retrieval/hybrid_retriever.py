from typing import Tuple, List
from backend.repositories.vector.vector_repository import VectorRepository
from backend.repositories.bm25.bm25_repository import BM25Repository

class HybridRetriever:
    def __init__(self):
        self.vector_repo = VectorRepository()
        self.bm25_repo = BM25Repository()

    def retrieve(self, workspace_id: str, query: str, faiss_top_k: int = 50, bm25_top_k: int = 50) -> Tuple[List[Tuple[str, float]], List[Tuple[str, float]]]:
        # Step 1: FAISS Search
        faiss_results = self.vector_repo.search_similar(workspace_id, query, faiss_top_k)
        if not faiss_results:
            # If workspace has no vectors, we return empty early
            return [], []
            
        # Step 2: BM25 Search
        bm25_results = self.bm25_repo.search(workspace_id, query, bm25_top_k)
        
        return faiss_results, bm25_results
