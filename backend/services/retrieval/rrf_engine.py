from collections import defaultdict
from typing import List, Tuple
from backend.core.config.settings import get_settings

class RRFEngine:
    def __init__(self):
        self.rrf_constant = get_settings().RRF_CONSTANT
        
    def fuse(self, ranked_lists: List[List[Tuple[str, float]]], top_n: int = 20) -> List[Tuple[str, float]]:
        rrf_scores = defaultdict(float)
        
        for ranked_list in ranked_lists:
            for i, (chunk_id, _) in enumerate(ranked_list):
                rrf_scores[chunk_id] += 1.0 / (i + 1 + self.rrf_constant)
                
        # Sort by RRF score descending
        sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:top_n]
