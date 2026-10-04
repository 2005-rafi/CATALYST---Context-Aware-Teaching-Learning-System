import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from rapidfuzz import process, fuzz

from backend.services.nlp.corpus_lexicon import CorpusLexicon

logger = logging.getLogger(__name__)

# Common English and educational stop words
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

# High-frequency student and educational typos
TYPO_DICT = {
    r'\bfo\b': 'of',
    r'\bchpater\b': 'chapter',
    r'\bchpaters\b': 'chapters',
    r'\bchaptr\b': 'chapter',
    r'\bchaptrs\b': 'chapters',
    r'\bcahtper\b': 'chapter',
    r'\blession\b': 'lesson',
    r'\blessions\b': 'lessons',
    r'\bfotosinthesis\b': 'photosynthesis',
    r'\bfotosynthesis\b': 'photosynthesis',
    r'\bspermatogenisis\b': 'spermatogenesis',
    r'\boogenesis\b': 'oogenesis',
    r'\bhormonel\b': 'hormonal',
    r'\btihnk\b': 'think',
    r'\bpreventaion\b': 'prevention',
    r'\benviroment\b': 'environment',
    r'\benviromental\b': 'environmental',
    r'\bpopulatoin\b': 'population',
    r'\breprodution\b': 'reproduction'
}

class QueryReformulatorPipeline:
    """
    Advanced Query Understanding & NLP Reformulation Engine.
    Implements:
    1. Universal Pre-Normalization & Corpus-Aware Spelling Recovery
    2. Disambiguated Intent Classification (TOC/Structural vs Conceptual vs Exam Prep)
    3. Multi-Query Formulation ("Never trust correction alone - search original + canonical + concepts")
    4. Adaptive Evidence Verification & Gap Detection
    """
    def __init__(self):
        self.lexicon = CorpusLexicon()

    def process_query(self, query: str, workspace_id: str) -> Dict[str, Any]:
        """
        Executes full NLP normalization, spelling recovery, intent classification,
        and multi-query formulation.
        """
        # 1. Text Normalization & Pre-typo replacement
        clean_query = self._normalize_whitespace(query)
        normalized_query = self._apply_pre_typo_fixes(clean_query)

        # 2. Corpus-Aware Spelling Recovery via RapidFuzz
        canonical_query, corrections = self.recover_spelling(normalized_query, workspace_id)
        if corrections:
            logger.info(f"[QueryReformulator] Recovered spelling: {corrections}")

        # 3. Disambiguated Intent Classification
        intent = self.classify_intent(canonical_query)
        logger.info(f"[QueryReformulator] Classified Intent: {intent}")

        # 4. Multi-Query Formulation
        retrieval_queries = self.generate_retrieval_queries(clean_query, canonical_query, intent)

        return {
            "original_query": clean_query,
            "canonical_query": canonical_query,
            "corrections": corrections,
            "intent": intent,
            "retrieval_queries": retrieval_queries
        }

    def _apply_pre_typo_fixes(self, text: str) -> str:
        res = text
        for pattern, replacement in TYPO_DICT.items():
            res = re.sub(pattern, replacement, res, flags=re.IGNORECASE)
        return res

    def recover_spelling(self, query: str, workspace_id: str) -> Tuple[str, Dict[str, str]]:
        """
        Recovers domain spelling against the uploaded document's vocabulary.
        Uses RapidFuzz with a high confidence threshold (>= 84%).
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
            if token.isdigit() or not token.isalpha() or lower_token in COMMON_ENGLISH_WORDS or lower_token in vocab_set:
                reconstructed_tokens.append(token)
                continue

            match = process.extractOne(lower_token, vocab, scorer=fuzz.ratio)
            if match:
                best_match, score, _ = match
                if score >= 84 and len(lower_token) >= 4:
                    corrected_word = best_match.capitalize() if token[0].isupper() else best_match
                    corrections[token] = corrected_word
                    reconstructed_tokens.append(corrected_word)
                    continue

            reconstructed_tokens.append(token)

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
        - USER_META_CONVERSATION: Queries about previous questions, chat history, user topics, learning progress.
        - STRUCTURAL_OVERVIEW: Asking for textbook syllabus/chapter list/TOC outline.
        - TOPICAL_CONCEPT: Inquiring about substantive subject matter.
        - COMPARATIVE: Comparing two or more concepts.
        - QUANTITATIVE: Numerical / statistical questions.
        - CONCEPTUAL: Conceptual / Mechanism questions.
        - FACTOID: Specific definitions or facts.
        """
        q = query.lower()

        # 0. Check for User Meta-Conversation / Learning Profile History queries
        meta_patterns = [
            r"\b(questions?|queries)\s+(i|we)\s+(have\s+)?(asked|sent|posed|discussed)\b",
            r"\b(list|show|what\s+are|tell|give)\s+(all\s+)?(the\s+)?(my|our)?\s*(past|previous|prior)?\s*(questions?|queries)\b",
            r"\bwhat\s+(have\s+)?(i|we)\s+(asked|studied|learned|covered|discussed)\b",
            r"\b(my|our)\s+(chat|conversation|learning|study)\s+history\b",
            r"\b(what\s+are\s+my|show\s+my|list\s+my)\s+(weak\s+areas?|struggles?|topics?|familiarity|progress)\b",
            r"\bwhat\s+topics\s+(have\s+i|did\s+i|have\s+we)\s+(studied|asked|covered)\b",
            r"\b(summarize|recap)\s+(my|our)\s+(session|conversations?|learning|questions?)\b"
        ]
        if any(re.search(p, q) for p in meta_patterns):
            return "USER_META_CONVERSATION"

        # 1. Check for Book Structure / Outline query (TOC / Syllabus / Chapter Listing)
        is_structure_query = False
        
        structure_keywords = [
            "table of contents", "syllabus", "curriculum", "book outline", 
            "list of chapters", "list of all chapters", "list all chapters", 
            "list chapters", "chapter list", "chapters list", "list of lessons", 
            "lesson list", "all the chapters", "all chapters", "list of all topics",
            "breakdown of components", "breakdown of chapters", "units and chapters"
        ]
        
        if any(kw in q for kw in structure_keywords):
            is_structure_query = True
        elif re.search(r'\b(list|show|give|what\s+are|name|tell)\b.*\b(all\s+)?(the\s+)?(chapters|lessons|units|lesson\s+names|chapter\s+names)\b', q):
            is_structure_query = True
        elif re.search(r'\bhow\s+many\s+(chapters|lessons|units)\b', q):
            is_structure_query = True

        if is_structure_query:
            # If user asks about a specific topical entity (e.g. "environmental issues in chapter 13"), keep it topical
            if not re.search(r'\b(environmental\s+issues|pollution|spermatogenesis|photosynthesis|microbes\s+in|biotechnology\s+applications|oogenesis|menstrual\s+cycle)\b', q):
                return "STRUCTURAL_OVERVIEW"

        # 2. Comparative query
        if any(kw in q for kw in [" vs ", " versus ", "difference between", "compare and contrast", "distinguish between"]):
            return "COMPARATIVE"

        # 3. Quantitative query
        if any(kw in q for kw in ["percentage", "formula", "ratio", "how many percent", "calculate", "proportion"]):
            return "QUANTITATIVE"

        # 4. Conceptual / Mechanism / Exam Doubts query
        if any(kw in q for kw in ["explain", "mechanism", "how does", "why does", "describe", "steps", "process", "issues", "prevention", "causes", "effects", "exam", "tomorrow"]):
            return "CONCEPTUAL"

        # 5. Factoid / Definition query
        if re.search(r'\b(what\s+is|what\s+are|define|definition\s+of|meaning\s+of)\b', q):
            return "FACTOID"

        # Default for subject matter inquiries
        return "TOPICAL_CONCEPT"

    def generate_retrieval_queries(self, original_query: str, canonical_query: str, intent: str = "TOPICAL_CONCEPT") -> List[str]:
        """
        Implements Multi-Query Strategy: "Never trust correction alone".
        Generates original query, canonical query, and concept-extracted query.
        """
        queries = [canonical_query]
        if original_query.lower() != canonical_query.lower():
            queries.append(original_query)

        if intent == "STRUCTURAL_OVERVIEW":
            # Add targeted structural and chapter queries
            for sq in ["CONTENTS Table of Contents Zoology", "UNIT I Chapter 1 Chapter 2 Chapter 3", "UNIT IV Chapter 10 Chapter 11 Chapter 12 Chapter 13"]:
                if sq not in queries:
                    queries.append(sq)
        else:
            # Generate concept query by removing conversational scaffolding
            concept_terms = self._extract_concept_keywords(canonical_query)
            if concept_terms and len(concept_terms) > 3 and concept_terms.lower() not in [q.lower() for q in queries]:
                queries.append(concept_terms)

        return queries

    def detect_evidence_gap(self, query: str, retrieved_chunks: List[Any]) -> Tuple[bool, Optional[str]]:
        """
        Checks if the user asked for substantive topical information,
        but the retrieved context ONLY contains front-matter Table of Contents chunks without substantive body text.
        """
        if not retrieved_chunks:
            return True, query

        only_toc = all(
            (getattr(c, "page_number", None) is not None and getattr(c, "page_number", None) <= 3) or 
            "CONTENTS" in getattr(c, "chunk_text", "") or 
            "Table of Contents" in getattr(c, "section_heading", "")
            for c in retrieved_chunks
        )

        q_lower = query.lower()
        topic_match = re.search(r'\b(chapter\s+\d+|environmental\s+issues|pollution|prevention|reproduction|genetics|evolution|health|disease|biotechnology|spermatogenesis)\b', q_lower)
        if only_toc and topic_match:
            matched_topic = topic_match.group(0)
            logger.warning(f"[QueryReformulator] Detected Evidence Gap: TOC returned for topic '{matched_topic}'")
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
            r'\bi\s+have\s+an\s+exam\s+tomorrow\b',
            r'\bfor\s+my\s+exam\s+tomorrow\b',
            r'\bi\s+want\s+to\s+know\b',
            r'\bgive\s+me\b'
        ]
        clean = text
        for p in noise_patterns:
            clean = re.sub(p, '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'[^\w\s]', ' ', clean)
        tokens = [t for t in clean.split() if t.lower() not in COMMON_ENGLISH_WORDS]
        return " ".join(tokens).strip()

    def _normalize_whitespace(self, text: str) -> str:
        return re.sub(r'\s+', ' ', text).strip()

    def extract_topics(self, text: str, workspace_id: str = "", top_n: int = 5) -> List[str]:
        """
        Extracts semantic educational/domain topics from query or context chunks.
        Delegates to TopicKnowledgeExtractor for syllabus grounding, word-boundary checks,
        and conversational stop-word elimination.
        """
        from backend.services.nlp.topic_knowledge_extractor import TopicKnowledgeExtractor
        return TopicKnowledgeExtractor().extract_topics(text, workspace_id=workspace_id, top_n=top_n)

