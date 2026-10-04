from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod


@dataclass
class PageContent:
    page_number: int
    text: str


@dataclass
class FigureContent:
    """
    Carries metadata for a single extracted figure from a document page.
    Bounding box is in PDF points (x0, y0, x1, y1).
    """
    page_number: int
    figure_index: int           # per-page sequential index
    bbox: Tuple[float, float, float, float]   # (x0, y0, x1, y1)
    image_bytes: Optional[bytes] = None       # PNG bytes of the cropped figure
    context_text: str = ""     # surrounding text extracted via spatial proximity
    caption_text: str = ""     # AI-generated caption (populated later by captioner)
    figure_type: str = "unknown"   # 'diagram', 'chart', 'photo', 'equation', 'table_image'


@dataclass
class ExtractionResult:
    full_text: str
    pages: List[PageContent]
    metadata: Dict[str, Any]
    total_pages: int
    extraction_success: bool
    page_boundaries: List[int] = field(default_factory=list)
    headings: List[Dict[str, Any]] = field(default_factory=list)
    figures: List[FigureContent] = field(default_factory=list)   # Visual RAG: extracted figures


class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, file_path: str) -> ExtractionResult:
        pass
