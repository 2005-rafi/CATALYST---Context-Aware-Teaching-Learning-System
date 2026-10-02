from dataclasses import dataclass
from typing import List
from backend.models.chat import RetrievedChunk

@dataclass
class SourceDocument:
    document_id: str
    file_name: str
    chunk_count: int

class SourceAttributor:
    def extract_sources(self, chunks: List[RetrievedChunk]) -> List[SourceDocument]:
        doc_counts = {}
        doc_names = {}
        
        for chunk in chunks:
            doc_id = chunk.document_id
            if doc_id not in doc_counts:
                doc_counts[doc_id] = 0
                doc_names[doc_id] = chunk.source_file
            doc_counts[doc_id] += 1
            
        sources = [
            SourceDocument(document_id=doc_id, file_name=doc_names[doc_id], chunk_count=count)
            for doc_id, count in doc_counts.items()
        ]
        
        sources.sort(key=lambda x: x.chunk_count, reverse=True)
        return sources
        
    def format_sources_text(self, sources: List[SourceDocument]) -> str:
        if not sources:
            return ""
            
        source_strings = []
        for i, src in enumerate(sources):
            chunk_word = "chunk" if src.chunk_count == 1 else "chunks"
            source_strings.append(f"[{i+1}] {src.file_name} ({src.chunk_count} {chunk_word})")
            
        return "Sources: " + ", ".join(source_strings)
