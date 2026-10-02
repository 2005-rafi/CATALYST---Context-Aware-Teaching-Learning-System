from dataclasses import dataclass
from typing import List
from backend.core.config.settings import get_settings
from backend.models.chat import RetrievedChunk

@dataclass
class ConfidenceResult:
    level: str
    sufficient: bool
    chunk_count: int
    message: str

class ConfidenceEngine:
    def __init__(self):
        self.min_score = get_settings().CROSS_ENCODER_MIN_SCORE
        self.high_confidence_threshold = 0.70
        self.medium_confidence_threshold = 0.55

    def evaluate(self, chunks: List[RetrievedChunk]) -> ConfidenceResult:
        """
        Evaluates retrieval confidence based on a hybrid score-and-count metric,
        assessing both the top chunk match quality and supporting evidence count.
        """
        passing = [c for c in chunks if c.score >= self.min_score]
        
        if not passing:
            return ConfidenceResult(
                level="LOW", 
                sufficient=False, 
                chunk_count=0, 
                message="No relevant snippets found matching the query context."
            )
            
        max_score = max(c.score for c in passing)
        
        # High confidence requires both a high-quality top match and supporting chunks
        if max_score >= self.high_confidence_threshold and len(passing) >= 2:
            return ConfidenceResult(
                level="HIGH", 
                sufficient=True, 
                chunk_count=len(passing), 
                message="Strong matching context found."
            )
            
        # Medium confidence requires at least a decent match or some passing evidence
        if max_score >= self.medium_confidence_threshold:
            return ConfidenceResult(
                level="MEDIUM", 
                sufficient=True, 
                chunk_count=len(passing), 
                message="Partial matching context found."
            )
            
        # Default fallback to low confidence if scores are marginally below medium threshold
        return ConfidenceResult(
            level="LOW", 
            sufficient=False, 
            chunk_count=len(passing), 
            message="Low relevance matches detected."
        )
