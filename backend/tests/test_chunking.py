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

def test_chunk_repository_batch_insertion(tmp_path):
    from backend.repositories.sqlite.chunk_repository import ChunkRepository
    from backend.repositories.sqlite.workspace_repository import WorkspaceRepository
    from backend.repositories.sqlite.document_repository import DocumentRepository
    import uuid
    import datetime

    ws_repo = WorkspaceRepository()
    doc_repo = DocumentRepository()
    chunk_repo = ChunkRepository()

    ws_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    ws_repo.create_workspace(ws_id, f"Batch Test {ws_id[:8]}", "Testing", now, now)
    doc_repo.create_document(doc_id, ws_id, f"test_{doc_id[:8]}.pdf", "pdf", 0.05, now, "data/test.pdf")

    chunks_data = [
        (str(uuid.uuid4()), ws_id, doc_id, i, f"Chunk text sample number {i}", 20, now, 1, "Section 1")
        for i in range(5)
    ]

    chunk_repo.create_chunks_batch(chunks_data)
    saved_chunks = chunk_repo.get_chunks_by_document(doc_id)
    assert len(saved_chunks) == 5
    assert saved_chunks[0]["chunk_text"] == "Chunk text sample number 0"

    # Cleanup
    doc_repo.delete_document(doc_id)
    ws_repo.delete_workspace(ws_id)

