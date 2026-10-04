import math
from typing import List, Tuple
from backend.core.config.settings import get_settings
from backend.models.chat import RetrievedChunk
from backend.providers.embeddings.cross_encoder_provider import get_cross_encoder_provider
from backend.repositories.sqlite.chunk_repository import ChunkRepository
from backend.repositories.sqlite.document_repository import DocumentRepository

def sigmoid(score: float) -> float:
    """Calibrate unbounded raw cross-encoder logits into [0, 1] probability range."""
    try:
        if score > 20:
            return 1.0
        elif score < -20:
            return 0.0
        return 1.0 / (1.0 + math.exp(-float(score)))
    except OverflowError:
        return 0.0 if score < 0 else 1.0

class CrossEncoderService:
    def __init__(self):
        self.provider = get_cross_encoder_provider()
        self.chunk_repo = ChunkRepository()
        self.doc_repo = DocumentRepository()
        self.min_score = get_settings().CROSS_ENCODER_MIN_SCORE
        
    def rerank(self, query: str, candidates: List[Tuple[str, float]], top_n: int = 5) -> List[RetrievedChunk]:
        if not candidates:
            return []
            
        chunk_ids = [c[0] for c in candidates]
        chunks_data = self.chunk_repo.get_chunks_by_ids(chunk_ids)
        
        # Build dict for quick lookup
        chunk_dict = {c["chunk_id"]: c for c in chunks_data}

        # Visual RAG: Also fetch figure chunks in candidates
        missing_ids = [cid for cid in chunk_ids if cid not in chunk_dict]
        if missing_ids:
            try:
                from backend.repositories.sqlite.figure_repository import FigureRepository
                fig_repo = FigureRepository()
                figs_data = fig_repo.get_figures_by_ids(missing_ids)
                for fig in figs_data:
                    caption = fig.get("caption_text") or fig.get("context_text") or "Figure"
                    chunk_dict[fig["figure_id"]] = {
                        "chunk_id": fig["figure_id"],
                        "document_id": fig["document_id"],
                        "chunk_text": f"[Figure p.{fig.get('page_number', 1)}] {caption}",
                        "page_number": fig.get("page_number", 1),
                        "section_heading": f"Figure {fig.get('figure_type', '')}",
                    }
            except Exception:
                pass
        
        texts_to_score = []
        valid_candidates = []
        for chunk_id, _ in candidates:
            if chunk_id in chunk_dict:
                texts_to_score.append(chunk_dict[chunk_id]["chunk_text"])
                valid_candidates.append(chunk_id)
                
        if not texts_to_score:
            return []
            
        # Get raw logits from cross-encoder model
        raw_scores = self.provider.predict(query, texts_to_score)
        
        # Convert logits to calibrated probabilities via sigmoid
        scored_chunks = []
        for chunk_id, raw_score in zip(valid_candidates, raw_scores):
            calibrated_score = sigmoid(raw_score)
            scored_chunks.append((chunk_id, calibrated_score))
                
        # Sort descending by calibrated score
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        scored_chunks = scored_chunks[:top_n]
        
        # Build RetrievedChunk objects
        results = []
        doc_cache = {}
        for chunk_id, score in scored_chunks:
            chunk_data = chunk_dict[chunk_id]
            doc_id = chunk_data["document_id"]
            if doc_id not in doc_cache:
                doc = self.doc_repo.get_document(doc_id)
                doc_cache[doc_id] = doc["file_name"] if doc else "Unknown"
                
            results.append(
                RetrievedChunk(
                    chunk_id=chunk_id,
                    document_id=doc_id,
                    source_file=doc_cache[doc_id],
                    chunk_text=chunk_data["chunk_text"],
                    score=float(score),
                    page_number=chunk_data.get("page_number"),
                    section_heading=chunk_data.get("section_heading")
                )
            )
            
        return results
