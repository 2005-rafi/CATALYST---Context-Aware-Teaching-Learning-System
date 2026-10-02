from typing import List, Tuple
from backend.core.config.settings import get_settings
from backend.models.chat import RetrievedChunk
from backend.providers.embeddings.cross_encoder_provider import get_cross_encoder_provider
from backend.repositories.sqlite.chunk_repository import ChunkRepository
from backend.repositories.sqlite.document_repository import DocumentRepository

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
        
        texts_to_score = []
        valid_candidates = []
        for chunk_id, _ in candidates:
            if chunk_id in chunk_dict:
                texts_to_score.append(chunk_dict[chunk_id]["chunk_text"])
                valid_candidates.append(chunk_id)
                
        if not texts_to_score:
            return []
            
        # Get scores
        scores = self.provider.predict(query, texts_to_score)
        
        # Zip and filter
        scored_chunks = []
        for chunk_id, score in zip(valid_candidates, scores):
            if score >= self.min_score:
                scored_chunks.append((chunk_id, score))
                
        # Sort descending
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
