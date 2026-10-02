import pytest
from backend.services.nlp.corpus_lexicon import CorpusLexicon
from backend.services.nlp.query_reformulator import QueryReformulatorPipeline
from backend.models.chat import RetrievedChunk

def test_corpus_lexicon_build():
    lexicon = CorpusLexicon()
    # Mocking chunk texts
    chunks = [
        {"chunk_text": "Environmental issues including air pollution, water contamination and global warming."},
        {"chunk_text": "Reproduction in organisms, gametogenesis, and fertilization mechanisms."}
    ]
    words = lexicon.extract_words_from_chunks(chunks)
    assert "environmental" in words
    assert "pollution" in words
    assert "reproduction" in words
    assert "fertilization" in words
    assert "mechanisms" in words
    # Short words or common punctuation stripped
    assert "in" not in words

def test_query_spelling_recovery_with_domain_vocabulary():
    reformulator = QueryReformulatorPipeline()
    # Inject a domain vocabulary into lexicon cache
    mock_workspace_id = "test-ws-nlp-1"
    reformulator.lexicon._cache[mock_workspace_id] = [
        "environmental", "issues", "prevention", "pollution", "biodiversity",
        "reproduction", "fertilization", "respiration", "greenhouse"
    ]
    
    # Test typo 'preventaion' -> 'prevention'
    query = "List all environmental issues and the preventaion to them?"
    canonical, corrections = reformulator.recover_spelling(query, mock_workspace_id)
    
    assert "prevention" in canonical
    assert "preventaion" not in canonical
    assert corrections.get("preventaion") == "prevention"
    assert "environmental" in canonical
    assert "issues" in canonical

def test_intent_classification_disambiguation():
    reformulator = QueryReformulatorPipeline()
    
    # 1. Structural TOC queries (Book outline / Syllabus)
    assert reformulator.classify_intent("list all the lessons in this textbook") == "STRUCTURAL_OVERVIEW"
    assert reformulator.classify_intent("what are the chapters in unit 1?") == "STRUCTURAL_OVERVIEW"
    assert reformulator.classify_intent("table of contents overview") == "STRUCTURAL_OVERVIEW"
    assert reformulator.classify_intent("how many chapters are in this book?") == "STRUCTURAL_OVERVIEW"
    
    # 2. Topical query that uses 'list all' - MUST NOT be classified as TOC outline!
    topical_intent = reformulator.classify_intent("List all environmental issues and the prevention to them?")
    assert topical_intent in ("CONCEPTUAL", "TOPICAL_CONCEPT")
    assert topical_intent != "STRUCTURAL_OVERVIEW"
    
    # 3. Comparative query
    assert reformulator.classify_intent("mitosis vs meiosis difference") == "COMPARATIVE"
    
    # 4. Mechanism / Explanation query
    assert reformulator.classify_intent("Explain contents in environmental issues of chapter 13") == "CONCEPTUAL"
    
    # 5. Factoid
    assert reformulator.classify_intent("what is a pollutant?") == "FACTOID"

def test_multi_query_generation():
    reformulator = QueryReformulatorPipeline()
    
    original = "List all environmental issues and the preventaion to them?"
    canonical = "List all environmental issues and the prevention to them?"
    
    queries = reformulator.generate_retrieval_queries(original, canonical)
    
    # Must include canonical
    assert canonical in queries
    # Must include original (for safety: 'never trust correction alone')
    assert original in queries
    # Must include stripped concept keywords
    concept_queries = [q for q in queries if "environmental" in q and "prevention" in q]
    assert len(concept_queries) >= 2

def test_adaptive_evidence_gap_detection():
    reformulator = QueryReformulatorPipeline()
    
    # Scenario A: User asks for Chapter 13 environmental issues, but retrieval only returned TOC Chunk (Page 1)
    toc_chunk = RetrievedChunk(
        chunk_id="chunk-toc-1",
        document_id="doc-1",
        source_file="TN-Std12-Zoology-EM.pdf",
        chunk_text="CONTENTS\nUNIT V\nChapter 13 Environmental Issues ... 235",
        score=0.85,
        page_number=1,
        section_heading="Table of Contents"
    )
    
    has_gap, suggested_query = reformulator.detect_evidence_gap(
        "List all environmental issues and the prevention to them?", 
        [toc_chunk]
    )
    assert has_gap is True
    assert suggested_query is not None
    assert "environmental issues" in suggested_query.lower()
    
    # Scenario B: Retrieval contains substantive body chunk (Page 237)
    body_chunk = RetrievedChunk(
        chunk_id="chunk-body-1",
        document_id="doc-1",
        source_file="TN-Std12-Zoology-EM.pdf",
        chunk_text="Pollution is any undesirable change in physical, chemical, or biological characteristics of the environment. Air pollution causes respiratory disorders...",
        score=0.92,
        page_number=237,
        section_heading="13.1 Air Pollution"
    )
    
    has_gap_b, _ = reformulator.detect_evidence_gap(
        "List all environmental issues and the prevention to them?", 
        [toc_chunk, body_chunk]
    )
    assert has_gap_b is False
