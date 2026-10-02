import logging
import threading
from typing import Dict, List, Set, Optional, Any
from backend.repositories.sqlite.chunk_repository import ChunkRepository

logger = logging.getLogger(__name__)

class CorpusLexicon:
    """
    Corpus-Aware Vocabulary Indexer.
    Extracts and caches the domain vocabulary from indexed document chunks in SQLite,
    allowing rapid, domain-specific spelling and fuzzy technical term recovery.
    """
    _instance: Optional["CorpusLexicon"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "CorpusLexicon":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CorpusLexicon, cls).__new__(cls)
                cls._instance._cache = {}
                cls._instance.chunk_repo = ChunkRepository()
            return cls._instance

    def get_domain_vocabulary(self, workspace_id: str) -> List[str]:
        """
        Returns cached list of unique domain words for the workspace.
        Loads from SQLite if not present in memory cache.
        """
        if workspace_id in self._cache:
            return self._cache[workspace_id]

        words = self._extract_vocabulary_from_db(workspace_id)
        with self._lock:
            self._cache[workspace_id] = words
        logger.info(f"[CorpusLexicon] Cached {len(words)} domain words for workspace '{workspace_id}'")
        return words

    def _extract_vocabulary_from_db(self, workspace_id: str) -> List[str]:
        """
        Queries chunks table to extract unique alphanumeric words.
        """
        chunks = self.chunk_repo.get_chunks_by_workspace(workspace_id)
        return self.extract_words_from_chunks(chunks)

    def extract_words_from_chunks(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """
        Extracts cleaned unique domain words from a list of chunk dicts.
        """
        vocab_set: Set[str] = set()
        for chunk in chunks:
            text = chunk.get("chunk_text", "")
            for word in text.split():
                clean_word = "".join(c for c in word if c.isalnum()).lower()
                # Store words with 3+ characters to avoid single letter noise
                if len(clean_word) >= 3 and not clean_word.isdigit():
                    vocab_set.add(clean_word)

        return sorted(list(vocab_set))

    def invalidate_cache(self, workspace_id: str) -> None:
        """Invalidates cached vocabulary when documents in a workspace change."""
        with self._lock:
            if workspace_id in self._cache:
                del self._cache[workspace_id]
                logger.info(f"[CorpusLexicon] Invalidated cache for workspace '{workspace_id}'")
