import pytest
from backend.core.config.settings import get_settings
from backend.services.document.chunking.recursive_chunker import RecursiveChunker
from backend.services.document.chunking.token_counter import TokenCounter

def test_token_counter():
    counter = TokenCounter()
    text = "Hello world! This is a test sentence for token counting."
    tokens = counter.count(text)
    assert tokens > 0
    assert isinstance(tokens, int)

    truncated = counter.truncate(text, max_tokens=3)
    assert counter.count(truncated) <= 3

def test_recursive_chunker():
    settings = get_settings()
    chunker = RecursiveChunker(settings=settings)
    # Paragraph long enough to exceed CHUNK_MIN_SIZE (100 tokens)
    sample_text = (
        "Artificial intelligence and natural language processing have evolved rapidly over recent decades. "
        "Retrieval-Augmented Generation (RAG) is an architectural pattern that combines "
        "information retrieval systems with generative large language models to ground "
        "model responses in authoritative external knowledge bases and dynamic enterprise documents. "
        "By doing so, RAG significantly reduces hallucinations, increases reliability, and ensures that answers reflect current facts. "
        "In modern enterprise architectures, hybrid retrieval combining dense vector embeddings (such as FAISS) "
        "and sparse lexical search (such as BM25 via SQLite FTS5) provides substantial gains in precision and recall. "
        "Furthermore, cross-encoder reranking models like ms-marco-MiniLM evaluate the direct semantic relationship "
        "between the user prompt and individual candidate passages, ensuring the most accurate chunks are passed into the LLM context window."
    )
    chunks = chunker.chunk(sample_text)
    
    assert len(chunks) > 0
    for chunk in chunks:
        assert len(chunk.text) > 0
        assert chunk.token_count >= settings.CHUNK_MIN_SIZE
