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
        if not chunks:
            return ConfidenceResult(
                level="LOW", 
                sufficient=False, 
                chunk_count=0, 
                message="No relevant snippets found in workspace documents."
            )
            
        max_score = max(c.score for c in chunks)
        passing = [c for c in chunks if c.score >= 0.40]
        
        # High confidence requires strong calibrated match
        if max_score >= self.high_confidence_threshold:
            return ConfidenceResult(
                level="HIGH", 
                sufficient=True, 
                chunk_count=len(chunks), 
                message="Strong matching context found."
            )
            
        # Medium confidence requires moderate match or passing evidence
        if max_score >= 0.40 or len(passing) > 0:
            return ConfidenceResult(
                level="MEDIUM", 
                sufficient=True, 
                chunk_count=len(chunks), 
                message="Partial matching context found."
            )
            
        # Default fallback with evidence still surfaced to LLM
        return ConfidenceResult(
            level="LOW", 
            sufficient=True, 
            chunk_count=len(chunks), 
            message="Low relevance matches detected; synthesizing with cautious grounding."
        )
