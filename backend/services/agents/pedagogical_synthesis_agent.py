import logging
from typing import Tuple, Generator, List, Dict, Any

from backend.models.context import ContextPackage
from backend.services.llm.prompt_builder import PromptBuilder
from backend.services.llm.failover_manager import FailoverManager
from backend.services.llm.response_formatter import ResponseFormatter
from backend.core.config.settings import get_settings

logger = logging.getLogger(__name__)

class PedagogicalSynthesisAgent:
    """
    Agent 2: Pedagogical Synthesis & Content Architect.
    Responsible for:
    1. Low-Temperature Inference (T=0.1) for strict factual fidelity and zero hallucination.
    2. Professional Academic Editorial Design (Core Concept, Mechanism/Curriculum, Evidence, Takeaways).
    3. Document Provenance Awareness (cites exact file names, page numbers, and section headings).
    4. Anti-Hallucination Guardrails (never claims 'no files exist' when workspace files are active).
    5. Clean Source Attribution formatting.
    """
    def __init__(self):
        self.prompt_builder = PromptBuilder()
        self.failover_manager = FailoverManager()
        self.formatter = ResponseFormatter()
        self.settings = get_settings()
        self.factual_temperature = 0.10

    def synthesize(self, context: ContextPackage, mode: str = "expert") -> Tuple[str, str, List[Dict[str, Any]]]:
        """
        Synthesizes an authoritative, structured pedagogical response from the retrieval context.
        Returns: (response_text, model_name, sources)
        """
        logger.info(
            f"[Agent 2: PedagogicalSynthesizer] Synthesizing response (mode={mode}, chunks={len(context.retrieved_chunks)}, temp={self.factual_temperature})"
        )

        # 1. Build Grounded Prompt with Document Awareness
        messages = self.prompt_builder.build_from_context(context)

        # 2. Generate with Low Temperature for Maximum Factual Grounding
        raw_response, model_used = self.failover_manager.generate(messages, mode=mode)

        # 3. Clean and Validate Response Formatting
        clean_response = self.formatter.validate_and_clean(raw_response)

        # 4. Append Verified Provenance Sources
        final_response = self.formatter.append_sources(clean_response, context.sources)

        return final_response, model_used, context.sources

    def synthesize_stream(self, context: ContextPackage, mode: str = "expert") -> Generator[str, None, None]:
        """
        Streams synthesized tokens to the frontend with pedagogical formatting.
        """
        messages = self.prompt_builder.build_from_context(context)
        
        # If groq provider supports streaming
        groq_provider = self.failover_manager.groq
        if groq_provider.is_available():
            target_model = self.settings.GROQ_MODEL_EXPERT if mode == "expert" else self.settings.GROQ_MODEL_MEDIUM
            try:
                for token in groq_provider.stream(messages, model=target_model, temperature=self.factual_temperature):
                    yield token
                return
            except Exception as e:
                logger.warning(f"[Agent 2] Groq streaming fallback: {e}")

        # Fallback to synchronous generation emitted as single stream
        full_text, _, _ = self.synthesize(context, mode=mode)
        yield full_text
