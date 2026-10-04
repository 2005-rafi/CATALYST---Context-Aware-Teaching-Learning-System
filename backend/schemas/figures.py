"""Figure API schemas — Pydantic request/response models."""
from pydantic import BaseModel
from typing import List, Optional


class FigureMetadataResponse(BaseModel):
    figure_id: str
    document_id: str
    page_number: int
    caption_text: Optional[str] = ""
    figure_type: Optional[str] = "unknown"
    context_text: Optional[str] = ""
    url: str


class FigureItem(BaseModel):
    figure_id: str
    page_number: int
    figure_type: Optional[str] = "unknown"
    caption_text: Optional[str] = ""
    url: str


class DocumentFiguresResponse(BaseModel):
    document_id: str
    figure_count: int
    figures: List[FigureItem]
