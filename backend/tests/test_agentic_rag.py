import pytest
from backend.services.agents.retrieval_orchestrator_agent import RetrievalOrchestratorAgent
from backend.services.retrieval.cross_encoder_service import sigmoid
from backend.models.context import ContextPackage
from backend.models.chat import RetrievedChunk
from backend.services.retrieval.confidence_engine import ConfidenceResult
from backend.services.agents.pedagogical_synthesis_agent import PedagogicalSynthesisAgent

def test_sigmoid_calibration():
    # Test sigmoid converts negative logits smoothly into probabilities
    assert 0.0 < sigmoid(-10.0) < 0.01
    assert sigmoid(0.0) == 0.5
    assert 0.99 < sigmoid(10.0) < 1.0
    # Test bounds handling
    assert sigmoid(-100.0) == 0.0
    assert sigmoid(100.0) == 1.0

def test_retrieval_orchestrator_query_normalization():
    agent = RetrievalOrchestratorAgent()
    query = "In the uploaded documents, list all the lession names, I tihnk it has upto 12 of them!"
    normalized = agent._normalize_query(query)
    assert "lesson" in normalized
    assert "lession" not in normalized

def test_retrieval_orchestrator_intent_classification():
    agent = RetrievalOrchestratorAgent()
    
    assert agent._classify_intent("list all the lessons in this textbook") == "STRUCTURAL_OVERVIEW"
    assert agent._classify_intent("what are the chapters in unit 1?") == "STRUCTURAL_OVERVIEW"
    assert agent._classify_intent("table of contents overview") == "STRUCTURAL_OVERVIEW"
    assert agent._classify_intent("mitosis vs meiosis difference") == "COMPARATIVE"
    assert agent._classify_intent("explain the mechanism of transcription") == "CONCEPTUAL"
    assert agent._classify_intent("what is a zygote?") == "FACTOID"

def test_pedagogical_synthesis_structure():
    synthesis_agent = PedagogicalSynthesisAgent()
    assert synthesis_agent.factual_temperature == 0.10
    
    chunk = RetrievedChunk(
        chunk_id="test-chunk-1",
        document_id="test-doc-1",
        source_file="TN-Std12-Zoology-EM.pdf",
        chunk_text="CONTENTS\nUNIT I\nChapter 1 Reproduction in Organisms 1\nChapter 2 Human Reproduction 13",
        score=0.98,
        page_number=1,
        section_heading="Table of Contents"
    )
    
    ctx = ContextPackage(
        workspace_id="test-ws",
        workspace_name="Biology Workspace",
        query="List all lesson names",
        retrieved_chunks=[chunk],
        confidence=ConfidenceResult(level="HIGH", sufficient=True, chunk_count=1, message="Strong match"),
        sources=[],
        workspace_summary="Uploaded Workspace Files:\n- TN-Std12-Zoology-EM.pdf (100 chunks)",
        recent_messages=[],
        mode="expert"
    )
    
    messages = synthesis_agent.prompt_builder.build_from_context(ctx)
    system_content = next(m["content"] for m in messages if m["role"] == "system")
    
    # Assert anti-hallucination and curriculum instructions are present
    assert "TN-Std12-Zoology-EM.pdf" in system_content
    assert "Zero-Hallucination Mandate" in system_content
    assert "Lesson / Curriculum Requests" in system_content
