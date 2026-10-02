from dataclasses import dataclass, field
from typing import List, Dict, Any
from abc import ABC, abstractmethod

@dataclass
class PageContent:
    page_number: int
    text: str

@dataclass
class ExtractionResult:
    full_text: str
    pages: List[PageContent]
    metadata: Dict[str, Any]
    total_pages: int
    extraction_success: bool
    page_boundaries: List[int] = field(default_factory=list)
    headings: List[Dict[str, Any]] = field(default_factory=list)

class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, file_path: str) -> ExtractionResult:
        pass
