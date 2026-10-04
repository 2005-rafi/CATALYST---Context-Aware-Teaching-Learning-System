from backend.services.document.extractors.base_extractor import BaseExtractor
from backend.services.document.extractors.pdf_extractor import PDFExtractor
from backend.services.document.extractors.docx_extractor import DOCXExtractor
from backend.services.document.extractors.text_extractor import TextExtractor


class ExtractorFactory:
    @staticmethod
    def get_extractor(file_type: str) -> BaseExtractor:
        file_type = file_type.lower()
        if file_type == "pdf":
            return PDFExtractor()
        elif file_type == "docx":
            return DOCXExtractor()
        elif file_type in ("txt", "text", "md", "markdown"):
            return TextExtractor()
        else:
            raise ValueError(f"Unsupported file type for extraction: {file_type}")
