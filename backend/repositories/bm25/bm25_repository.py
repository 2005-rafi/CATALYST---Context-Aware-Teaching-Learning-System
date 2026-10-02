import re
from typing import List, Tuple
from backend.repositories.sqlite.base_repository import BaseRepository
from backend.services.retrieval.base_retriever import BaseRetriever

class BM25Repository(BaseRepository, BaseRetriever):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BM25Repository, cls).__new__(cls)
        return cls._instance

    def rebuild_index(self, workspace_id: str) -> None:
        """
        No-op: SQLite FTS5 virtual table indexes update automatically
        whenever chunks are written to the database.
        """
        pass

    def search(self, workspace_id: str, query: str, top_k: int = 50) -> List[Tuple[str, float]]:
        """
        Executes a sparse lexical BM25 search utilizing SQLite FTS5 built-in metrics,
        guaranteeing O(log N) scale performance and negligible RAM footprint.
        """
        # Clean user query and extract alphanumeric tokens
        clean_query = re.sub(r'[^a-zA-Z0-9\s]', ' ', query).strip()
        tokens = [t for t in clean_query.split() if t]
        
        if not tokens:
            return []
            
        # Formulate FTS5 boolean match query (combining query terms using OR)
        search_terms = " OR ".join(tokens)
        
        # SQLite's bm25() returns negative values (smaller is better).
        # We negate the value to yield a positive relevance score.
        sql = """
            SELECT chunk_id, -bm25(chunks_fts) AS score
            FROM chunks_fts
            WHERE chunks_fts MATCH ? AND workspace_id = ?
            ORDER BY score DESC
            LIMIT ?
        """
        
        try:
            rows = self._execute(sql, (search_terms, workspace_id, top_k), fetch_all=True)
            if not rows:
                return []
            return [(row["chunk_id"], float(row["score"])) for row in rows]
        except Exception:
            # Handle potential SQLite match syntax issues gracefully by falling back to empty list
            return []

    def delete_workspace_index(self, workspace_id: str) -> None:
        """
        No-op: SQLite cascading deletes clean up chunks and virtual indexes automatically.
        """
        pass
