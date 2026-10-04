"""
FigureStorageService — manages physical file lifecycle for extracted PDF figures.
Stores PNGs at: storage/figures/{workspace_id}/{document_id}/fig_{page}_{idx}.png
"""
import os
import shutil
import logging
from typing import Optional

logger = logging.getLogger(__name__)

FIGURES_BASE_PATH = "storage/figures"


class FigureStorageService:
    """
    Handles the disk I/O lifecycle for figure crop PNGs extracted from PDFs.
    Follows Single Responsibility: only storage, no metadata, no captioning.
    """

    def save_figure(
        self,
        workspace_id: str,
        document_id: str,
        page_number: int,
        figure_index: int,
        image_bytes: bytes,
    ) -> Optional[str]:
        """
        Saves a PNG crop to disk and returns its absolute file path.
        Returns None on failure (non-blocking — pipeline continues).
        """
        try:
            dir_path = self._get_dir(workspace_id, document_id)
            os.makedirs(dir_path, exist_ok=True)
            file_name = f"fig_{page_number}_{figure_index}.png"
            file_path = os.path.join(dir_path, file_name)
            with open(file_path, "wb") as f:
                f.write(image_bytes)
            logger.debug(f"[FigureStorage] Saved figure: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"[FigureStorage] Failed to save figure p{page_number}_{figure_index}: {e}")
            return None

    def delete_document_figures(self, workspace_id: str, document_id: str) -> None:
        """
        Deletes all figure PNGs for a given document (called on document deletion).
        """
        dir_path = self._get_dir(workspace_id, document_id)
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path, ignore_errors=True)
            logger.info(f"[FigureStorage] Deleted figure directory: {dir_path}")

    def delete_workspace_figures(self, workspace_id: str) -> None:
        """Deletes all figures for an entire workspace (called on workspace deletion)."""
        ws_path = os.path.join(FIGURES_BASE_PATH, workspace_id)
        if os.path.isdir(ws_path):
            shutil.rmtree(ws_path, ignore_errors=True)
            logger.info(f"[FigureStorage] Deleted workspace figure directory: {ws_path}")

    def get_figure_path(self, workspace_id: str, document_id: str, page_number: int, figure_index: int) -> str:
        """Constructs the expected path for a figure (may or may not exist)."""
        dir_path = self._get_dir(workspace_id, document_id)
        return os.path.join(dir_path, f"fig_{page_number}_{figure_index}.png")

    def _get_dir(self, workspace_id: str, document_id: str) -> str:
        return os.path.join(FIGURES_BASE_PATH, workspace_id, document_id)
