"""
TokenBudgetManager — pure-logic token accounting and allocation.

SOLID:
  - S: Only counts and allocates tokens. No I/O, no DB, no LLM calls.
  - O: Budget tables are configurable constants — swappable without touching logic.

Uses a simple word-based approximation (1 token ≈ 0.75 words) to avoid
adding the `tiktoken` dependency. Accuracy is sufficient for budget enforcement
(within ±10%). If high precision is needed, swap _count_tokens() to use tiktoken.
"""
import logging

logger = logging.getLogger(__name__)

# Tokens per prompt section per mode
BUDGETS: dict[str, dict[str, int]] = {
    "expert": {
        "system":   1200,
        "memory":   600,
        "evidence": 2000,
        "history":  800,
    },
    "medium": {
        "system":   800,
        "memory":   400,
        "evidence": 1500,
        "history":  600,
    },
    "simple": {
        "system":   400,
        "memory":   200,
        "evidence": 700,
        "history":  300,
    },
}


class TokenBudgetManager:

    def get_budget(self, mode: str) -> dict[str, int]:
        return BUDGETS.get(mode, BUDGETS["medium"])

    def count_tokens(self, text: str) -> int:
        """Approximate token count: 1 token ≈ 0.75 words (GPT-family heuristic)."""
        if not text:
            return 0
        words = len(text.split())
        return max(1, int(words / 0.75))

    def allocate_history(
        self, messages: list[dict], budget: int
    ) -> list[dict]:
        """
        Priority-trim conversation history to fit within the token budget.

        Retention priority (highest to lowest):
          1. Messages with importance_score > 0.8
          2. The last 2 user–assistant turn pairs (immediate coherence)
          3. Remaining messages newest-first until budget exhausted

        Always returns messages in chronological order.
        """
        if not messages or budget <= 0:
            return []

        # Separate high-importance messages
        high_importance = [
            m for m in messages
            if float(m.get("importance_score", 0.5)) > 0.8
        ]
        # Always keep last 2 full turns (4 messages: 2 user + 2 assistant)
        last_anchors = messages[-4:] if len(messages) >= 4 else messages[:]
        anchored_ids = {id(m) for m in high_importance + last_anchors}

        anchored = [m for m in messages if id(m) in anchored_ids]
        remaining = [m for m in reversed(messages) if id(m) not in anchored_ids]

        selected: list[dict] = []
        used_tokens = 0

        # Fill anchored messages first
        for msg in anchored:
            t = self.count_tokens(msg.get("message", ""))
            if used_tokens + t <= budget:
                selected.append(msg)
                used_tokens += t

        # Fill remaining newest-first
        for msg in remaining:
            t = self.count_tokens(msg.get("message", ""))
            if used_tokens + t <= budget:
                selected.append(msg)
                used_tokens += t
            else:
                break

        # Re-sort chronologically
        msg_order = {id(m): i for i, m in enumerate(messages)}
        selected.sort(key=lambda m: msg_order.get(id(m), 0))

        logger.debug(
            f"TokenBudgetManager: history trimmed to {len(selected)}/{len(messages)} messages "
            f"({used_tokens}/{budget} tokens used)"
        )
        return selected

    def allocate_evidence(self, chunks: list, budget: int) -> list:
        """
        Trim retrieved chunks by score descending to fit within the token budget.
        If a top chunk exceeds remaining budget, it is gracefully truncated rather
        than discarded.
        """
        if not chunks or budget <= 0:
            return []

        sorted_chunks = sorted(
            chunks, key=lambda c: getattr(c, "score", 0.0), reverse=True
        )
        selected = []
        used = 0
        for chunk in sorted_chunks:
            text = getattr(chunk, "chunk_text", "") or ""
            t = self.count_tokens(text)
            if used + t <= budget:
                selected.append(chunk)
                used += t
            elif used < budget and (budget - used) >= 80:
                # Gracefully truncate chunk text to fit remaining token budget
                remaining_tokens = budget - used
                approx_words = max(10, int(remaining_tokens * 0.75))
                words = text.split()
                if len(words) > approx_words:
                    truncated_text = " ".join(words[:approx_words]) + "\n[... truncated to fit budget]"
                else:
                    truncated_text = text[:int(remaining_tokens * 3.5)] + "\n[... truncated to fit budget]"

                truncated_chunk = chunk.model_copy(update={"chunk_text": truncated_text}) if hasattr(chunk, "model_copy") else chunk
                selected.append(truncated_chunk)
                used = budget
                break
            else:
                break

        logger.debug(
            f"TokenBudgetManager: evidence allocated {len(selected)}/{len(chunks)} chunks "
            f"({used}/{budget} tokens used)"
        )
        return selected

    def estimate_total(self, *texts: str) -> int:
        return sum(self.count_tokens(t) for t in texts)
