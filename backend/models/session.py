"""
Pydantic domain models for Conversational Intelligence and Session Management:
  - ConversationSession: a named conversation thread within a workspace
  - UserMemoryProfile:   persistent per-workspace behavioural profile
  - ConversationMemoryPackage: assembled memory bundle passed to ContextBuilder
"""
from __future__ import annotations

import json
from typing import Literal
from pydantic import BaseModel, field_validator


class ConversationSession(BaseModel):
    """A named conversation thread scoped to a workspace."""
    session_id: str
    workspace_id: str
    session_name: str
    created_at: str
    updated_at: str
    message_count: int = 0
    is_active: bool = True


class UserMemoryProfile(BaseModel):
    """
    Persistent learning profile for a user within a workspace.
    Survives across all conversation sessions.
    """
    workspace_id: str
    preferred_mode: Literal["simple", "medium", "expert"] = "medium"
    topic_familiarity: dict[str, float] = {}
    learning_style: Literal["visual", "analytical", "narrative", "balanced"] = "balanced"
    struggle_topics: list[str] = []
    session_count: int = 0
    last_active: str = ""

    @field_validator("topic_familiarity", mode="before")
    @classmethod
    def parse_topic_familiarity(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return {}
        return v or {}

    @field_validator("struggle_topics", mode="before")
    @classmethod
    def parse_struggle_topics(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return []
        return v or []

    def build_context_snippet(self) -> str:
        """
        Returns a compact, human-readable profile summary for LLM prompt injection.
        Capped at ~150 tokens to stay within budget allocation.
        """
        parts: list[str] = []

        if self.preferred_mode == "expert":
            parts.append("Preferred depth: Expert (detailed, rigorous explanations).")
        elif self.preferred_mode == "simple":
            parts.append("Preferred depth: Simple (direct, foundational explanations).")
        else:
            parts.append("Preferred depth: Medium (clear, structured explanations).")

        if self.learning_style != "balanced":
            style_map = {
                "visual": "prefers diagrams, tables, and visual breakdowns",
                "analytical": "prefers step-by-step logical analysis",
                "narrative": "prefers storytelling and real-world examples",
            }
            parts.append(f"Learning style: {style_map.get(self.learning_style, '')}.")

        if self.topic_familiarity:
            topics_list = list(self.topic_familiarity.keys())[:5]
            parts.append(f"Active topics studied: {', '.join(topics_list)}.")
            strong = [t for t, s in self.topic_familiarity.items() if s >= 0.6]
            if strong:
                parts.append(f"Familiar concepts: {', '.join(strong[:3])}.")

        if self.struggle_topics:
            top_struggles = self.struggle_topics[:3]
            parts.append(f"Areas needing extra reinforcement: {', '.join(top_struggles)}.")

        if self.session_count > 0:
            parts.append(f"Session activity: {self.session_count} total interactions.")

        return " ".join(parts) if parts else ""


class ConversationMemoryPackage(BaseModel):
    """
    Assembled memory bundle passed from ConversationIntelligenceManager to ContextBuilder.
    Contains a session reference, token-budgeted history, profile snippet, and workspace summary.
    """
    session_id: str
    recent_messages: list[dict] = []
    profile_snippet: str = ""
    workspace_summary: str = ""
    total_tokens_estimated: int = 0
