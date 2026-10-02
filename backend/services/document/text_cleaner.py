import re
import unicodedata

class TextCleaner:
    def clean(self, text: str) -> str:
        if not text:
            return ""
            
        text = self._fix_encoding(text)
        text = self._remove_control_chars(text)
        text = self._fix_hyphenated_breaks(text)
        text = self._normalize_whitespace(text)
        text = self._normalize_newlines(text)
        text = self._strip_lines(text)
        
        return text

    def truncate_references(self, text: str) -> tuple[str, str]:
        """
        Detects standard bibliography/reference headers and splits the core content
        from the reference section to prevent semantic vector pollution.
        """
        # Look for standalone lines like References, Bibliography, Works Cited (with optional numbers/spaces)
        pattern = re.compile(
            r'\n(?:[0-9]*[\.\s]*)?(References|Bibliography|Works\s+Cited)\b', 
            re.IGNORECASE
        )
        matches = list(pattern.finditer(text))
        if matches:
            # We take the last match to avoid early false positives (like a mention in the abstract or text)
            last_match = matches[-1]
            split_idx = last_match.start()
            
            content = text[:split_idx].strip()
            references = text[split_idx:].strip()
            return content, references
            
        return text, ""

    def _fix_encoding(self, text: str) -> str:
        return text.encode('utf-8', errors='ignore').decode('utf-8')

    def _remove_control_chars(self, text: str) -> str:
        # Keep \n, \r, \t, and printable chars
        # Remove Cc (Control) and Cf (Format)
        cleaned = []
        for char in text:
            if char in ('\n', '\r', '\t'):
                cleaned.append(char)
                continue
            cat = unicodedata.category(char)
            if cat not in ('Cc', 'Cf'):
                cleaned.append(char)
        return "".join(cleaned)

    def _fix_hyphenated_breaks(self, text: str) -> str:
        return re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

    def _normalize_whitespace(self, text: str) -> str:
        return re.sub(r'[ \t]+', ' ', text)

    def _normalize_newlines(self, text: str) -> str:
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        return re.sub(r'\n{3,}', '\n\n', text)

    def _strip_lines(self, text: str) -> str:
        lines = text.split('\n')
        stripped_lines = [line.strip() for line in lines]
        
        # Remove empty lines that were just whitespace
        # But wait, if we drop ALL empty lines, we lose paragraph breaks (\n\n).
        # The instructions say: "Remove lines that are purely whitespace."
        # If we have paragraph breaks, they might be empty lines.
        # Let's keep empty lines if they were produced by \n\n, 
        # or maybe the instruction "split by \n, strip each line, rejoin. Remove lines that are purely whitespace"
        # means if a line had ONLY spaces, it becomes empty string.
        # We still want to preserve \n\n. Let's just strip lines and rejoin.
        # Wait, if we drop empty lines, \n\n becomes \n.
        # Let's drop empty lines only if there are more than 2 consecutive?
        # Actually, if we rejoin with \n, empty strings remain empty strings, so \n\n is preserved.
        
        return "\n".join(stripped_lines).strip()
