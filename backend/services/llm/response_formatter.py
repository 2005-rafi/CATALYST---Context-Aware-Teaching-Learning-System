import re
from typing import List
from backend.services.retrieval.source_attributor import SourceDocument, SourceAttributor

class ResponseFormatter:
    def __init__(self):
        self.source_attributor = SourceAttributor()
        
    def validate_and_clean(self, text: str) -> str:
        text = text.strip()
        if not text:
            return "I could not generate a response. Please try again."
            
        # Ensure code blocks are closed
        backtick_count = text.count("```")
        if backtick_count % 2 != 0:
            text += "\n```"
            
        # Standardize markdown table structure: ensure rows are intact and <br /> is preserved
        text = self._sanitize_tables(text)
        
        # Ensure headers have space after #
        text = re.sub(r'^(#{1,6})([^#\s])', r'\1 \2', text, flags=re.MULTILINE)
        
        # Basic validation: if we only got "I don't know" phrases, standardize it
        hallucination_phrases = ["i don't know", "i do not know", "i am not sure", "no evidence found", "no information"]
        if len(text) < 100 and any(p in text.lower() for p in hallucination_phrases):
            return "I could not find sufficient information in the uploaded documents to answer your question."
            
        return text

    def _sanitize_tables(self, text: str) -> str:
        """
        Sanitizes Markdown tables:
        1. Preserves '<br />' inside cells for multi-point bullet items.
        2. Normalizes table row lines so that stray multiline cell breaks are rejoined.
        """
        lines = text.split('\n')
        sanitized_lines = []
        in_table = False
        current_row = []

        for line in lines:
            stripped = line.strip()
            
            # Detect table separator line e.g. |---|---|---|
            if re.match(r'^\|[\s:\-\|]+\|$', stripped):
                in_table = True
                sanitized_lines.append(stripped)
                continue

            if in_table:
                # If line is a valid table row, keep it
                if stripped.startswith('|') and stripped.endswith('|'):
                    sanitized_lines.append(stripped)
                    continue
                else:
                    # Table has ended
                    in_table = False

            sanitized_lines.append(line)

        return '\n'.join(sanitized_lines)
        
    def append_sources(self, response_text: str, sources: List[SourceDocument]) -> str:
        if not sources:
            return response_text
            
        # If the response explicitly denotes out-of-box content or does not cite [1], do not attach sources
        if "content not from uploaded content" in response_text.lower():
            return response_text
        if not re.search(r'\[\d+\]', response_text):
            return response_text

        sources_text = self.source_attributor.format_sources_text(sources)
        return response_text + "\n\n---\n\n" + sources_text
