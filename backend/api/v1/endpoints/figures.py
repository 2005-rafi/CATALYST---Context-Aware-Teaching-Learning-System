"""Visual RAG figure streaming and metadata API endpoints."""
import os
import logging
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from backend.repositories.sqlite.figure_repository import FigureRepository
from backend.schemas.figures import FigureMetadataResponse, DocumentFiguresResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/figures", tags=["Figures"])

_figure_repo = FigureRepository()


@router.get("/{figure_id}")
def serve_figure_image(
    figure_id: str,
    workspace_id: str = Query(..., description="Workspace scope for access validation"),
):
    """
    Streams the PNG crop for a specific figure.
    Workspace ID is validated to enforce data isolation.
    """
    figure = _figure_repo.get_figure(figure_id)

    if not figure:
        raise HTTPException(status_code=404, detail=f"Figure '{figure_id}' not found.")

    # Scope validation: figure must belong to the requesting workspace
    if figure.get("workspace_id") != workspace_id:
        raise HTTPException(status_code=403, detail="Access denied: figure does not belong to this workspace.")

    file_path = figure.get("file_path", "")
    if not file_path or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Figure file not found on server. It may have been cleaned up.")

    return FileResponse(
        path=file_path,
        media_type="image/png",
        filename=os.path.basename(file_path),
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.get("/{figure_id}/meta", response_model=FigureMetadataResponse)
def get_figure_metadata(
    figure_id: str,
    workspace_id: str = Query(..., description="Workspace scope for access validation"),
):
    """Returns metadata for a specific figure (caption, type, page number, document)."""
    figure = _figure_repo.get_figure(figure_id)

    if not figure:
        raise HTTPException(status_code=404, detail=f"Figure '{figure_id}' not found.")

    if figure.get("workspace_id") != workspace_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    return FigureMetadataResponse(
        figure_id=figure["figure_id"],
        document_id=figure["document_id"],
        page_number=figure["page_number"],
        caption_text=figure.get("caption_text", ""),
        figure_type=figure.get("figure_type", "unknown"),
        context_text=figure.get("context_text", ""),
        url=f"/api/v1/figures/{figure_id}?workspace_id={workspace_id}",
    )


@router.get("/document/{document_id}", response_model=DocumentFiguresResponse)
def list_document_figures(
    document_id: str,
    workspace_id: str = Query(...),
):
    """Lists all figures extracted from a specific document."""
    figures = _figure_repo.get_figures_by_document(document_id)
    # Filter by workspace for safety
    figures = [f for f in figures if f.get("workspace_id") == workspace_id]

    return DocumentFiguresResponse(
        document_id=document_id,
        figure_count=len(figures),
        figures=[
            {
                "figure_id": f["figure_id"],
                "page_number": f["page_number"],
                "figure_type": f.get("figure_type", "unknown"),
                "caption_text": f.get("caption_text", ""),
                "url": f"/api/v1/figures/{f['figure_id']}?workspace_id={workspace_id}",
            }
            for f in figures
        ],
    )
