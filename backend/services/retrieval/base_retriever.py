from abc import ABC, abstractmethod
from typing import List, Tuple

class BaseRetriever(ABC):
    @abstractmethod
    def search(self, workspace_id: str, query: str, top_k: int) -> List[Tuple[str, float]]:
        """
        Executes a retrieval search for the given query within a specific workspace.
        Returns a list of tuples containing (chunk_id, relevance_score).
        """
        pass
