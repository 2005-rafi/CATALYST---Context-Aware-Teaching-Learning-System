from pydantic import BaseModel

from typing import Optional

class RetrievedChunk(BaseModel):
    chunk_id: str
    document_id: str
    source_file: str
    chunk_text: str
    score: float
    page_number: Optional[int] = None
    section_heading: Optional[str] = None
