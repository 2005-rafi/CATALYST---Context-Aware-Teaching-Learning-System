import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field

from backend.models.chat import RetrievedChunk

logger = logging.getLogger(__name__)

@dataclass
class ChunkEvaluationResult:
    """
    Multi-dimensional quality and coverage evaluation of retrieved context chunks.
    """
    relevance_score: float # 0.0 to 1.0 (mean/max calibrated cross-encoder score)
    coverage_score: float  # 0.0 to 1.0 (keyword & entity coverage)
    structural_score: float # 0.0 to 1.0 (TOC, chapter structure presence)
    grounding_confidence: str # "HIGH", "MEDIUM", "LOW"
    sufficient: bool # True if chunks can ground answer
    detected_gaps: List[str] = field(default_factory=list)
    suggested_action: str = "PROCEED" # "PROCEED", "RETRY_STRUCTURAL", "RETRY_BODY_EXPANSION"
    evaluation_summary: str = ""
    is_out_of_box: bool = False
    uncovered_topics: List[str] = field(default_factory=list)

class ChunkEvaluatorEngine:
    """
    Intelligent Retrieval Quality & Chunk Scoring Engine.
    Evaluates retrieved chunks across 4 critical production dimensions:
    1. Semantic Relevance Score: Neural cross-encoder grounding confidence
    2. Intent & Entity Coverage Score: Query entity representation in chunks
    3. Structural Completeness Score: Front-matter, TOC, and section header integrity
    4. Adaptive Gap Detection: Identifies missing components (e.g., TOC vs body)
    """

    def evaluate(
        self,
        query: str,
        intent: str,
        chunks: List[RetrievedChunk],
        workspace_docs_count: int = 1
    ) -> ChunkEvaluationResult:
        if not chunks:
            return ChunkEvaluationResult(
                relevance_score=0.0,
                coverage_score=0.0,
                structural_score=0.0,
                grounding_confidence="LOW",
                sufficient=False,
                detected_gaps=["No chunks retrieved from workspace index."],
                suggested_action="RETRY_BODY_EXPANSION",
                evaluation_summary="Retrieval failed: 0 chunks available.",
                is_out_of_box=True,
                uncovered_topics=[query]
            )

        q_lower = query.lower()
        
        # 1. Calculate Relevance Score (Mean & Max from Cross-Encoder)
        scores = [c.score for c in chunks if hasattr(c, 'score') and c.score is not None]
        max_score = max(scores) if scores else 0.0
        avg_score = sum(scores) / len(scores) if scores else 0.0
        relevance_score = round(0.6 * max_score + 0.4 * avg_score, 3)

        # 2. Calculate Coverage Score with Substantive Topic Isolation
        raw_words = re.findall(r'\b[a-zA-Z]{3,}\b', q_lower)
        filler_words = {
            "give", "tell", "what", "show", "list", "with", "this", "that", "from",
            "your", "have", "book", "file", "document", "standard", "grade", "explain",
            "describe", "detail", "detailed", "diagram", "diagrams", "figure", "figures",
            "chart", "charts", "illustration", "illustrations", "overview", "summary",
            "please", "can", "could", "would", "about", "into", "their", "there", "these", "those"
        }
        domain_generic_words = {
            "system", "systems", "human", "body", "living", "organism", "organisms",
            "biology", "science", "structure", "function", "functions", "process", "processes", "types"
        }

        specific_terms = [w for w in raw_words if w not in filler_words and w not in domain_generic_words]
        key_terms = specific_terms if specific_terms else [w for w in raw_words if w not in filler_words]
        
        combined_text = " ".join([c.chunk_text.lower() for c in chunks])
        if key_terms:
            matched_terms = [t for t in key_terms if t in combined_text]
            unmatched_terms = [t for t in key_terms if t not in combined_text]
            coverage_score = round(len(matched_terms) / len(key_terms), 3)
        else:
            matched_terms = []
            unmatched_terms = []
            coverage_score = 0.85

        # 3. Calculate Structural Completeness Score
        has_toc_chunk = any(
            "contents" in c.chunk_text.lower() or 
            "chapter 1" in c.chunk_text.lower() or 
            "table of contents" in (c.section_heading or "").lower() or
            (c.page_number is not None and c.page_number <= 3)
            for c in chunks
        )
        has_headings = any(bool(c.section_heading and len(c.section_heading) > 2) for c in chunks)
        structural_score = 0.9 if has_toc_chunk else (0.6 if has_headings else 0.3)

        # 4. Out-of-Box Topic Detection & Gap Analysis
        gaps: List[str] = []
        suggested_action = "PROCEED"
        is_out_of_box = False
        uncovered_topics: List[str] = []

        # If specific substantive concepts were asked, but NONE matched the retrieved chunks:
        if specific_terms and len(matched_terms) == 0 and not has_toc_chunk and intent not in ("STRUCTURAL_OVERVIEW", "USER_META_CONVERSATION"):
            is_out_of_box = True
            uncovered_topics = specific_terms
            grounding_confidence = "LOW"
            sufficient = False
            gaps.append(f"Substantive query topics {specific_terms} not found in workspace documents.")
            suggested_action = "PROCEED"
        elif intent in ("STRUCTURAL_OVERVIEW", "BOOK_STRUCTURE_TOC") and not has_toc_chunk:
            gaps.append("Structural TOC / Chapter index missing from retrieved evidence.")
            suggested_action = "RETRY_STRUCTURAL"
        elif intent in ("CONCEPTUAL", "TOPICAL_CONCEPT", "COMPARATIVE") and len(chunks) == 1 and chunks[0].page_number in (1, 2, 3):
            # Only front matter retrieved for substantive topic
            gaps.append("Substantive body passages missing; only front matter retrieved.")
            suggested_action = "RETRY_BODY_EXPANSION"
        elif relevance_score < 0.05 and max_score < 0.10 and not has_toc_chunk:
            gaps.append("Low semantic relevance across candidate pool.")
            suggested_action = "RETRY_BODY_EXPANSION"

        # 5. Determine Overall Grounding Confidence
        if not is_out_of_box:
            if (relevance_score >= 0.40 or (intent == "STRUCTURAL_OVERVIEW" and has_toc_chunk)) and coverage_score >= 0.50:
                grounding_confidence = "HIGH"
                sufficient = True
            elif (relevance_score >= 0.15 or has_toc_chunk) and coverage_score >= 0.30:
                grounding_confidence = "MEDIUM"
                sufficient = True
            else:
                grounding_confidence = "LOW"
                sufficient = False if gaps else (coverage_score >= 0.20 and relevance_score >= 0.10)

        summary = (
            f"Evaluated {len(chunks)} chunks | Relevance: {relevance_score:.2f} | "
            f"Coverage: {coverage_score:.2f} | Structural: {structural_score:.2f} | "
            f"Confidence: {grounding_confidence} | OutOfBox: {is_out_of_box} | Action: {suggested_action}"
        )
        logger.info(f"[ChunkEvaluatorEngine] {summary}")

        return ChunkEvaluationResult(
            relevance_score=relevance_score,
            coverage_score=coverage_score,
            structural_score=structural_score,
            grounding_confidence=grounding_confidence,
            sufficient=sufficient,
            detected_gaps=gaps,
            suggested_action=suggested_action,
            evaluation_summary=summary,
            is_out_of_box=is_out_of_box,
            uncovered_topics=uncovered_topics
        )
