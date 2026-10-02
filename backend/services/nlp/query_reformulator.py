import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from rapidfuzz import process, fuzz

from backend.services.nlp.corpus_lexicon import CorpusLexicon

logger = logging.getLogger(__name__)

COMMON_ENGLISH_WORDS = {
    "the", "and", "that", "have", "for", "not", "with", "you", "this", "but", "his", "from", 
    "they", "say", "her", "she", "will", "one", "all", "would", "there", "their", "what", 
    "out", "about", "who", "get", "which", "when", "make", "can", "like", "time", "just", 
    "him", "know", "take", "people", "into", "year", "your", "good", "some", "could", "them", 
    "see", "other", "than", "then", "now", "look", "only", "come", "its", "over", "think", 
    "also", "back", "after", "use", "two", "how", "our", "work", "first", "well", "way", 
    "even", "new", "want", "because", "any", "these", "give", "day", "most", "us", "are", 
    "list", "tell", "explain", "does", "why", "many", "more", "very", "much", "each", "show",
    "uploaded", "upload", "documents", "document", "files", "file", "book", "textbook", "pdf", 
    "page", "pages", "chapter", "chapters", "lesson", "lessons", "names", "name", "content", 
    "contents", "table", "topics", "topic", "subject", "subjects", "text", "unit", "units",
    "them", "please", "upto", "down", "find", "read", "written", "given", "following"
}

class QueryReformulatorPipeline:
    """
    Advanced Query Understanding & NLP Reformulation Engine.
    Implements the full architecture from docs/plan.md:
    1. Corpus-Aware Spelling Recovery (via RapidFuzz against indexed document vocabulary)
    2. Multi-Query Formulation ("Never trust correction alone - search original + canonical")
    3. Disambiguated Intent Classification (Distinguishing Book Structure vs Topic Queries)
    4. Adaptive Evidence Verification & Gap Detection
    """
    def __init__(self):
        self.lexicon = CorpusLexicon()

    def process_query(self, query: str, workspace_id: str) -> Dict[str, Any]:
        """
        Executes full NLP normalization, spelling recovery, intent classification,
        and multi-query formulation.
        """
        # 1. Text Normalization
        clean_query = self._normalize_whitespace(query)

        # 2. Corpus-Aware Spelling Recovery
        canonical_query, corrections = self.recover_spelling(clean_query, workspace_id)
        if corrections:
            logger.info(f"[QueryReformulator] Recovered spelling: {corrections}")

        # 3. Disambiguated Intent Classification
        intent = self.classify_intent(canonical_query)
        logger.info(f"[QueryReformulator] Classified Intent: {intent}")

        # 4. Multi-Query Formulation
        retrieval_queries = self.generate_retrieval_queries(clean_query, canonical_query)

        return {
            "original_query": clean_query,
            "canonical_query": canonical_query,
            "corrections": corrections,
            "intent": intent,
            "retrieval_queries": retrieval_queries
        }

    def recover_spelling(self, query: str, workspace_id: str) -> Tuple[str, Dict[str, str]]:
        """
        Recovers spelling and technical terms against the uploaded document's domain vocabulary.
        Uses RapidFuzz with a high confidence threshold (>= 84%) to prevent over-correction.
        """
        vocab = self.lexicon.get_domain_vocabulary(workspace_id)
        if not vocab:
            return query, {}

        vocab_set = set(vocab)
        tokens = re.findall(r'[a-zA-Z0-9]+|[^\w\s]', query)
        corrections = {}
        reconstructed_tokens = []

        for token in tokens:
            lower_token = token.lower()
            # If word is number, punctuation, common English word, or already exact in vocab, keep it
            if token.isdigit() or not token.isalpha() or lower_token in COMMON_ENGLISH_WORDS or lower_token in vocab_set:
                reconstructed_tokens.append(token)
                continue

            # Look up closest match in domain vocabulary
            match = process.extractOne(lower_token, vocab, scorer=fuzz.ratio)
            if match:
                best_match, score, _ = match
                # Only correct if similarity >= 84% and token length >= 4
                if score >= 84 and len(lower_token) >= 4:
                    # Match casing of original
                    corrected_word = best_match.capitalize() if token[0].isupper() else best_match
                    corrections[token] = corrected_word
                    reconstructed_tokens.append(corrected_word)
                    continue

            reconstructed_tokens.append(token)

        # Reconstruct sentence respecting punctuation spacing
        corrected_text = ""
        for i, t in enumerate(reconstructed_tokens):
            if i > 0 and t.isalnum() and reconstructed_tokens[i-1].isalnum():
                corrected_text += " " + t
            elif i > 0 and t.isalnum() and reconstructed_tokens[i-1] not in "(['\"":
                corrected_text += " " + t
            else:
                corrected_text += t

        return corrected_text.strip(), corrections

    def classify_intent(self, query: str) -> str:
        """
        Strictly disambiguates between:
        - STRUCTURAL_OVERVIEW: Asking specifically for textbook syllabus/chapter list outline.
        - TOPICAL_CONCEPT: Inquiring about substantive subject matter (even if phrased 'list all...').
        - COMPARATIVE: Comparing two or more concepts.
        - QUANTITATIVE: Numerical / statistical questions.
        - CONCEPTUAL: Conceptual / Mechanism questions.
        - FACTOID: Specific definitions or facts.
        """
        q = query.lower()

        # 1. Check for Book Structure / Outline query (Strict TOC query)
        # Matches queries specifically asking for chapter list, lesson names, syllabus, or TOC
        toc_pattern = re.compile(
            r'\b(table\s+of\s+contents|syllabus|curriculum\s+outline|book\s+outline)\b|'
            r'(?:list|what\s+are|show|name|give)\s+(?:all\s+)?(?:the\s+)?(?:chapters|lessons|units|lesson\s+names|chapter\s+names)\b|'
            r'\bhow\s+many\s+(?:chapters|lessons|units)\b',
            re.IGNORECASE
        )
        if toc_pattern.search(q):
            # Ensure it is NOT a topical query that happens to mention a specific chapter
            # e.g. "list all environmental issues in chapter 13" is a TOPIC query, not a TOC list!
            if not re.search(r'\b(environmental|pollution|prevention|reproduction|genetics|evolution|microbes|biotechnology)\b', q):
                return "STRUCTURAL_OVERVIEW"

        # 2. Comparative query
        if any(kw in q for kw in [" vs ", " versus ", "difference between", "compare and contrast", "distinguish between"]):
            return "COMPARATIVE"

        # 3. Quantitative query
        if any(kw in q for kw in ["percentage", "formula", "ratio", "how many percent", "calculate", "proportion"]):
            return "QUANTITATIVE"

        # 4. Conceptual / Mechanism / Topical query
        if any(kw in q for kw in ["explain", "mechanism", "how does", "why does", "describe", "steps", "process", "issues", "prevention", "causes", "effects"]):
            return "CONCEPTUAL"

        # 5. Factoid / Definition query
        if re.search(r'\b(what\s+is|what\s+are|define|definition\s+of|meaning\s+of)\b', q):
            return "FACTOID"

        # Default for subject matter inquiries
        return "TOPICAL_CONCEPT"

    def generate_retrieval_queries(self, original_query: str, canonical_query: str) -> List[str]:
        """
        Implements Multi-Query Strategy: "Never trust correction alone".
        Generates original query, canonical query, and concept-extracted query.
        """
        queries = [canonical_query]
        if original_query.lower() != canonical_query.lower():
            queries.append(original_query)

        # Generate concept query by removing conversational scaffolding
        concept_terms = self._extract_concept_keywords(canonical_query)
        if concept_terms and concept_terms.lower() not in [q.lower() for q in queries]:
            queries.append(concept_terms)

        return queries

    def detect_evidence_gap(self, query: str, retrieved_chunks: List[Any]) -> Tuple[bool, Optional[str]]:
        """
        Checks if the user asked for substantive topical information (e.g. Chapter 13, environmental issues, prevention),
        but the retrieved context ONLY contains front-matter Table of Contents chunks (Page 1) without substantive body text.
        Returns: (has_gap, suggested_target_query)
        """
        if not retrieved_chunks:
            return True, query

        # Check if chunks are only TOC chunks
        only_toc = all(
            c.page_number in (1, 2, 3, None) or "CONTENTS" in c.chunk_text or "Table of Contents" in getattr(c, "section_heading", "")
            for c in retrieved_chunks
        )

        q_lower = query.lower()
        # If user asks about a specific topic (e.g. environmental issues, prevention, air pollution, genetics)
        # but only TOC chunks were retrieved, there is an evidence gap!
        topic_match = re.search(r'\b(chapter\s+\d+|environmental\s+issues|pollution|prevention|reproduction|genetics|evolution|health|disease|biotechnology)\b', q_lower)
        if only_toc and topic_match:
            matched_topic = topic_match.group(0)
            logger.warning(f"[QueryReformulator] Detected Evidence Gap: TOC returned for topic '{matched_topic}'")
            # Suggest a body-targeted search query
            target_query = f"{matched_topic} body mechanism details {query}"
            return True, target_query

        return False, None

    def _extract_concept_keywords(self, text: str) -> str:
        """Strips conversational noise and extracts domain keywords."""
        noise_patterns = [
            r'\bin\s+the\s+uploaded\s+documents?\b',
            r'\bfrom\s+the\s+uploaded\s+files?\b',
            r'\bcan\s+you\s+(?:please\s+)?(?:explain|tell|list|show)\b',
            r'\bplease\s+(?:explain|tell|list|show)\b',
            r'\bi\s+think\s+it\s+has\s+upto\s+\d+\s+of\s+them\b',
            r'\bi\s+want\s+to\s+know\b'
        ]
        clean = text
        for p in noise_patterns:
            clean = re.sub(p, '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'[^\w\s]', ' ', clean)
        tokens = [t for t in clean.split() if t.lower() not in COMMON_ENGLISH_WORDS]
        return " ".join(tokens).strip()

    def _normalize_whitespace(self, text: str) -> str:
        return re.sub(r'\s+', ' ', text).strip()
