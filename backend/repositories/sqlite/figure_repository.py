"""
FigureRepository — CRUD operations for the figure_chunks table.
Follows the same BaseRepository pattern as ChunkRepository.
"""
import datetime
import logging
from typing import List, Optional, Dict, Any

from backend.repositories.sqlite.base_repository import BaseRepository
from backend.repositories.sqlite.database import db_connection

logger = logging.getLogger(__name__)


class FigureRepository(BaseRepository):
    """
    Manages figure metadata persistence in SQLite.
    figure_chunks table stores extracted figure crops with their AI captions
    and embedding references for semantic retrieval.
    """

    def create_figure(
        self,
        figure_id: str,
        workspace_id: str,
        document_id: str,
        page_number: int,
        figure_index: int,
        file_path: str,
        context_text: str = "",
        caption_text: str = "",
        figure_type: str = "unknown",
        embedding_ref: str = "",
    ) -> Dict[str, Any]:
        """Inserts a single figure record into figure_chunks."""
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self._execute(
            """
            INSERT INTO figure_chunks (
                figure_id, workspace_id, document_id, page_number, figure_index,
                file_path, caption_text, context_text, figure_type, embedding_ref, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                figure_id, workspace_id, document_id, page_number, figure_index,
                file_path, caption_text, context_text, figure_type, embedding_ref, now
            )
        )
        return self.get_figure(figure_id) or {}

    def create_figures_batch(self, figures_data: List[tuple]) -> None:
        """
        Atomically inserts multiple figure records in a single transaction.
        Each tuple: (figure_id, workspace_id, document_id, page_number, figure_index,
                     file_path, caption_text, context_text, figure_type, embedding_ref, created_at)
        """
        if not figures_data:
            return
        with db_connection() as conn:
            conn.cursor().executemany(
                """
                INSERT INTO figure_chunks (
                    figure_id, workspace_id, document_id, page_number, figure_index,
                    file_path, caption_text, context_text, figure_type, embedding_ref, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                figures_data
            )

    def get_figure(self, figure_id: str) -> Optional[Dict[str, Any]]:
        return self._execute(
            "SELECT * FROM figure_chunks WHERE figure_id = ?",
            (figure_id,),
            fetch_one=True
        )

    def get_figures_by_document(self, document_id: str) -> List[Dict[str, Any]]:
        return self._execute(
            "SELECT * FROM figure_chunks WHERE document_id = ? ORDER BY page_number, figure_index",
            (document_id,),
            fetch_all=True
        ) or []

    def get_figures_by_workspace(self, workspace_id: str) -> List[Dict[str, Any]]:
        return self._execute(
            "SELECT * FROM figure_chunks WHERE workspace_id = ? ORDER BY document_id, page_number, figure_index",
            (workspace_id,),
            fetch_all=True
        ) or []

    def get_figures_by_ids(self, figure_ids: List[str]) -> List[Dict[str, Any]]:
        if not figure_ids:
            return []
        placeholders = ",".join(["?"] * len(figure_ids))
        return self._execute(
            f"SELECT * FROM figure_chunks WHERE figure_id IN ({placeholders})",
            tuple(figure_ids),
            fetch_all=True
        ) or []

    def update_caption(self, figure_id: str, caption_text: str, figure_type: str) -> None:
        """Updates the AI-generated caption and detected figure type after captioning stage."""
        self._execute(
            "UPDATE figure_chunks SET caption_text = ?, figure_type = ? WHERE figure_id = ?",
            (caption_text, figure_type, figure_id)
        )

    def update_embedding_ref(self, figure_id: str, embedding_ref: str) -> None:
        """Links a figure to its vector store entry (chunk_id used as embedding key)."""
        self._execute(
            "UPDATE figure_chunks SET embedding_ref = ? WHERE figure_id = ?",
            (embedding_ref, figure_id)
        )

    def delete_figures_by_document(self, document_id: str) -> None:
        self._execute(
            "DELETE FROM figure_chunks WHERE document_id = ?",
            (document_id,)
        )

    def delete_figures_by_workspace(self, workspace_id: str) -> None:
        self._execute(
            "DELETE FROM figure_chunks WHERE workspace_id = ?",
            (workspace_id,)
        )

    def get_figure_count_by_document(self, document_id: str) -> int:
        result = self._execute(
            "SELECT COUNT(*) as cnt FROM figure_chunks WHERE document_id = ?",
            (document_id,),
            fetch_one=True
        )
        return result["cnt"] if result else 0
