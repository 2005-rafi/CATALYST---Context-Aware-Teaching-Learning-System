import re
from pathlib import Path
from backend.services.document.extractors.base_extractor import (
    BaseExtractor,
    ExtractionResult,
    PageContent,
)


class TextExtractor(BaseExtractor):
    """
    Robust extractor for plain text (.txt) and Markdown (.md) documents.
    Handles multiple encodings (UTF-8, Latin-1, CP1252) and preserves structural headings.
    """

    def extract(self, file_path: str) -> ExtractionResult:
        content = ""
        for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
            try:
                with open(file_path, "r", encoding=enc) as f:
                    content = f.read()
                break
            except (UnicodeDecodeError, LookupError):
                continue

        # Extract markdown headings (# Heading) if present
        headings = []
        for line in content.splitlines():
            line_str = line.strip()
            if line_str.startswith("#"):
                match = re.match(r"^(#{1,6})\s+(.*)$", line_str)
                if match:
                    level = len(match.group(1))
                    title = match.group(2).strip()
                    headings.append({"title": title, "level": level})

        # Check for explicit form feed page markers (\x0c) or markdown page dividers
        raw_pages = re.split(r"\x0c|\n---page---\n", content)
        pages = []
        if len(raw_pages) > 1:
            for idx, p_text in enumerate(raw_pages, start=1):
                cleaned = p_text.strip()
                if cleaned:
                    pages.append(PageContent(page_number=idx, text=cleaned))
        
        if not pages:
            pages.append(PageContent(page_number=1, text=content.strip()))

        page_boundaries = []
        cursor = 0
        for p in pages:
            cursor += len(p.text)
            page_boundaries.append(cursor)

        metadata = {
            "source": Path(file_path).name,
            "file_type": "txt" if file_path.lower().endswith(".txt") else "md",
            "character_count": len(content),
            "line_count": len(content.splitlines()),
        }

        return ExtractionResult(
            full_text=content,
            pages=pages,
            metadata=metadata,
            total_pages=len(pages),
            extraction_success=True,
            page_boundaries=page_boundaries,
            headings=headings,
            figures=[],
        )
