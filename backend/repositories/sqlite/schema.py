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
    
    # conversations table
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_workspace_time ON conversations(workspace_id, created_at)")
    
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
