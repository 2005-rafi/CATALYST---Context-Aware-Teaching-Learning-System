import re
from typing import List, Set
from backend.core.config.settings import get_settings
from backend.models.chat import RetrievedChunk

class ContextCompressor:
    def __init__(self):
        settings = get_settings()
        self.similarity_threshold = 0.80  # Jaccard threshold (usually 0.80-0.85 is ideal for token overlap check)
        self.max_chunks = settings.CONTEXT_MAX_CHUNKS
        self.min_chunks = 3

    def compress(self, chunks: List[RetrievedChunk]) -> List[RetrievedChunk]:
        """
        Prunes redundant chunks using Jaccard Similarity of token sets,
        which is highly optimized and runs in O(N) using Python hash sets.
        """
        keep = []
        token_sets = []  # Parallel list storing sets of tokens for kept chunks
        
        for chunk in chunks:
            chunk_tokens = self._to_token_set(chunk.chunk_text)
            is_duplicate = False
            
            for kept_tokens in token_sets:
                if not chunk_tokens or not kept_tokens:
                    continue
                    
                # Fast set intersection and union
                intersection = len(chunk_tokens.intersection(kept_tokens))
                union = len(chunk_tokens.union(kept_tokens))
                jaccard_ratio = intersection / union
                
                if jaccard_ratio > self.similarity_threshold:
                    is_duplicate = True
                    break
                    
            if not is_duplicate:
                keep.append(chunk)
                token_sets.append(chunk_tokens)
                
        return keep[:self.max_chunks]

    def _to_token_set(self, text: str) -> Set[str]:
        # Quick tokenization using regex
        text_lower = text.lower()
        return set(re.findall(r'\b\w+\b', text_lower))

    def get_final_chunk_count(self, chunks: List[RetrievedChunk]) -> int:
        return len(chunks)
