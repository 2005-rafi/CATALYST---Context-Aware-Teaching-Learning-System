"""
Advanced Multi-Agent Agentic RAG Subsystem.
Exposes:
- RetrievalOrchestratorAgent (Agent 1): Intent classification, structural TOC routing, hybrid retrieval & cross-encoder reranking.
- PedagogicalSynthesisAgent (Agent 2): Factual low-temperature pedagogical synthesis, formatting & citation grounding.
"""
from backend.services.agents.retrieval_orchestrator_agent import RetrievalOrchestratorAgent
from backend.services.agents.pedagogical_synthesis_agent import PedagogicalSynthesisAgent

__all__ = ["RetrievalOrchestratorAgent", "PedagogicalSynthesisAgent"]
