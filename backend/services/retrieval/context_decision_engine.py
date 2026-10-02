import re
from typing import List
from backend.core.config.settings import get_settings
from backend.models.chat import RetrievedChunk

class ContextDecisionEngine:
    """
    Intelligent Context Decision & Refinement Engine for Pedagogical RAG.
    Performs intent classification, semantic chunk deduplication, thresholding,
    and intent-guided structural formatting for 1,000+ chunk document stores.
    """
    def __init__(self):
        self.settings = get_settings()
        self.min_score = self.settings.CROSS_ENCODER_MIN_SCORE

    def decide(self, query: str, chunks: List[RetrievedChunk]) -> List[RetrievedChunk]:
        """
        Filters, de-duplicates, and formats retrieved chunks based on query intent
        and document structural provenance.
        """
        if not chunks:
            return []

        # 1. Filter out low-relevance chunks using Cross-Encoder threshold
        relevant_chunks = [c for c in chunks if c.score >= self.min_score]
        
        # Fallback: if no chunks pass the strict threshold, preserve the single highest scoring chunk
        # if its score is reasonably positive (> 0.20), otherwise treat as empty (zero-doc fallback).
        if not relevant_chunks and chunks:
            top_candidate = max(chunks, key=lambda x: x.score)
            if top_candidate.score >= 0.20:
                relevant_chunks = [top_candidate]

        # 2. Semantic Deduplication across large corpora (e.g. 1000+ chunk books)
        deduped_chunks = self._deduplicate_chunks(relevant_chunks)

        # 3. Classify Query Intent
        intent = self._classify_intent(query)
        
        # 4. Format/Structure chunks based on intent and metadata
        engineered_chunks = []
        for chunk in deduped_chunks:
            formatted_text = self._engineer_chunk_text(chunk, intent)
            
            engineered_chunks.append(
                RetrievedChunk(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    source_file=chunk.source_file,
                    chunk_text=formatted_text,
                    score=chunk.score,
                    page_number=chunk.page_number,
                    section_heading=chunk.section_heading
                )
            )
            
        return engineered_chunks

    def _deduplicate_chunks(self, chunks: List[RetrievedChunk]) -> List[RetrievedChunk]:
        """
        Removes near-duplicate chunks that share significant character overlap,
        ensuring diversity in the top-N retrieved context.
        """
        unique_chunks = []
        seen_snippets = []

        for chunk in chunks:
            text_sample = chunk.chunk_text.strip().lower()[:150]
            is_dup = False
            for seen in seen_snippets:
                # Check character prefix overlap
                if len(text_sample) > 50 and text_sample in seen or seen in text_sample:
                    is_dup = True
                    break
            if not is_dup:
                seen_snippets.append(text_sample)
                unique_chunks.append(chunk)

        return unique_chunks

    def _classify_intent(self, query: str) -> str:
        query_lower = query.lower()
        
        technical_keywords = ["code", "function", "class", "import", "def ", "config", "install", "exception", "error", "api", "database", "schema", "table"]
        quantitative_keywords = ["metrics", "percent", "%", "average", "mean", "count", "sum", "number", "stat", "total", "amount", "ratio"]
        comparative_keywords = ["versus", "vs", "difference", "compare", "contrast", "alternative", "better", "worse", "comparison", "distinguish"]
        pedagogical_keywords = ["explain", "how does", "why does", "what is", "mechanism", "steps", "process", "define", "concept", "teach", "break down", "overview"]
        
        if any(kw in query_lower for kw in technical_keywords):
            return "technical"
        elif any(kw in query_lower for kw in quantitative_keywords):
            return "quantitative"
        elif any(kw in query_lower for kw in comparative_keywords):
            return "comparative"
        elif any(kw in query_lower for kw in pedagogical_keywords):
            return "pedagogical"
        return "descriptive"

    def _engineer_chunk_text(self, chunk: RetrievedChunk, intent: str) -> str:
        """
        Format the chunk text dynamically based on the detected intent and metadata
        to maximize retrieval value for the LLM.
        """
        metadata_parts = [f"FILE: {chunk.source_file}"]
        if chunk.page_number:
            metadata_parts.append(f"PAGE: {chunk.page_number}")
        if chunk.section_heading:
            metadata_parts.append(f"SECTION: {chunk.section_heading}")
            
        header = f"[{' | '.join(metadata_parts)}]"
        text = chunk.chunk_text.strip()
        
        # Apply intent-based formatting optimizations
        if intent == "technical":
            if ("import " in text or "def " in text or "class " in text or "const " in text) and "```" not in text:
                text = f"```\n{text}\n```"
                
        elif intent == "quantitative":
            lines = text.split("\n")
            formatted_lines = []
            for line in lines:
                if len(re.findall(r'\b\d+(?:\.\d+)?\b', line)) >= 2:
                    formatted_lines.append(f"| {line.replace('|', '').strip()} |")
                else:
                    formatted_lines.append(line)
            text = "\n".join(formatted_lines)
            
        return f"{header}\n{text}"
