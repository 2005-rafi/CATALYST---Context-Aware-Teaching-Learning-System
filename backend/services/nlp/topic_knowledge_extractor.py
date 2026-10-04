import re
import logging
import threading
from typing import List, Set, Dict, Optional, Tuple, Any
from backend.repositories.sqlite.chunk_repository import ChunkRepository

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Strict Conversational, Stylistic, Grammatical, and Sub-word Blacklists
# ---------------------------------------------------------------------------
NON_TOPIC_WORDS: Set[str] = {
    # Conversational & Prompts
    "simple", "simply", "brief", "briefly", "term", "terms", "plain", "explain",
    "explained", "explaining", "explanation", "explanations", "overview", "summary",
    "summarize", "summarized", "summaries", "summarizing", "detail", "details",
    "detailed", "describe", "described", "describing", "description", "definition",
    "define", "defined", "defining", "meaning", "meanings", "concept", "concepts",
    "difference", "differences", "different", "differ", "differs", "versus", "comparison",
    "compare", "compared", "comparing", "guide", "guidance", "note", "notes", "key",
    "point", "points", "main", "important", "importance", "essay", "paragraph", "answer",
    "answers", "question", "questions", "ask", "asked", "please", "tell", "give", "giving",
    "show", "showing", "help", "helping", "understand", "understanding", "learn",
    "learning", "study", "studying", "read", "reading", "write", "writing", "written",
    
    # Document Meta, Structure & Layout Words
    "chapter", "chapters", "chapte", "section", "sections", "page", "pages", "book",
    "books", "textbook", "textbooks", "unit", "units", "lesson", "lessons", "table",
    "tables", "figure", "figures", "diagram", "diagrams", "chart", "charts", "graph",
    "graphs", "content", "contents", "index", "syllabus", "curriculum", "curricula",
    "document", "documents", "file", "files", "pdf", "pdfs", "heading", "headings",
    "title", "titles", "paragraph", "line", "lines", "stage", "stages", "exam", "exams",
    "test", "tests", "paper", "papers", "score", "scores", "mark", "marks", "grade",
    "evaluation", "evaluations", "assessment", "assessments", "exercise", "exercises",
    "activity", "activities", "assignment", "assignments", "objective", "objectives",
    
    # Common English Adverbs, Prepositions, Verbs & Adjectives
    "the", "and", "that", "have", "for", "not", "with", "you", "this", "but", "his",
    "from", "they", "say", "her", "she", "will", "one", "all", "would", "there",
    "their", "what", "out", "about", "who", "get", "which", "when", "make", "can",
    "like", "time", "just", "him", "know", "take", "people", "into", "year", "your",
    "good", "some", "could", "them", "see", "other", "than", "then", "now", "look",
    "only", "come", "its", "over", "think", "also", "back", "after", "use", "used",
    "two", "how", "our", "work", "first", "well", "way", "even", "new", "want",
    "because", "any", "these", "day", "most", "us", "are", "was", "were", "been",
    "being", "does", "did", "why", "many", "more", "very", "much", "each", "both",
    "such", "under", "between", "through", "before", "same", "able", "ability",
    "base", "based", "basis", "basic", "acquire", "acquired", "acquiring", "adapt",
    "adaptation", "adapted", "agreement", "ants", "live", "living", "life", "late",
    "less", "class", "classify", "classified", "classification", "type", "types",
    "kind", "kinds", "sort", "sorts", "part", "parts", "step", "steps", "form", "forms",
    "role", "roles", "case", "cases", "state", "states", "view", "views", "plan", "plans",
    "fact", "facts", "level", "levels", "area", "areas", "side", "sides", "head",
    "body", "order", "orders", "group", "groups", "number", "numbers", "name", "names",
    "method", "methods", "biology", "human", "animal", "animals", "plant", "plants",
    "blood", "abdominal", "digestive", "reproductive", "health",
    
    # Broken Sub-tokens & Fragment Truncations
    "agra", "gram", "ation", "eproductive", "acteria", "uct", "duct", "less", "chapte",
    "plain", "ants", "live", "late", "base", "able", "digest", "tion", "sion", "ment",
}

# ---------------------------------------------------------------------------
# High-Value Domain Curricula Multi-Word Patterns (Title Case Canonical)
# ---------------------------------------------------------------------------
CANONICAL_DOMAIN_PATTERNS: List[Tuple[str, str]] = [
    # Biology & Human Physiology
    (r"\b(human\s+reproduction|reproductive\s+system)\b", "Human Reproduction"),
    (r"\b(male\s+reproductive\s+system)\b", "Male Reproductive System"),
    (r"\b(female\s+reproductive\s+system)\b", "Female Reproductive System"),
    (r"\b(spermatogenesis)\b", "Spermatogenesis"),
    (r"\b(oogenesis)\b", "Oogenesis"),
    (r"\b(menstrual\s+cycle)\b", "Menstrual Cycle"),
    (r"\b(fertilization\s+and\s+implantation|fertilization)\b", "Fertilization"),
    (r"\b(embryonic\s+development)\b", "Embryonic Development"),
    (r"\b(structure\s+of\s+ovum|ovum\s+structure)\b", "Structure of Ovum"),
    (r"\b(structure\s+of\s+spermatozoan|sperm\s+structure|structure\s+of\s+sperm)\b", "Structure of Sperm"),
    (r"\b(contraception|contraceptive\s+methods)\b", "Contraception"),
    (r"\b(sexually\s+transmitted\s+diseases|std|stds)\b", "Sexually Transmitted Diseases"),
    (r"\b(digestive\s+system|human\s+digestive\s+system|digestion\s+and\s+absorption)\b", "Digestive System"),
    (r"\b(circulatory\s+system|blood\s+circulation|circulation)\b", "Circulatory System"),
    (r"\b(respiratory\s+system|breathing\s+and\s+respiration)\b", "Respiratory System"),
    (r"\b(nervous\s+system|neural\s+control\s+and\s+coordination)\b", "Nervous System"),
    (r"\b(excretory\s+system|excretory\s+products)\b", "Excretory System"),
    (r"\b(endocrine\s+system|chemical\s+coordination)\b", "Endocrine System"),
    (r"\b(immune\s+system|immunity\s+and\s+vaccination)\b", "Immune System"),
    (r"\b(cell\s+cycle|mitosis\s+and\s+meiosis|cell\s+division)\b", "Cell Division"),
    
    # Genetics & Molecular Biology
    (r"\b(principles\s+of\s+inheritance|mendelian\s+inheritance|genetics)\b", "Principles of Inheritance"),
    (r"\b(molecular\s+basis\s+of\s+inheritance)\b", "Molecular Basis of Inheritance"),
    (r"\b(dna\s+replication)\b", "DNA Replication"),
    (r"\b(transcription)\b", "Transcription"),
    (r"\b(translation)\b", "Translation"),
    (r"\b(genetic\s+code)\b", "Genetic Code"),
    (r"\b(recombinant\s+dna\s+technology|recombinant\s+dna)\b", "Recombinant DNA Technology"),
    (r"\b(polymerase\s+chain\s+reaction|pcr\s+amplification)\b", "Polymerase Chain Reaction"),
    (r"\b(biotechnology\s+applications|biotechnology)\b", "Biotechnology Applications"),
    
    # Ecology & Evolution
    (r"\b(environmental\s+issues)\b", "Environmental Issues"),
    (r"\b(biodiversity\s+and\s+conservation|biodiversity)\b", "Biodiversity and Conservation"),
    (r"\b(ecosystem\s+structure|ecosystem)\b", "Ecosystem Structure"),
    (r"\b(air\s+pollution)\b", "Air Pollution"),
    (r"\b(water\s+pollution)\b", "Water Pollution"),
    (r"\b(ozone\s+depletion)\b", "Ozone Depletion"),
    (r"\b(greenhouse\s+effect\s+and\s+global\s+warming|greenhouse\s+effect)\b", "Greenhouse Effect"),
    (r"\b(evolution\s+and\s+origin|evolution)\b", "Evolutionary Biology"),
    (r"\b(reproduction\s+in\s+organisms)\b", "Reproduction in Organisms"),
    (r"\b(parthenogenesis|natural\s+parthenogenesis)\b", "Parthenogenesis"),
]

# Specific validated single-word domain concepts
VALIDATED_SINGLE_DOMAIN_WORDS: Dict[str, str] = {
    "photosynthesis": "Photosynthesis",
    "respiration": "Respiration",
    "genetics": "Genetics",
    "evolution": "Evolution",
    "ecosystem": "Ecosystem",
    "biodiversity": "Biodiversity",
    "spermatogenesis": "Spermatogenesis",
    "oogenesis": "Oogenesis",
    "contraception": "Contraception",
    "fertilization": "Fertilization",
    "mitosis": "Mitosis",
    "meiosis": "Meiosis",
    "chromosome": "Chromosome",
    "chromatids": "Chromatids",
    "mutation": "Mutation",
    "vaccination": "Vaccination",
    "antibody": "Antibody",
    "antigen": "Antigen",
    "plasmid": "Plasmid",
    "transgenic": "Transgenic Organisms",
    "syngamy": "Syngamy",
    "parthenogenesis": "Parthenogenesis",
    "digestion": "Digestive System",
    "circulation": "Circulatory System",
    "immunity": "Immune System",
}


class TopicKnowledgeExtractor:
    """
    Syllabus-Grounded Pedagogical Concept & Topic Extractor.
    Ensures that only authentic, curriculum-relevant academic topics are tracked
    in Cognitive Mastery profiles, completely rejecting conversational filler words,
    stop words, formatting commands, and fragmented sub-word artifacts.
    """
    _instance: Optional["TopicKnowledgeExtractor"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "TopicKnowledgeExtractor":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TopicKnowledgeExtractor, cls).__new__(cls)
                cls._instance.chunk_repo = ChunkRepository()
                cls._instance._syllabus_cache = {}
            return cls._instance

    def is_valid_topic(self, topic: str) -> bool:
        """
        Validates whether a candidate string is an authentic pedagogical topic.
        Used for runtime extraction, memory updates, DB sanitization, and analytics defense.
        """
        if not topic:
            return False
            
        clean = topic.strip().lower()
        
        # 1. Disallow very short words or fragments
        if len(clean) < 4:
            # Allow well-known academic acronyms only
            return clean.upper() in {"DNA", "RNA", "PCR", "ATP", "STD"}

        # 2. Check strict non-topic blacklist
        if clean in NON_TOPIC_WORDS:
            return False

        # 3. Check if all individual words in a multi-word topic are non-topic filler
        tokens = [t for t in re.findall(r'[a-zA-Z]+', clean)]
        if not tokens:
            return False
        if all(t in NON_TOPIC_WORDS for t in tokens):
            return False

        # 4. Check known domain multi-words or single domain words
        for pattern, _ in CANONICAL_DOMAIN_PATTERNS:
            if re.search(pattern, clean, re.IGNORECASE):
                return True

        if clean in VALIDATED_SINGLE_DOMAIN_WORDS:
            return True

        # 5. Length and character health checks
        if any(char.isdigit() for char in clean):
            # E.g. "Chapter 13 235" or "14 Human"
            cleaned_of_digits = re.sub(r'^\d+\s*|\s*\d+$', '', clean).strip()
            if cleaned_of_digits in NON_TOPIC_WORDS:
                return False
            if len(cleaned_of_digits) >= 4 and cleaned_of_digits not in NON_TOPIC_WORDS:
                return True

        # Must have at least 4 letters, no weird trailing symbols
        return len(clean) >= 4 and not bool(re.search(r'[^a-zA-Z\s\-]', clean))

    def extract_topics(
        self,
        text: str,
        workspace_id: str = "",
        top_n: int = 5
    ) -> List[str]:
        """
        Extracts verified, syllabus-grounded educational topics from text.
        Applies:
        1. Multi-word domain curriculum pattern matching.
        2. Syllabus section headings grounding from SQLite chunks.
        3. Validated single domain terms with strict word boundary enforcement.
        4. Canonical Title Casing and deduplication.
        """
        if not text or not text.strip():
            return []

        matched_topics: List[str] = []

        # 1. Multi-Word Canonical Domain Patterns (Highest Priority)
        for pattern, canonical_name in CANONICAL_DOMAIN_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                matched_topics.append(canonical_name)

        # 2. Syllabus Section Headings Grounding (from SQLite chunks)
        if workspace_id:
            syllabus_headings = self.get_workspace_syllabus_headings(workspace_id)
            for heading in syllabus_headings:
                # Use word boundary search to avoid substring bleed
                pattern = r'\b' + re.escape(heading.lower()) + r'\b'
                if re.search(pattern, text.lower(), re.IGNORECASE):
                    matched_topics.append(self.canonicalize_topic(heading))

        # 3. Validated Single Domain Words with Strict Word Boundaries
        for term, canonical_name in VALIDATED_SINGLE_DOMAIN_WORDS.items():
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                matched_topics.append(canonical_name)

        # 4. Filter, Deduplicate & Canonicalize
        seen: Set[str] = set()
        clean_topics: List[str] = []
        for t in matched_topics:
            canonical = self.canonicalize_topic(t)
            canonical_lower = canonical.lower()
            if canonical_lower not in seen and self.is_valid_topic(canonical):
                seen.add(canonical_lower)
                clean_topics.append(canonical)

        return clean_topics[:top_n]

    def get_workspace_syllabus_headings(self, workspace_id: str) -> List[str]:
        """
        Retrieves and caches cleaned section headings from indexed workspace chunks.
        Extracts genuine curriculum chapters/sections while dropping noise.
        """
        if not workspace_id:
            return []

        with self._lock:
            if workspace_id in self._syllabus_cache:
                return self._syllabus_cache[workspace_id]

        try:
            chunks = self.chunk_repo.get_chunks_by_workspace(workspace_id)
            clean_headings: Set[str] = set()
            for c in chunks:
                heading = c.get("section_heading")
                if heading and isinstance(heading, str):
                    clean_h = self._clean_raw_heading(heading)
                    if clean_h and self.is_valid_topic(clean_h):
                        clean_headings.add(clean_h)

            sorted_headings = sorted(list(clean_headings))
            with self._lock:
                self._syllabus_cache[workspace_id] = sorted_headings
            logger.info(
                f"[TopicKnowledgeExtractor] Cached {len(sorted_headings)} syllabus topics for workspace '{workspace_id}'"
            )
            return sorted_headings
        except Exception as e:
            logger.warning(f"[TopicKnowledgeExtractor] Failed to load syllabus headings: {e}")
            return []

    def _clean_raw_heading(self, heading: str) -> str:
        """
        Cleans OCR/PDF artifacts and chapter numbers from headings:
        e.g. 'Chapter 13 Environmental Issues  235' -> 'Environmental Issues'
             '14 Human Reproduction' -> 'Human Reproduction'
             '6 Reproduction in Organisms' -> 'Reproduction in Organisms'
        """
        if not heading:
            return ""
        # Remove chapter prefixes like 'Chapter 13' or 'Unit 2'
        h = re.sub(r'^(Chapter|Unit|Section|Part)\s+\d+[:\.\s-]*', '', heading, flags=re.IGNORECASE)
        # Remove leading numbers like '14 ' or '6 '
        h = re.sub(r'^\d+(\.\d+)*\s*[:\.\s-]*', '', h)
        # Remove trailing page numbers like ' 235'
        h = re.sub(r'\s+\d+$', '', h)
        # Normalize whitespace
        h = re.sub(r'\s+', ' ', h).strip()
        
        lower_h = h.lower()

        # Drop OCR uppercase random trigrams e.g. "ABC DEF OQG HIJ KL"
        if re.search(r'\b[A-Z]{3}\s+[A-Z]{3}\b', h):
            return ""

        # Drop generic boilerplate, conversational phrases or incomplete heading fragments
        if lower_h in {
            "the book", "learning objectives", "government of tamil nadu",
            "five stages of exam", "bangalore", "activities", "syllabus", "summary"
        }:
            return ""

        if lower_h.startswith("according to") or lower_h.startswith("activities") or lower_h.startswith("who can participate") or lower_h.endswith("are of") or lower_h.endswith("can be"):
            return ""

        # Drop single-letter sequences like "A B C D" or "ABC DEF OQG HIJ KL"
        tokens = [t for t in h.split() if t.isalpha()]
        if len(tokens) >= 2 and sum(1 for t in tokens if len(t) <= 2) / len(tokens) >= 0.5:
            return ""
        if len(tokens) == 1 and len(tokens[0]) <= 2:
            return ""

        return h

    def canonicalize_topic(self, topic: str) -> str:
        """
        Normalizes a topic name to canonical Title Casing with proper acronym handling.
        """
        if not topic:
            return ""
        acronyms = {"dna": "DNA", "rna": "RNA", "pcr": "PCR", "atp": "ATP", "std": "STD", "stds": "STDs"}
        words = topic.strip().split()
        capitalized = []
        for w in words:
            w_lower = w.lower()
            if w_lower in acronyms:
                capitalized.append(acronyms[w_lower])
            elif w_lower in {"and", "in", "of", "the", "for", "to"}:
                capitalized.append(w_lower)
            else:
                capitalized.append(w.capitalize())
        
        res = " ".join(capitalized)
        if res and res[0].islower():
            res = res[0].upper() + res[1:]
        return res

    def invalidate_cache(self, workspace_id: str) -> None:
        """Invalidate syllabus cache when workspace documents change."""
        with self._lock:
            if workspace_id in self._syllabus_cache:
                del self._syllabus_cache[workspace_id]
