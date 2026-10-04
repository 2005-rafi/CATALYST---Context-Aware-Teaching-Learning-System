"""
FigureCaptioner — generates AI captions for extracted PDF figures using Groq Vision API.
Uses llama-3.2-11b-vision (free tier) with rate-limit guarding and graceful fallback.

Architecture: pure service layer — takes image bytes, returns structured description.
No DB/storage dependencies (SOLID SRP).
"""
import base64
import time
import logging
import re
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# Groq Vision models (free tier, ordered by preference)
_VISION_MODELS = [
    "llama-3.2-11b-vision-preview",
    "llama-3.2-90b-vision-preview",
]

# Rate limit guard: 2 seconds between requests on free tier
_REQUEST_INTERVAL_SECONDS = 2.5

# Token budget: keep responses concise to preserve free-tier quota
_MAX_CAPTION_TOKENS = 180

# System prompt: structured and deterministic to minimise output tokens
_SYSTEM_PROMPT = (
    "You are an educational document analyst. For the given image, provide a single JSON object "
    "with these exact keys: "
    '"type" (one of: diagram, chart, photo, equation, flowchart, table_image, illustration, other), '
    '"caption" (1-2 sentences describing what this figure shows and its educational significance), '
    '"entities" (up to 5 key terms visible or depicted). '
    "Respond with raw JSON only. No markdown fences."
)


class FigureCaptioner:
    """
    Groq Vision-based figure captioner with rate limiting and graceful degradation.
    Falls back to context-text-only description if the Vision API is unavailable.
    """

    def __init__(self, groq_api_key: str):
        self._api_key = groq_api_key
        self._last_request_time: float = 0.0
        self._client = None
        self._active_model: Optional[str] = None

        if groq_api_key:
            try:
                from groq import Groq
                self._client = Groq(api_key=groq_api_key)
                self._active_model = _VISION_MODELS[0]
                logger.info(f"[FigureCaptioner] Initialised with model: {self._active_model}")
            except Exception as e:
                logger.warning(f"[FigureCaptioner] Groq client init failed: {e}. Captioning disabled.")

    def caption(
        self,
        image_bytes: bytes,
        context_text: str = "",
        page_number: int = 0,
    ) -> Dict[str, str]:
        """
        Generates a structured caption for a figure image.

        Returns a dict:
          {
            "caption_text": str,   # human-readable description
            "figure_type": str,    # detected figure category
          }
        Falls back to context_text description if API unavailable.
        """
        if not self._client or not self._active_model:
            return self._fallback_caption(context_text)

        # Rate limit: ensure minimum interval between API calls
        self._enforce_rate_limit()

        try:
            b64_image = base64.b64encode(image_bytes).decode("utf-8")
            user_message = {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64_image}"},
                    },
                    {
                        "type": "text",
                        "text": (
                            f"Describe this educational figure from page {page_number}. "
                            f"Surrounding context: {context_text[:200] if context_text else 'None'}."
                        ),
                    },
                ],
            }

            response = self._client.chat.completions.create(
                model=self._active_model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    user_message,
                ],
                max_tokens=_MAX_CAPTION_TOKENS,
                temperature=0.1,
            )

            raw = response.choices[0].message.content.strip()
            return self._parse_response(raw, context_text)

        except Exception as e:
            err_str = str(e)
            logger.warning(f"[FigureCaptioner] Caption request failed (page {page_number}): {err_str}")

            # If rate limited, back off and retry once
            if "429" in err_str or "rate" in err_str.lower():
                logger.info("[FigureCaptioner] Rate limited. Backing off 10 seconds and retrying...")
                time.sleep(10)
                try:
                    response = self._client.chat.completions.create(
                        model=self._active_model,
                        messages=[
                            {"role": "system", "content": _SYSTEM_PROMPT},
                            user_message,
                        ],
                        max_tokens=_MAX_CAPTION_TOKENS,
                        temperature=0.1,
                    )
                    raw = response.choices[0].message.content.strip()
                    return self._parse_response(raw, context_text)
                except Exception as e2:
                    logger.error(f"[FigureCaptioner] Retry also failed: {e2}")

            return self._fallback_caption(context_text)

    def _enforce_rate_limit(self) -> None:
        """Ensures minimum interval between Groq API requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < _REQUEST_INTERVAL_SECONDS:
            time.sleep(_REQUEST_INTERVAL_SECONDS - elapsed)
        self._last_request_time = time.time()

    def _parse_response(self, raw: str, context_text: str) -> Dict[str, str]:
        """Parses JSON response from Groq Vision, with regex fallback."""
        import json

        # Strip markdown fences if model ignores the system prompt
        raw = re.sub(r"```(?:json)?", "", raw).strip().strip("`").strip()

        try:
            data = json.loads(raw)
            figure_type = str(data.get("type", "unknown")).lower()
            caption = str(data.get("caption", "")).strip()
            entities = data.get("entities", [])
            if entities:
                caption += f" Key elements: {', '.join(str(e) for e in entities[:5])}."

            # Validate type against known categories
            valid_types = {"diagram", "chart", "photo", "equation", "flowchart",
                           "table_image", "illustration", "other", "unknown"}
            if figure_type not in valid_types:
                figure_type = "other"

            return {
                "caption_text": caption or context_text[:200] or "Figure extracted from document.",
                "figure_type": figure_type,
            }
        except (json.JSONDecodeError, KeyError):
            # JSON parse failed — extract anything useful from raw text
            logger.debug(f"[FigureCaptioner] JSON parse failed, using raw: {raw[:100]}")
            return {
                "caption_text": raw[:300] if raw else (context_text[:200] or "Figure from document."),
                "figure_type": "unknown",
            }

    def _fallback_caption(self, context_text: str, page_number: int = 0) -> Dict[str, str]:
        """Uses LLM to deduce structured figure caption and type from surrounding context text."""
        if not context_text:
            return {"caption_text": f"Figure from page {page_number}.", "figure_type": "diagram"}

        if self._client:
            try:
                resp = self._client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {"role": "system", "content": (
                            "You are an educational document analyst. Based on the surrounding textbook text, "
                            "identify what the figure illustrates. Return JSON only with keys: "
                            '"type" (one of: diagram, chart, photo, equation, flowchart, illustration), '
                            '"caption" (1 sentence describing what the figure shows).'
                        )},
                        {"role": "user", "content": f"Text surrounding the figure on page {page_number}:\n{context_text[:500]}"}
                    ],
                    max_tokens=100,
                    temperature=0.1
                )
                raw = resp.choices[0].message.content.strip()
                return self._parse_response(raw, context_text)
            except Exception as e:
                logger.debug(f"[FigureCaptioner] LLM context captioning fallback failed: {e}")

        # Heuristic fallback
        fig_type = "diagram"
        low = context_text.lower()
        if "graph" in low or "chart" in low or "plot" in low:
            fig_type = "chart"
        elif "equation" in low or "formula" in low:
            fig_type = "equation"
        elif "flowchart" in low or "cycle" in low or "pathway" in low:
            fig_type = "flowchart"

        caption = context_text[:250].strip() or f"Figure from page {page_number}."
        return {"caption_text": caption, "figure_type": fig_type}

    @property
    def is_available(self) -> bool:
        return self._client is not None and bool(self._api_key)
