import sqlite3


def create_schema(conn: sqlite3.Connection):

    # workspaces table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS workspaces (
            workspace_id TEXT PRIMARY KEY,
            workspace_name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            total_documents INTEGER DEFAULT 0,
            total_chunks INTEGER DEFAULT 0,
            storage_used_mb REAL DEFAULT 0.0
        )
    """)

    # documents table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            document_id TEXT PRIMARY KEY,
            workspace_id TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_size_mb REAL DEFAULT 0.0,
            upload_time TEXT NOT NULL,
            processing_status TEXT DEFAULT 'pending',
            total_chunks INTEGER DEFAULT 0,
            embedding_status INTEGER DEFAULT 0,
            file_path TEXT,
            FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_workspace_id ON documents(workspace_id)")

    # chunks table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id TEXT PRIMARY KEY,
            workspace_id TEXT NOT NULL,
            document_id TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            chunk_text TEXT NOT NULL,
            embedding_ref TEXT,
            token_count INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            page_number INTEGER,
            section_heading TEXT,
            FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
            FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_workspace_doc ON chunks(workspace_id, document_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_workspace_id ON chunks(workspace_id)")

    # FTS5 Virtual Table for lexical search scoring
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
            chunk_id UNINDEXED,
            workspace_id,
            chunk_text
        )
    """)

    # Automatic database backfill migration for existing datasets
    try:
        fts_count = conn.execute("SELECT COUNT(*) FROM chunks_fts").fetchone()[0]
        if fts_count == 0:
            conn.execute("""
                INSERT INTO chunks_fts (chunk_id, workspace_id, chunk_text)
                SELECT chunk_id, workspace_id, chunk_text FROM chunks
            """)
    except Exception:
        pass

    # conversations table (core)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            message_id TEXT PRIMARY KEY,
            workspace_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            model_used TEXT,
            created_at TEXT NOT NULL,
            retrieval_chunks INTEGER DEFAULT 0,
            FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_conversations_workspace_time ON conversations(workspace_id, created_at)"
    )

    # --- CI Phase 1: Additive migrations on conversations (safe on existing data) ---
    _migrate_conversations_columns(conn)

    # --- CI Phase 1: conversation_sessions table (NEW) ---
    # Groups messages into named, user-manageable conversation threads per workspace.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversation_sessions (
            session_id    TEXT PRIMARY KEY,
            workspace_id  TEXT NOT NULL,
            session_name  TEXT NOT NULL DEFAULT 'New Conversation',
            created_at    TEXT NOT NULL,
            updated_at    TEXT NOT NULL,
            message_count INTEGER DEFAULT 0,
            is_active     INTEGER DEFAULT 1,
            FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_sessions_workspace
            ON conversation_sessions(workspace_id, updated_at DESC)
    """)

    # --- CI Phase 1: user_memory_profiles table (NEW) ---
    # Persists per-workspace behavioural memory across all sessions.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_memory_profiles (
            profile_id        TEXT PRIMARY KEY,
            workspace_id      TEXT NOT NULL UNIQUE,
            preferred_mode    TEXT DEFAULT 'medium',
            topic_familiarity TEXT,
            learning_style    TEXT DEFAULT 'balanced',
            struggle_topics   TEXT,
            session_count     INTEGER DEFAULT 0,
            last_active       TEXT NOT NULL,
            FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE
        )
    """)

    # workspace_summaries table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS workspace_summaries (
            summary_id TEXT PRIMARY KEY,
            workspace_id TEXT NOT NULL UNIQUE,
            summary_text TEXT,
            last_updated TEXT NOT NULL,
            FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE
        )
    """)

    # analytics table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analytics (
            analytics_id TEXT PRIMARY KEY,
            workspace_id TEXT NOT NULL UNIQUE,
            total_queries INTEGER DEFAULT 0,
            total_documents INTEGER DEFAULT 0,
            total_chunks INTEGER DEFAULT 0,
            total_storage_mb REAL DEFAULT 0.0,
            groq_requests INTEGER DEFAULT 0,
            local_model_requests INTEGER DEFAULT 0,
            last_updated TEXT NOT NULL,
            FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE
        )
    """)

    # --- Visual RAG: figure_chunks table (Phase 1) ---
    # Stores extracted figure crops with AI captions for semantic retrieval.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS figure_chunks (
            figure_id     TEXT PRIMARY KEY,
            workspace_id  TEXT NOT NULL,
            document_id   TEXT NOT NULL,
            page_number   INTEGER NOT NULL,
            figure_index  INTEGER NOT NULL,
            file_path     TEXT NOT NULL,
            caption_text  TEXT DEFAULT '',
            context_text  TEXT DEFAULT '',
            figure_type   TEXT DEFAULT 'unknown',
            embedding_ref TEXT DEFAULT '',
            created_at    TEXT NOT NULL,
            FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
            FOREIGN KEY (document_id)  REFERENCES documents(document_id)   ON DELETE CASCADE
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_figure_chunks_doc ON figure_chunks(document_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_figure_chunks_ws ON figure_chunks(workspace_id, page_number)"
    )

    # --- Visual RAG: additive migration — link text chunks to figures ---
    _safe_add_column(conn, "chunks", "figure_id", "TEXT")

def _migrate_conversations_columns(conn: sqlite3.Connection):
    """
    Safely adds new CI columns to the existing conversations table.
    Each column is added independently via try/except — idempotent on re-runs.
    Existing rows receive NULL or DEFAULT values; zero data loss guaranteed.
    """
    _safe_add_column(conn, "conversations", "session_id",       "TEXT")
    _safe_add_column(conn, "conversations", "turn_index",       "INTEGER DEFAULT 0")
    _safe_add_column(conn, "conversations", "topic_tags",       "TEXT")
    _safe_add_column(conn, "conversations", "importance_score", "REAL DEFAULT 0.5")
    # Composite index for fast session-scoped history fetches
    try:
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_session
                ON conversations(workspace_id, session_id, created_at)
        """)
    except Exception:
        pass


def _safe_add_column(conn: sqlite3.Connection, table: str, column: str, col_def: str):
    """Adds a column only if it does not already exist — safe idempotent migration."""
    try:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}")
    except Exception:
        pass  # Column already exists — expected on re-runs
