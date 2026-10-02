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
            
        # Strip raw HTML tags like <br>
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        
        # Ensure headers have space after #
        text = re.sub(r'^(#{1,6})([^#\s])', r'\1 \2', text, flags=re.MULTILINE)
        
        # Basic validation: if we only got "I don't know" phrases, standardize it
        hallucination_phrases = ["i don't know", "i do not know", "i am not sure", "no evidence found", "no information"]
        if len(text) < 100 and any(p in text.lower() for p in hallucination_phrases):
            return "I could not find sufficient information in the uploaded documents to answer your question."
            
        return text
        
    def append_sources(self, response_text: str, sources: List[SourceDocument]) -> str:
        if not sources:
            return response_text
            
        sources_text = self.source_attributor.format_sources_text(sources)
        return response_text + "\n\n---\n\n" + sources_text
