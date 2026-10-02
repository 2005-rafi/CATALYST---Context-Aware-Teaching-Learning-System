import docx
from backend.services.document.extractors.base_extractor import BaseExtractor, ExtractionResult, PageContent

class DOCXExtractor(BaseExtractor):
    def extract(self, file_path: str) -> ExtractionResult:
        try:
            document = docx.Document(file_path)
            
            text_parts = []
            headings = []
            current_cumulative_length = 0
            
            for para in document.paragraphs:
                para_text = para.text.strip()
                if not para_text:
                    continue
                    
                # Basic check for headings based on style name
                is_heading = para.style and para.style.name and para.style.name.startswith("Heading")
                
                if is_heading:
                    headings.append({
                        "text": para_text,
                        "start_offset": current_cumulative_length
                    })
                    text_parts.append(f"# {para_text}")
                    current_cumulative_length += len(f"# {para_text}") + 1
                else:
                    text_parts.append(para_text)
                    current_cumulative_length += len(para_text) + 1
                    
            full_text = "\n".join(text_parts)
            
            # Extract basic metadata
            metadata = {}
            core_props = document.core_properties
            if core_props:
                metadata = {
                    "author": core_props.author,
                    "title": core_props.title,
                    "subject": core_props.subject,
                    "created": str(core_props.created) if core_props.created else None,
                    "modified": str(core_props.modified) if core_props.modified else None
                }
            
            # DOCX doesn't have native pages easily accessible, so we treat it as 1 page
            pages = [PageContent(page_number=1, text=full_text)]
            page_boundaries = [len(full_text)]
            
            return ExtractionResult(
                full_text=full_text,
                pages=pages,
                metadata=metadata,
                total_pages=1,
                extraction_success=True,
                page_boundaries=page_boundaries,
                headings=headings
            )
        except Exception as e:
            return ExtractionResult(
                full_text="",
                pages=[],
                metadata={},
                total_pages=0,
                extraction_success=False
            )
