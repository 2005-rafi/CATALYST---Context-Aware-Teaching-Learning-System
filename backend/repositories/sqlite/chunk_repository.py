from backend.repositories.sqlite.base_repository import BaseRepository
from backend.repositories.sqlite.database import db_connection

class ChunkRepository(BaseRepository):
    def create_chunk(self, chunk_id: str, workspace_id: str, document_id: str, chunk_index: int, chunk_text: str, token_count: int, created_at: str, page_number: int = None, section_heading: str = None) -> dict:
        self._execute(
            "INSERT INTO chunks (chunk_id, workspace_id, document_id, chunk_index, chunk_text, token_count, created_at, page_number, section_heading) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (chunk_id, workspace_id, document_id, chunk_index, chunk_text, token_count, created_at, page_number, section_heading)
        )
        self._execute(
            "INSERT INTO chunks_fts (chunk_id, workspace_id, chunk_text) VALUES (?, ?, ?)",
            (chunk_id, workspace_id, chunk_text)
        )
        return self._execute("SELECT * FROM chunks WHERE chunk_id = ?", (chunk_id,), fetch_one=True)

    def create_chunks_batch(self, chunks_data: list[tuple]) -> None:
        """
        Atomically inserts a batch of chunks into both chunks and chunks_fts tables
        using a single database transaction and executemany.
        chunks_data: list of tuples (chunk_id, workspace_id, document_id, chunk_index, chunk_text, token_count, created_at, page_number, section_heading)
        """
        if not chunks_data:
            return
            
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT INTO chunks (chunk_id, workspace_id, document_id, chunk_index, chunk_text, token_count, created_at, page_number, section_heading) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                chunks_data
            )
            fts_data = [(c[0], c[1], c[4]) for c in chunks_data]
            cursor.executemany(
                "INSERT INTO chunks_fts (chunk_id, workspace_id, chunk_text) VALUES (?, ?, ?)",
                fts_data
            )


    def get_chunks_by_document(self, document_id: str) -> list[dict]:
        return self._execute(
            "SELECT * FROM chunks WHERE document_id = ? ORDER BY chunk_index ASC",
            (document_id,),
            fetch_all=True
        )

    def get_chunks_by_workspace(self, workspace_id: str) -> list[dict]:
        return self._execute(
            "SELECT * FROM chunks WHERE workspace_id = ? ORDER BY document_id, chunk_index ASC",
            (workspace_id,),
            fetch_all=True
        )

    def get_chunks_by_ids(self, chunk_ids: list[str]) -> list[dict]:
        if not chunk_ids:
            return []
        placeholders = ",".join(["?"] * len(chunk_ids))
        return self._execute(
            f"SELECT * FROM chunks WHERE chunk_id IN ({placeholders})",
            tuple(chunk_ids),
            fetch_all=True
        )

    def get_front_matter_and_toc_chunks(self, workspace_id: str, limit: int = 10) -> list[dict]:
        """
        Retrieves front-matter (pages 1-10) and chunks containing structural markers
        (CONTENTS, Chapter, Unit, Syllabus, Table of Contents) for global overview queries.
        """
        query = """
            SELECT * FROM chunks 
            WHERE workspace_id = ? AND (
                page_number <= 10 
                OR chunk_text LIKE '%CONTENTS%' 
                OR chunk_text LIKE '%Table of Contents%' 
                OR chunk_text LIKE '%Chapter 1%' 
                OR chunk_text LIKE '%Unit I%'
            )
            ORDER BY page_number ASC, chunk_index ASC
            LIMIT ?
        """
        return self._execute(query, (workspace_id, limit), fetch_all=True)

    def update_embedding_ref(self, chunk_id: str, embedding_ref: str):
        self._execute(
            "UPDATE chunks SET embedding_ref = ? WHERE chunk_id = ?",
            (embedding_ref, chunk_id)
        )

    def delete_chunks_by_document(self, document_id: str):
        # Delete from FTS virtual table first by matching chunk ids
        self._execute(
            "DELETE FROM chunks_fts WHERE chunk_id IN (SELECT chunk_id FROM chunks WHERE document_id = ?)",
            (document_id,)
        )
        self._execute(
            "DELETE FROM chunks WHERE document_id = ?",
            (document_id,)
        )
