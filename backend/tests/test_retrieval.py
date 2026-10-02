import pytest
from backend.services.retrieval.rrf_engine import RRFEngine
from backend.services.retrieval.context_compressor import ContextCompressor
from backend.services.retrieval.confidence_engine import ConfidenceEngine
from backend.services.retrieval.source_attributor import SourceAttributor
from backend.models.chat import RetrievedChunk

def test_rrf_engine():
    rrf = RRFEngine()
    dense_results = [("c1", 0.9), ("c2", 0.8)]
    lexical_results = [("c2", 12.5), ("c3", 8.0)]

    fused = rrf.fuse([dense_results, lexical_results], top_n=3)
    assert len(fused) <= 3
    chunk_ids = [c[0] for c in fused]
    # c2 appeared in both so it should be ranked high
    assert "c2" in chunk_ids

def test_context_compressor():
    compressor = ContextCompressor()
    chunks = [
        RetrievedChunk(chunk_id="c1", document_id="d1", source_file="rag.pdf", chunk_text="Machine learning models require clean training data.", score=0.9),
        RetrievedChunk(chunk_id="c2", document_id="d1", source_file="rag.pdf", chunk_text="Machine learning models require clean training data.", score=0.85), # Near identical duplicate
        RetrievedChunk(chunk_id="c3", document_id="d2", source_file="api.pdf", chunk_text="FastAPI provides high performance asynchronous REST endpoints.", score=0.7)
    ]

    deduped = compressor.compress(chunks)
    assert len(deduped) == 2
    assert {c.chunk_id for c in deduped} == {"c1", "c3"}

def test_confidence_engine():
    engine = ConfidenceEngine()
    high_score_chunks = [
        RetrievedChunk(chunk_id="c1", document_id="d1", source_file="rag.pdf", chunk_text="Sample content", score=0.85),
        RetrievedChunk(chunk_id="c2", document_id="d1", source_file="rag.pdf", chunk_text="Sample content 2", score=0.75)
    ]
    result = engine.evaluate(high_score_chunks)
    assert result.sufficient is True
    assert result.level in ["HIGH", "MEDIUM", "LOW"]
    assert result.chunk_count == 2

def test_source_attributor():
    attributor = SourceAttributor()
    chunks = [
        RetrievedChunk(chunk_id="c1", document_id="d1", source_file="paper1.pdf", chunk_text="Information retrieval methods", score=0.85),
        RetrievedChunk(chunk_id="c2", document_id="d1", source_file="paper1.pdf", chunk_text="Dense passage retrieval", score=0.80),
        RetrievedChunk(chunk_id="c3", document_id="d2", source_file="paper2.pdf", chunk_text="Vector similarity search", score=0.75)
    ]
    sources = attributor.extract_sources(chunks)
    assert len(sources) == 2
    assert any(s.file_name == "paper1.pdf" for s in sources)
    assert any(s.file_name == "paper2.pdf" for s in sources)
    formatted = attributor.format_sources_text(sources)
    assert "Sources:" in formatted
