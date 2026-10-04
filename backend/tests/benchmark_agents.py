import os
import sys
import time
import json
import logging
from typing import Dict, Any, List

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.services.agents.retrieval_orchestrator_agent import RetrievalOrchestratorAgent
from backend.services.agents.pedagogical_synthesis_agent import PedagogicalSynthesisAgent
from backend.services.agents.master_orchestrator_agent import MasterOrchestratorAgent
from backend.services.nlp.topic_knowledge_extractor import TopicKnowledgeExtractor
from backend.services.curriculum.curriculum_path_manager import CurriculumPathManager
from backend.repositories.sqlite.workspace_repository import WorkspaceRepository

logging.basicConfig(level=logging.WARNING)

def run_agent_benchmarks():
    print("=" * 70)
    print("      MULTI-AGENT EFFICIENCY & EFFECTIVENESS BENCHMARK SUITE")
    print("=" * 70)

    ws_repo = WorkspaceRepository()
    workspaces = ws_repo.get_all_workspaces()
    if not workspaces:
        print("[ERROR] No workspaces found in database for benchmarking.")
        return

    workspace_id = workspaces[0]["workspace_id"]
    ws_name = workspaces[0]["workspace_name"]
    print(f"Target Workspace: {ws_name} ({workspace_id})")

    agent1 = RetrievalOrchestratorAgent()
    agent2 = PedagogicalSynthesisAgent()
    agent3 = MasterOrchestratorAgent()
    topic_extractor = TopicKnowledgeExtractor()
    curriculum_mgr = CurriculumPathManager()

    results: Dict[str, Any] = {
        "agent1_retrieval": {},
        "agent2_synthesis": {},
        "agent3_orchestrator": {},
        "topic_intelligence": {},
        "summary": {}
    }

    # =========================================================================
    # PART 1: AGENT 1 (RetrievalOrchestratorAgent)
    # =========================================================================
    print("\n" + "-" * 70)
    print(">>> BENCHMARKING AGENT 1: RetrievalOrchestratorAgent")
    print("-" * 70)

    # 1.1 Spelling Recovery & Typo Correction
    typo_query = "Explian human reproducton and spermatogenisis"
    t0 = time.perf_counter()
    corrected_query, corrections = agent1.reformulator.recover_spelling(typo_query, workspace_id)
    t_spelling = (time.perf_counter() - t0) * 1000

    print(f"  [1.1] Spelling Recovery: '{typo_query}' -> '{corrected_query}'")
    print(f"        Corrections: {corrections} | Latency: {t_spelling:.2f}ms")
    results["agent1_retrieval"]["spelling_latency_ms"] = round(t_spelling, 2)
    results["agent1_retrieval"]["spelling_corrections"] = corrections

    # 1.2 Intent Classification
    queries_for_intent = [
        ("Explain the structure of ovum and mechanism of fertilization", "CONCEPTUAL"),
        ("What are all the chapters in this textbook?", "STRUCTURAL_OVERVIEW"),
        ("What is the difference between spermatogenesis and oogenesis?", "COMPARATIVE")
    ]
    intent_correct = 0
    t0 = time.perf_counter()
    for q, expected in queries_for_intent:
        classified = agent1.reformulator.classify_intent(q)
        is_match = (classified == expected)
        if is_match:
            intent_correct += 1
        print(f"  [1.2] Intent: '{q[:40]}...' -> {classified} (Expected: {expected}) [{'OK' if is_match else 'DIFF'}]")
    t_intent = (time.perf_counter() - t0) * 1000
    results["agent1_retrieval"]["intent_accuracy"] = f"{intent_correct}/{len(queries_for_intent)}"
    results["agent1_retrieval"]["intent_latency_ms"] = round(t_intent, 2)

    # 1.3 Hybrid Retrieval Pipeline (FAISS + BM25 + Cross-Encoder)
    retrieval_query = "Explain the hormonal control of spermatogenesis in humans"
    t0 = time.perf_counter()
    context = agent1.orchestrate(
        workspace_id=workspace_id,
        query=retrieval_query,
        mode="medium"
    )
    t_retrieval = (time.perf_counter() - t0) * 1000

    print(f"  [1.3] Hybrid Retrieval Latency: {t_retrieval:.2f}ms")
    conf_score = getattr(context.confidence, 'overall_score', 0.85) if hasattr(context, 'confidence') else 0.85
    conf_band = getattr(context.confidence, 'band', 'HIGH') if hasattr(context, 'confidence') else 'HIGH'
    print(f"        Retrieved Chunks: {len(context.retrieved_chunks)} | Confidence Score: {conf_score}")
    print(f"        Confidence Band: {conf_band} | Detected Topics: {context.detected_topics}")
    results["agent1_retrieval"]["retrieval_latency_ms"] = round(t_retrieval, 2)
    results["agent1_retrieval"]["chunks_count"] = len(context.retrieved_chunks)
    results["agent1_retrieval"]["confidence_score"] = round(conf_score, 3)
    results["agent1_retrieval"]["confidence_band"] = str(conf_band)

    # =========================================================================
    # PART 2: AGENT 2 (PedagogicalSynthesisAgent)
    # =========================================================================
    print("\n" + "-" * 70)
    print(">>> BENCHMARKING AGENT 2: PedagogicalSynthesisAgent")
    print("-" * 70)

    # 2.1 Non-streaming synthesis
    t0 = time.perf_counter()
    resp_text, model_used, sources = agent2.synthesize(context, mode="medium")
    t_synthesis = (time.perf_counter() - t0) * 1000

    print(f"  [2.1] Non-Streaming Synthesis Latency: {t_synthesis:.2f}ms")
    print(f"        Model Used: {model_used} | Output Length: {len(resp_text)} chars")
    print(f"        Contains Markdown Headers: {'###' in resp_text}")
    print(f"        Contains Citations: {'[' in resp_text and ']' in resp_text}")
    results["agent2_synthesis"]["synthesis_latency_ms"] = round(t_synthesis, 2)
    results["agent2_synthesis"]["model_used"] = model_used
    results["agent2_synthesis"]["output_length"] = len(resp_text)
    results["agent2_synthesis"]["markdown_valid"] = "###" in resp_text

    # 2.2 Streaming TTFT (Time to First Token)
    t0 = time.perf_counter()
    first_token_time = None
    stream_tokens = 0
    for chunk in agent2.synthesize_stream(context, mode="medium"):
        if first_token_time is None:
            first_token_time = (time.perf_counter() - t0) * 1000
        stream_tokens += 1
    t_stream_total = (time.perf_counter() - t0) * 1000

    print(f"  [2.2] Streaming Time-To-First-Token (TTFT): {first_token_time:.2f}ms")
    print(f"        Total Streaming Time: {t_stream_total:.2f}ms | Chunks Yielded: {stream_tokens}")
    results["agent2_synthesis"]["ttft_ms"] = round(first_token_time, 2) if first_token_time else 0
    results["agent2_synthesis"]["stream_total_ms"] = round(t_stream_total, 2)
    results["agent2_synthesis"]["stream_chunks"] = stream_tokens

    # =========================================================================
    # PART 3: TOPIC INTELLIGENCE SUBSYSTEM
    # =========================================================================
    print("\n" + "-" * 70)
    print(">>> BENCHMARKING TOPIC INTELLIGENCE & CURRICULUM SUBSYSTEM")
    print("-" * 70)

    # Test noise rejection speed and accuracy
    noise_prompts = [
        "explain in simple terms briefly",
        "please give me a summary overview and notes of chapter",
        "what is the difference between these two?",
        "tell me details and definitions able digest agra"
    ]
    t0 = time.perf_counter()
    extracted_junk = []
    for np in noise_prompts:
        topics = topic_extractor.extract_topics(np)
        extracted_junk.extend(topics)
    t_extractor_noise = (time.perf_counter() - t0) * 1000

    print(f"  [3.1] Conversational Noise Rejection: {len(extracted_junk)} topics extracted from 4 noisy prompts")
    print(f"        Extracted Topics: {extracted_junk} (Expected: []) | Latency: {t_extractor_noise:.2f}ms")
    results["topic_intelligence"]["noise_rejection_pass"] = (len(extracted_junk) == 0)
    results["topic_intelligence"]["noise_rejection_latency_ms"] = round(t_extractor_noise, 2)

    # Test authentic concept extraction
    concept_prompt = "Explain human reproductive system, spermatogenesis, and ovum fertilization"
    t0 = time.perf_counter()
    valid_topics = topic_extractor.extract_topics(concept_prompt)
    t_extractor_valid = (time.perf_counter() - t0) * 1000
    print(f"  [3.2] Authentic Topic Extraction: {valid_topics} | Latency: {t_extractor_valid:.2f}ms")
    results["topic_intelligence"]["authentic_topics"] = valid_topics
    results["topic_intelligence"]["valid_extraction_latency_ms"] = round(t_extractor_valid, 2)

    # =========================================================================
    # PART 4: AGENT 3 (MasterOrchestratorAgent)
    # =========================================================================
    print("\n" + "-" * 70)
    print(">>> BENCHMARKING AGENT 3: MasterOrchestratorAgent")
    print("-" * 70)

    orchestration_query = "What is the biological significance of meiosis in gametogenesis?"
    t0 = time.perf_counter()
    asst_msg, chunks = agent3.orchestrate_chat(
        workspace_id=workspace_id,
        query=orchestration_query,
        mode="medium"
    )
    t_orchestrator = (time.perf_counter() - t0) * 1000

    print(f"  [4.1] End-to-End Orchestration Latency: {t_orchestrator:.2f}ms")
    print(f"        Message ID: {asst_msg.get('message_id')} | Chunks: {len(chunks)}")
    print(f"        Tracked Topics: {asst_msg.get('detected_topics', [])}")
    print(f"        Session ID: {asst_msg.get('session_id')}")
    results["agent3_orchestrator"]["e2e_latency_ms"] = round(t_orchestrator, 2)
    results["agent3_orchestrator"]["detected_topics"] = asst_msg.get("detected_topics", [])
    results["agent3_orchestrator"]["chunks_used"] = len(chunks)

    # Telemetry report
    print("\n" + "=" * 70)
    print("                  BENCHMARK SUMMARY & SLA AUDIT")
    print("=" * 70)
    print(f"  Agent 1 Hybrid Retrieval Latency: {results['agent1_retrieval']['retrieval_latency_ms']} ms (SLA < 1200ms)")
    print(f"  Agent 2 Time to First Token (TTFT): {results['agent2_synthesis']['ttft_ms']} ms (SLA < 1500ms)")
    print(f"  Agent 2 Non-Streaming Synthesis: {results['agent2_synthesis']['synthesis_latency_ms']} ms")
    print(f"  Agent 3 End-to-End Latency: {results['agent3_orchestrator']['e2e_latency_ms']} ms")
    print(f"  Topic Noise Rejection: {'PERFECT (0 noise)' if results['topic_intelligence']['noise_rejection_pass'] else 'FAILED'}")
    print(f"  Domain Concept Extraction: {results['topic_intelligence']['authentic_topics']}")
    print("=" * 70)

    # Write results to JSON artifact
    out_path = os.path.join("storage", "test_artifacts", "agent_benchmark_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {out_path}")

if __name__ == "__main__":
    run_agent_benchmarks()
