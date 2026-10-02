# RAG Document Intelligence Platform — Backend & Storage Implementation Plan

> **Scope:** Backend (FastAPI) + Storage (SQLite, FAISS, BM25) — Phases 1 through 44.
> Frontend is excluded. Build and validate the entire intelligence pipeline through FastAPI Swagger before any UI work begins.
> **Goal:** Zero bugs, zero flaws, fully functional RAG pipeline at Milestone M4.

---

## How to Read This Document

Each phase is a self-contained unit of work with a clear objective, technical context explaining the rationale, an ordered list of micro-tasks that the agent executes sequentially, and a checklist to verify completion. After completing every phase, the agent must run the error verification steps before marking any checklist item done. If any verification step fails, stop, diagnose, and fix before proceeding.

Phases build linearly. Every phase depends on all previous phases being error-free. Never skip a phase or partially complete it.

---

## Pre-Implementation Setup

Before touching any code, establish the project skeleton and dependency environment. This is the scaffolding that every subsequent phase builds on.

### Folder Structure to Initialise

Create the following directory tree from the project root. Every directory must exist before Phase 1 begins. Use `mkdir -p` for nested paths.

```
project-root/
├── backend/
│   ├── api/
│   │   ├── workspace/
│   │   ├── document/
│   │   ├── chat/
│   │   ├── analytics/
│   │   └── system/
│   ├── services/
│   │   ├── workspace/
│   │   ├── document/
│   │   │   ├── extractors/
│   │   │   └── chunking/
│   │   ├── retrieval/
│   │   ├── memory/
│   │   ├── llm/
│   │   └── analytics/
│   ├── repositories/
│   │   ├── sqlite/
│   │   ├── vector/
│   │   └── bm25/
│   ├── providers/
│   │   ├── embeddings/
│   │   ├── groq/
│   │   └── qwen/
│   ├── schemas/
│   ├── models/
│   ├── core/
│   │   ├── config/
│   │   ├── logging/
│   │   ├── exceptions/
│   │   └── startup/
│   ├── utils/
│   ├── tests/
│   └── logs/
├── storage/
│   ├── uploads/
│   │   └── workspaces/
│   ├── sqlite/
│   ├── vectors/
│   │   └── faiss/
│   ├── bm25/
│   ├── cache/
│   └── exports/
├── secrets/
│   └── templates/
└── docs/
```

Place an empty `__init__.py` inside every Python package directory under `backend/`. That means every single directory inside `backend/` must have its own `__init__.py` file so Python treats them as importable packages. This is not optional — missing `__init__.py` files cause silent import failures.

### Python Environment

Create a Python 3.11 virtual environment at the project root (`python3.11 -m venv .venv`). Activate it before installing anything.

### Requirements File

Create `requirements.txt` at the project root with the following dependencies. Pin exact major versions to avoid breaking changes mid-development:

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
pydantic==2.8.0
pydantic-settings==2.4.0
python-dotenv==1.0.1
python-multipart==0.0.9
aiofiles==24.1.0
pdfplumber==0.11.4
python-docx==1.1.2
sentence-transformers==3.1.0
faiss-cpu==1.8.0
rank-bm25==0.2.2
tiktoken==0.7.0
numpy==1.26.4
groq==0.11.0
transformers==4.44.0
torch==2.4.0
scikit-learn==1.5.1
```

Install with `pip install -r requirements.txt`. Confirm installation completes with zero errors before Phase 1.

### Secrets File

Create `secrets/.env` with the following template. Do not put actual keys in version control.

```env
GROQ_API_KEY=your_groq_api_key_here
HF_TOKEN=your_huggingface_token_here

DATABASE_PATH=storage/sqlite/app.db
UPLOADS_PATH=storage/uploads/workspaces
FAISS_PATH=storage/vectors/faiss
BM25_PATH=storage/bm25
LOGS_PATH=backend/logs

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CROSS_ENCODER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
GROQ_MODEL_MEDIUM=llama3-8b-8192
GROQ_MODEL_EXPERT=llama3-70b-8192
LOCAL_MODEL_NAME=qwen2.5:3b

CHUNK_SIZE=512
CHUNK_OVERLAP=100
CHUNK_MIN_SIZE=100
FAISS_TOP_K=50
BM25_TOP_K=50
RRF_CONSTANT=60
RRF_TOP_N=20
CROSS_ENCODER_TOP_N=5
CROSS_ENCODER_MIN_SCORE=0.60
CONTEXT_MAX_CHUNKS=5
RECENT_CHAT_WINDOW=5
SUMMARY_UPDATE_INTERVAL=10

ENABLE_BM25=true
ENABLE_RRF=true
ENABLE_CROSS_ENCODER=true
ENABLE_LOCAL_MODEL=true
LOG_LEVEL=INFO
```

---

## Phase 1 — Project Foundation

**Objective:** Initialize the FastAPI application with configuration management, structured logging, and a startup lifecycle so that the server boots cleanly and all subsystems have a single source of truth for configuration.

**Technical Context:**

The FastAPI application is the central orchestration point of this entire system. Before any domain logic is written, the foundation must be rock-solid. The three concerns to address in this phase are: (1) how the application reads its configuration from environment variables, (2) how the application produces observable logs, and (3) how the application initializes and tears down resources gracefully at startup and shutdown.

Configuration uses `pydantic-settings` which reads from the `.env` file and validates types automatically. This is better than raw `os.getenv` because it gives you type safety, default values, and a single `Settings` object that all other modules import. The settings object is created once at module load time using the singleton pattern — you define a `get_settings()` function with `lru_cache` so the settings file is read exactly once per process lifetime.

Logging is set up using Python's standard `logging` module with a formatted handler. Every module in the application will import a logger using `logging.getLogger(__name__)`. The central setup in `logger.py` configures the root logger's format, level, and handlers once at startup.

The lifespan context manager (FastAPI's modern replacement for `@app.on_event`) handles startup validation: it verifies that storage directories exist, confirms the database file path is accessible, and logs the application version. This means if you start the server with a misconfigured environment, it fails immediately with a clear error rather than silently at runtime.

**Files to Create:**

- `backend/core/config/settings.py` — Pydantic settings class
- `backend/core/logging/logger.py` — Logging configuration
- `backend/core/startup/lifespan.py` — FastAPI lifespan handler
- `backend/main.py` — FastAPI application factory

**Micro-Tasks:**

**Task 1.1 — Define the Settings class**

In `backend/core/config/settings.py`, define a class `Settings` that extends `pydantic_settings.BaseSettings`. Add every key from the `.env` file as a typed field. Use `Field(default=...)` where values have sensible defaults. At the bottom of the file, define a `get_settings` function that returns a cached `Settings()` instance using `functools.lru_cache`. The `model_config` on the `Settings` class must set `env_file = "secrets/.env"` and `env_file_encoding = "utf-8"`. Group fields logically with inline comments: paths, model names, retrieval config, feature flags.

The `Settings` class must expose computed path properties where needed — for example, a property `faiss_workspace_path(workspace_id: str)` that returns the full path to a workspace's FAISS index. Do not scatter path construction logic throughout the codebase; keep it in `Settings`.

**Task 1.2 — Configure structured logging**

In `backend/core/logging/logger.py`, define a function `setup_logging(log_level: str)` that configures the Python root logger. Create two handlers: a `StreamHandler` for console output and a `RotatingFileHandler` for the logs directory (with `maxBytes=10MB` and `backupCount=3`). The log format must include: timestamp, logger name, log level, and message. The format string should be `"%(asctime)s | %(name)s | %(levelname)s | %(message)s"`. After defining `setup_logging`, define a `get_logger(name: str)` helper that returns `logging.getLogger(name)`. Every module in the project gets its logger via `logger = get_logger(__name__)`.

**Task 1.3 — Implement the lifespan context manager**

In `backend/core/startup/lifespan.py`, import `contextlib.asynccontextmanager`, `fastapi.FastAPI`, and the settings and logger. Define an `asynccontextmanager` function named `lifespan(app: FastAPI)`. Inside the startup section (before `yield`): call `setup_logging`, log "Application starting", verify that all directories defined in settings (uploads, faiss, bm25, sqlite, logs) exist and create them with `os.makedirs(path, exist_ok=True)` if they do not. After all checks pass, log "All systems initialized". The shutdown section (after `yield`) should log "Application shutting down" and perform any cleanup needed.

**Task 1.4 — Assemble the FastAPI application**

In `backend/main.py`, create the FastAPI application using `FastAPI(title="RAG Document Intelligence", version="1.0.0", lifespan=lifespan)`. Add a `CORSMiddleware` with `allow_origins=["*"]` for development. Add a root health endpoint `GET /` that returns `{"status": "running", "version": "1.0.0"}`. Do not register any routers yet — those come in later phases. The application object must be importable as `from backend.main import app`.

**Error Verification — Phase 1:**

Run `uvicorn backend.main:app --reload` from the project root. The server must boot without any import errors or exceptions. Open `http://127.0.0.1:8000/` and confirm the health response. Check the `backend/logs/` directory and confirm a log file is created. Check that all storage directories were created by the lifespan. If any `ModuleNotFoundError` appears, verify all `__init__.py` files exist and the virtual environment is activated.

**Phase 1 Checklist:**
- [x] `Settings` class loads all keys from `.env` without errors
- [x] `get_settings()` returns the same object on every call (cached)
- [x] `setup_logging()` creates both console and file handlers
- [x] `lifespan` creates all required storage directories on first boot
- [x] `uvicorn backend.main:app --reload` starts without any errors
- [x] `GET /` returns `{"status": "running", "version": "1.0.0"}`
- [x] Log file appears in `backend/logs/` after first run
- [x] All `__init__.py` files exist in every `backend/` subdirectory

---

## Phase 2 — SQLite Initialization

**Objective:** Create a database connection manager that provides a reliable, reusable interface to the SQLite database with WAL mode enabled for write performance.

**Technical Context:**

SQLite is used as-is via Python's built-in `sqlite3` module. No ORM, no migration framework. The simplicity is intentional — direct SQL is easier to debug, has zero abstraction overhead, and maps clearly to the repository pattern. The connection manager is responsible for exactly one thing: opening a connection to the SQLite file and returning it with the correct configuration applied.

WAL (Write-Ahead Logging) mode must be enabled on every new connection. WAL allows concurrent reads during writes, which matters because document ingestion writes to the database while queries read from it. Enable it with `PRAGMA journal_mode=WAL`. Also enable `PRAGMA foreign_keys=ON` so that foreign key constraints are enforced — this prevents orphaned document records when a workspace is deleted.

The connection manager uses Python's context manager protocol (`__enter__` / `__exit__`). This ensures connections are always closed, even when exceptions occur. Define a function `get_connection()` that opens a connection, sets `row_factory = sqlite3.Row` (so rows behave like dictionaries), applies both PRAGMAs, and returns the connection. The `sqlite3.Row` factory is critical — it allows column access by name (`row["workspace_id"]`) rather than index, making code readable.

**Files to Create:**

- `backend/repositories/sqlite/database.py` — Connection manager

**Micro-Tasks:**

**Task 2.1 — Build the database connection function**

In `backend/repositories/sqlite/database.py`, import `sqlite3`, `contextlib`, and `get_settings`. Define a function `get_db_path()` that returns the database file path from settings. Define `get_connection()` as a regular function (not async) that opens a `sqlite3.connect(get_db_path())`, sets `row_factory = sqlite3.Row`, executes `PRAGMA journal_mode=WAL`, executes `PRAGMA foreign_keys=ON`, and returns the connection object.

Define a context manager `db_connection()` using `@contextlib.contextmanager` that calls `get_connection()`, yields the connection, commits on success, rolls back on exception, and always closes the connection in the `finally` block. The rollback-on-exception logic is critical for data consistency: if any operation in a repository method fails partway through, the entire transaction is rolled back cleanly.

**Task 2.2 — Verify database file creation**

Add an `initialize_database()` function that simply calls `get_connection()`, executes `SELECT 1`, closes the connection, and returns `True`. Call this from the lifespan in `backend/core/startup/lifespan.py` as a smoke test during startup. If the SQLite file does not exist, `sqlite3.connect()` creates it automatically — this is expected behavior.

**Error Verification — Phase 2:**

Add a call to `initialize_database()` in the lifespan and restart the server. Confirm that `storage/sqlite/app.db` is created. Connect to it manually with `sqlite3 storage/sqlite/app.db` and run `.tables` — it should return empty (no tables yet). Run `PRAGMA journal_mode;` and confirm the result is `wal`. If the database path is wrong, check settings and confirm the path is relative to the project root or absolute.

**Phase 2 Checklist:**
- [x] `storage/sqlite/app.db` is created on server startup
- [x] `PRAGMA journal_mode` returns `wal`
- [x] `PRAGMA foreign_keys` returns `1`
- [x] `db_connection()` context manager commits on success
- [x] `db_connection()` context manager rolls back on exception
- [x] `initialize_database()` is called from lifespan without error

---

## Phase 3 — Database Schema

**Objective:** Define and execute all DDL statements to create the six core tables with proper indexes, foreign keys, and constraints so the data model is ready for the repository layer.

**Technical Context:**

All six tables must be created in a single `create_schema()` function using `CREATE TABLE IF NOT EXISTS` so that running it repeatedly on an already-initialized database is safe. The `IF NOT EXISTS` guard is the simplest possible migration strategy for a prototype — it lets you restart the server freely without errors.

Foreign key relationships enforce workspace isolation at the database level. Every table except `workspaces` has a `workspace_id` column with a `FOREIGN KEY` referencing `workspaces(workspace_id)`. When a workspace is deleted (`ON DELETE CASCADE`), all related documents, chunks, conversations, summaries, and analytics records are automatically removed. This cascade behavior eliminates the need for manual cleanup logic in the service layer.

Indexes on `workspace_id` columns are essential for query performance. Every query in this system filters by workspace — without indexes, every query would perform a full table scan. Add composite indexes where queries filter by both workspace and another column, such as `(workspace_id, document_id)` on the chunks table.

Use UUID strings (stored as `TEXT`) for all primary keys. Generate UUIDs in Python using `uuid.uuid4()` before inserting — do not rely on SQLite's `AUTOINCREMENT`. This keeps IDs consistent across storage backends (SQLite, FAISS, BM25) since you'll use the same chunk UUIDs everywhere.

**Files to Create:**

- `backend/repositories/sqlite/schema.py` — All DDL statements and the `create_schema()` function

**Micro-Tasks:**

**Task 3.1 — Define the workspaces table**

The `workspaces` table must have: `workspace_id TEXT PRIMARY KEY`, `workspace_name TEXT NOT NULL`, `description TEXT`, `created_at TEXT NOT NULL` (ISO format string), `updated_at TEXT NOT NULL`, `status TEXT DEFAULT 'active'`, `total_documents INTEGER DEFAULT 0`, `total_chunks INTEGER DEFAULT 0`, `storage_used_mb REAL DEFAULT 0.0`. Add a `UNIQUE` constraint on `workspace_name` to prevent duplicate names.

**Task 3.2 — Define the documents table**

The `documents` table must have: `document_id TEXT PRIMARY KEY`, `workspace_id TEXT NOT NULL`, `file_name TEXT NOT NULL`, `file_type TEXT NOT NULL`, `file_size_mb REAL DEFAULT 0.0`, `upload_time TEXT NOT NULL`, `processing_status TEXT DEFAULT 'pending'`, `total_chunks INTEGER DEFAULT 0`, `embedding_status INTEGER DEFAULT 0` (0=false, 1=true), `file_path TEXT`. Add `FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE`. Add an index on `workspace_id`.

**Task 3.3 — Define the chunks table**

The `chunks` table must have: `chunk_id TEXT PRIMARY KEY`, `workspace_id TEXT NOT NULL`, `document_id TEXT NOT NULL`, `chunk_index INTEGER NOT NULL`, `chunk_text TEXT NOT NULL`, `embedding_ref TEXT`, `token_count INTEGER DEFAULT 0`, `created_at TEXT NOT NULL`, `page_number INTEGER`, `section_heading TEXT`. Add foreign keys on both `workspace_id` and `document_id`. Add a composite index on `(workspace_id, document_id)` and a separate index on `workspace_id` alone for workspace-wide retrieval operations.

**Task 3.4 — Define the conversations table**

The `conversations` table must have: `message_id TEXT PRIMARY KEY`, `workspace_id TEXT NOT NULL`, `role TEXT NOT NULL`, `message TEXT NOT NULL`, `model_used TEXT`, `created_at TEXT NOT NULL`, `retrieval_chunks INTEGER DEFAULT 0`. Add foreign key on `workspace_id`. Add an index on `(workspace_id, created_at)` for efficient chronological conversation retrieval.

**Task 3.5 — Define the workspace_summaries table**

The `workspace_summaries` table must have: `summary_id TEXT PRIMARY KEY`, `workspace_id TEXT NOT NULL UNIQUE`, `summary_text TEXT`, `last_updated TEXT NOT NULL`. The `UNIQUE` constraint on `workspace_id` enforces one summary per workspace — use `INSERT OR REPLACE` when updating summaries.

**Task 3.6 — Define the analytics table**

The `analytics` table must have: `analytics_id TEXT PRIMARY KEY`, `workspace_id TEXT NOT NULL UNIQUE`, `total_queries INTEGER DEFAULT 0`, `total_documents INTEGER DEFAULT 0`, `total_chunks INTEGER DEFAULT 0`, `total_storage_mb REAL DEFAULT 0.0`, `groq_requests INTEGER DEFAULT 0`, `local_model_requests INTEGER DEFAULT 0`, `last_updated TEXT NOT NULL`.

**Task 3.7 — Implement create_schema()**

In `schema.py`, define `create_schema()` that accepts a `connection` parameter. Execute all six `CREATE TABLE IF NOT EXISTS` statements and all `CREATE INDEX IF NOT EXISTS` statements in the correct order (parent tables before child tables: workspaces first, then documents, chunks, conversations, summaries, analytics). Call `create_schema()` from the lifespan in `lifespan.py` after `initialize_database()`, passing a connection from `db_connection()`.

**Error Verification — Phase 3:**

Restart the server. Connect to `storage/sqlite/app.db` with `sqlite3`. Run `.tables` — all six tables must appear. Run `.schema workspaces` and verify constraints. Run `PRAGMA foreign_key_list(documents)` and verify the cascade rule. Run `.indices documents` and verify indexes exist. Try inserting a document with a nonexistent `workspace_id` and confirm it fails with a foreign key error.

**Phase 3 Checklist:**
- [x] All six tables created on startup
- [x] All `FOREIGN KEY ... ON DELETE CASCADE` constraints defined
- [x] All `workspace_id` columns indexed
- [x] `workspace_summaries.workspace_id` has UNIQUE constraint
- [x] `analytics.workspace_id` has UNIQUE constraint
- [x] `workspaces.workspace_name` has UNIQUE constraint
- [x] Foreign key violation is correctly rejected
- [x] `create_schema()` is idempotent (safe to run multiple times)

---

## Phase 4 — Repository Layer

**Objective:** Build the complete data access layer with five repository classes that handle all CRUD operations against the six SQLite tables, fully isolating SQL from business logic.

**Technical Context:**

The repository pattern is the boundary between business logic (services) and storage (SQLite). Services never write SQL — they call repository methods that return domain objects. This separation means if you ever swap SQLite for another database, only repository files change.

Define a `BaseRepository` with a method `_execute(sql, params, fetch_one=False, fetch_all=False)` that obtains a `db_connection()`, executes the SQL, and returns appropriately fetched results. All repositories inherit from `BaseRepository` and call `self._execute()` internally. This keeps connection management in one place.

Every repository method converts raw `sqlite3.Row` results to Python dicts immediately using `dict(row)`. Do not pass `Row` objects to the service layer — they are an implementation detail of the storage layer. Services work with plain dicts or domain model objects.

Date-time values are stored as ISO 8601 strings (`datetime.utcnow().isoformat()`) because SQLite has no native datetime type. Always generate timestamps in UTC. When reading them back, parse them with `datetime.fromisoformat()` if you need datetime objects.

**Files to Create:**

- `backend/repositories/sqlite/base_repository.py`
- `backend/repositories/sqlite/workspace_repository.py`
- `backend/repositories/sqlite/document_repository.py`
- `backend/repositories/sqlite/chunk_repository.py`
- `backend/repositories/sqlite/conversation_repository.py`
- `backend/repositories/sqlite/analytics_repository.py`

**Micro-Tasks:**

**Task 4.1 — Build BaseRepository**

In `base_repository.py`, define class `BaseRepository`. Define `_execute(self, sql: str, params: tuple = (), fetch_one: bool = False, fetch_all: bool = False, commit: bool = True)`. Inside, use `db_connection()` as a context manager. Execute the SQL with params. If `fetch_one`, call `cursor.fetchone()` and return `dict(row)` if row is not None, else `None`. If `fetch_all`, call `cursor.fetchall()` and return `[dict(r) for r in rows]`. If neither, return the `cursor.lastrowid` or `cursor.rowcount`. This single method handles every database operation pattern in the system.

**Task 4.2 — Build WorkspaceRepository**

In `workspace_repository.py`, define `WorkspaceRepository(BaseRepository)` with methods:
- `create_workspace(workspace_id, name, description) -> dict` — insert and return the new record.
- `get_workspace(workspace_id) -> dict | None` — fetch single by primary key.
- `get_all_workspaces() -> list[dict]` — fetch all, ordered by `created_at DESC`.
- `update_workspace(workspace_id, **fields)` — dynamic update using the fields dict to build SET clause.
- `delete_workspace(workspace_id) -> bool` — delete by primary key, return whether a row was deleted.
- `workspace_exists(workspace_id) -> bool` — fast existence check.
- `increment_document_count(workspace_id, delta=1)` — `UPDATE workspaces SET total_documents = total_documents + ? WHERE workspace_id = ?`.
- `increment_chunk_count(workspace_id, delta)` — same pattern for chunks.

**Task 4.3 — Build DocumentRepository**

In `document_repository.py`, define `DocumentRepository(BaseRepository)` with methods:
- `create_document(document_id, workspace_id, file_name, file_type, file_size_mb, file_path) -> dict`
- `get_document(document_id) -> dict | None`
- `get_documents_by_workspace(workspace_id) -> list[dict]`
- `update_processing_status(document_id, status: str)` — valid values: `pending`, `processing`, `completed`, `failed`.
- `update_chunk_stats(document_id, total_chunks, embedding_status=True)`
- `delete_document(document_id) -> bool`

**Task 4.4 — Build ChunkRepository**

In `chunk_repository.py`, define `ChunkRepository(BaseRepository)` with methods:
- `create_chunk(chunk_id, workspace_id, document_id, chunk_index, chunk_text, token_count, page_number=None, section_heading=None) -> dict`
- `get_chunks_by_document(document_id) -> list[dict]`
- `get_chunks_by_workspace(workspace_id) -> list[dict]` — used to reconstruct BM25 corpus.
- `get_chunks_by_ids(chunk_ids: list[str]) -> list[dict]` — used in source attribution; uses `WHERE chunk_id IN (?,?,?)`.
- `update_embedding_ref(chunk_id, embedding_ref: str)` — stores the FAISS index position as reference.
- `delete_chunks_by_document(document_id)`

**Task 4.5 — Build ConversationRepository**

In `conversation_repository.py`, define `ConversationRepository(BaseRepository)` with methods:
- `save_message(message_id, workspace_id, role, message, model_used=None, retrieval_chunks=0) -> dict`
- `get_recent_messages(workspace_id, limit=5) -> list[dict]` — `ORDER BY created_at DESC LIMIT ?` then reverse in Python for chronological order.
- `get_all_messages(workspace_id) -> list[dict]` — for summarization.
- `get_message_count(workspace_id) -> int`
- `delete_conversation(workspace_id)` — for workspace cleanup.

**Task 4.6 — Build AnalyticsRepository**

In `analytics_repository.py`, define `AnalyticsRepository(BaseRepository)` with methods:
- `init_analytics(workspace_id) -> dict` — insert initial zero-value row for a new workspace.
- `get_analytics(workspace_id) -> dict | None`
- `increment_query_count(workspace_id)`
- `increment_groq_requests(workspace_id)`
- `increment_local_requests(workspace_id)`
- `update_storage_stats(workspace_id, total_documents, total_chunks, total_storage_mb)`

**Error Verification — Phase 4:**

Write a simple test script at `backend/tests/test_repositories.py`. Create a workspace, retrieve it, update it, and delete it. Create a document inside a workspace, verify it returns in `get_documents_by_workspace`, then delete the workspace and confirm the document is gone via cascade. Run: `python -m pytest backend/tests/test_repositories.py -v`. All operations must succeed without SQL errors.

**Phase 4 Checklist:**
- [x] `BaseRepository._execute` handles fetch_one, fetch_all, and write modes
- [x] All five repositories inherit from `BaseRepository`
- [x] `WorkspaceRepository.delete_workspace` cascades to documents via SQLite
- [x] `ConversationRepository.get_recent_messages` returns messages in chronological order
- [x] `AnalyticsRepository.init_analytics` creates a zero-row on new workspace
- [x] Repository test script runs without errors
- [x] No SQL is written outside of repository files

---

## Phase 5 — Workspace Service

**Objective:** Build the workspace business logic layer that orchestrates repository operations, enforces validation rules, manages the workspace directory on disk, and initializes dependent storage resources for each new workspace.

**Technical Context:**

The workspace service is responsible for the complete workspace lifecycle. When a workspace is created, four things must happen atomically from the user's perspective: (1) the database row is inserted, (2) an analytics row is initialized, (3) the upload directory `storage/uploads/workspaces/{workspace_id}/` is created on disk, and (4) the workspace is logged. If any step fails, the workspace creation should be treated as failed — delete the partially created row if the directory creation fails.

Workspace names are validated for uniqueness. The service checks `workspace_exists_by_name()` before calling the repository, returning a clear error rather than relying on the UNIQUE constraint to throw a database exception (though the constraint is still there as a safety net).

The workspace service imports `WorkspaceRepository` and `AnalyticsRepository` directly (no dependency injection framework needed — this is Python, just instantiate them). Define both as instance attributes on the service class.

**Files to Create:**

- `backend/models/workspace.py` — Workspace domain model
- `backend/services/workspace/workspace_service.py`

**Micro-Tasks:**

**Task 5.1 — Define the Workspace domain model**

In `backend/models/workspace.py`, define a Python dataclass `Workspace` with all fields matching the database schema. Use `@dataclasses.dataclass`. This is the internal domain object that services pass between each other. It is distinct from the Pydantic schemas used for API validation. Include a class method `from_dict(data: dict) -> Workspace` that constructs a Workspace from a repository-returned dict.

**Task 5.2 — Build WorkspaceService**

In `workspace_service.py`, define class `WorkspaceService`. Initialize `self.workspace_repo = WorkspaceRepository()` and `self.analytics_repo = AnalyticsRepository()` in `__init__`. Define the following methods:

`create_workspace(name: str, description: str = "") -> dict`: Validate the name is not empty and does not already exist. Generate a UUID with `str(uuid.uuid4())`. Call `workspace_repo.create_workspace(...)`. Call `analytics_repo.init_analytics(workspace_id)`. Create the directory `{UPLOADS_PATH}/{workspace_id}` using `os.makedirs(..., exist_ok=True)`. Return the created workspace dict. If directory creation fails, call `workspace_repo.delete_workspace(workspace_id)` and raise an exception.

`get_workspace(workspace_id: str) -> dict`: Fetch and return workspace, raise a `WorkspaceNotFoundException` (defined in Phase 40) if not found. For now, raise a generic `ValueError`.

`list_workspaces() -> list[dict]`: Return all workspaces from the repository.

`delete_workspace(workspace_id: str) -> bool`: Verify the workspace exists, then call `workspace_repo.delete_workspace`. Additionally, remove the upload directory and its contents using `shutil.rmtree`. Remove the FAISS index file and BM25 index file for this workspace from storage. Return `True` on success.

`workspace_exists(workspace_id: str) -> bool`: Delegates to `workspace_repo.workspace_exists`.

**Error Verification — Phase 5:**

In a Python shell or test script, instantiate `WorkspaceService` and call `create_workspace("Test Workspace")`. Confirm the database row exists, the analytics row exists, and the directory `storage/uploads/workspaces/{uuid}/` was created. Call `delete_workspace` and confirm all three are cleaned up. Try creating two workspaces with the same name and confirm the second raises an error.

**Phase 5 Checklist:**
- [x] Workspace creation inserts both workspace row and analytics row
- [x] Upload directory is created on workspace creation
- [x] Upload directory is removed on workspace deletion
- [x] Duplicate workspace name raises an error before hitting the database
- [x] FAISS and BM25 files are cleaned up on workspace deletion (no files exist yet; write the cleanup calls but they will silently pass with `if os.path.exists`)
- [x] `Workspace.from_dict()` constructs correctly from repository data

---

## Phase 6 — Workspace APIs

**Objective:** Expose workspace functionality as RESTful API endpoints with proper Pydantic request/response validation, and register the router with the main FastAPI application.

**Technical Context:**

FastAPI uses `APIRouter` for modular endpoint organization. Each domain (workspace, document, chat, analytics, system) has its own router file with its own prefix. The main `app` in `main.py` includes each router with `app.include_router(...)`.

Pydantic schemas in `backend/schemas/` are the API contract. Define separate request and response models. Never reuse a database model as an API schema — the separation ensures that internal fields (like file paths) are never accidentally exposed to clients. All schema classes use Pydantic v2 `model_config = ConfigDict(from_attributes=True)`.

HTTP status codes matter: 201 for creation, 200 for reads, 204 for successful deletion with no body, 404 for not found, 409 for conflict (duplicate name), 422 for validation errors (FastAPI handles these automatically).

**Files to Create:**

- `backend/schemas/workspace_schemas.py`
- `backend/api/workspace/router.py`

**Files to Modify:**

- `backend/main.py` — include the workspace router

**Micro-Tasks:**

**Task 6.1 — Define workspace schemas**

In `workspace_schemas.py`:
- `CreateWorkspaceRequest`: fields `workspace_name: str` (min_length=1, max_length=255), `description: str = ""`.
- `WorkspaceResponse`: all fields that should be returned to the client — omit internal file system paths.
- `WorkspaceListResponse`: field `workspaces: list[WorkspaceResponse]` and `count: int`.
- `DeleteWorkspaceResponse`: fields `success: bool`, `message: str`.

**Task 6.2 — Build the workspace router**

In `backend/api/workspace/router.py`, create `router = APIRouter(prefix="/api/v1/workspace", tags=["Workspace"])`. Instantiate `workspace_service = WorkspaceService()` at module level (service is stateless, safe to share). Define:

`POST /` — accepts `CreateWorkspaceRequest`, calls `workspace_service.create_workspace()`, returns `WorkspaceResponse` with status 201. Catch duplicate name errors and return HTTP 409.

`GET /` — returns `WorkspaceListResponse` with all workspaces.

`GET /{workspace_id}` — returns `WorkspaceResponse` or 404.

`DELETE /{workspace_id}` — calls `workspace_service.delete_workspace()`, returns 204 or 404.

**Task 6.3 — Register the router in main.py**

In `backend/main.py`, import the workspace router and call `app.include_router(workspace_router)`.

**Error Verification — Phase 6:**

Start the server. Open `http://127.0.0.1:8000/docs` in a browser. The Swagger UI must show the Workspace section with four endpoints. Test each endpoint: create a workspace, list workspaces, get by ID, delete. Confirm 201 on creation, 409 on duplicate name, 404 on invalid ID. Check that the database rows and directories are created and removed as expected.

**Phase 6 Checklist:**
- [x] Swagger UI shows `/api/v1/workspace` endpoints
- [x] `POST /api/v1/workspace` returns 201 with workspace data
- [x] `GET /api/v1/workspace` returns list with count
- [x] `GET /api/v1/workspace/{id}` returns 404 for nonexistent ID
- [x] `DELETE /api/v1/workspace/{id}` returns 204 on success
- [x] Duplicate workspace name returns 409 not 500
- [x] Validation errors (empty name) return 422 automatically

---

## Phase 7 — Document Storage

**Objective:** Build the file system storage service that manages workspace-specific upload directories and safely persists uploaded files with unique names to prevent collisions.

**Technical Context:**

Uploaded files are stored at `storage/uploads/workspaces/{workspace_id}/{document_id}_{original_filename}`. Prefixing the document UUID prevents filename collisions when multiple users upload files with identical names into the same workspace.

The storage service is concerned only with the file system — it does not touch the database. It is called by the document upload service after the database record is created. This separation keeps file system logic and database logic in different layers.

File size calculation must happen after saving the file, not from the HTTP content-length header, because multipart uploads may have an incorrect or missing content-length. Read the actual file size with `os.path.getsize()` after writing.

**Files to Create:**

- `backend/services/document/storage_service.py`

**Micro-Tasks:**

**Task 7.1 — Build StorageService**

In `storage_service.py`, define class `StorageService`. Define method `save_file(workspace_id: str, document_id: str, file_content: bytes, original_filename: str) -> tuple[str, float]`. Inside: construct the target path as `{UPLOADS_PATH}/{workspace_id}/{document_id}_{original_filename}`. Write the bytes to disk. Calculate `file_size_mb = os.path.getsize(path) / (1024 * 1024)`. Return `(file_path, file_size_mb)`.

Define method `delete_file(file_path: str) -> bool`. Check if the file exists and delete it. Return `True` if deleted, `False` if not found.

Define method `workspace_directory_exists(workspace_id: str) -> bool`. Check if `{UPLOADS_PATH}/{workspace_id}` is a directory.

**Error Verification — Phase 7:**

Instantiate `StorageService` in a test script. Create a workspace directory manually. Call `save_file` with dummy byte content. Verify the file appears on disk with the correct naming scheme. Call `delete_file` and verify the file is removed.

**Phase 7 Checklist:**
- [x] Files are saved to `{UPLOADS_PATH}/{workspace_id}/{doc_id}_{filename}`
- [x] `file_size_mb` is calculated from actual file size, not headers
- [x] `delete_file` handles missing files gracefully (returns False, no exception)
- [x] `workspace_directory_exists` returns correct boolean

---

## Phase 8 — Document Upload Service

**Objective:** Build the service that receives an uploaded file, validates it, creates the database record, persists the file to disk, and enqueues the ingestion pipeline as a background task.

**Technical Context:**

The upload service is the entry point for all document ingestion. Its job is to validate the file type and size, create the pending database record, save the file to disk, and return control to the caller immediately. The actual text extraction, chunking, and embedding happen asynchronously as a background task — the user gets a `"processing"` status response within milliseconds.

File validation checks: only `application/pdf` and `application/vnd.openxmlformats-officedocument.wordprocessingml.document` MIME types are accepted. File size must not exceed 50MB (configurable). The workspace must exist.

The ingestion pipeline is passed to FastAPI's `BackgroundTasks` mechanism — the upload endpoint accepts a `BackgroundTasks` parameter and adds the ingestion coroutine to it. FastAPI runs background tasks after the response is sent but within the same process. This is appropriate for a prototype.

**Files to Create:**

- `backend/services/document/upload_service.py`

**Micro-Tasks:**

**Task 8.1 — Build UploadService**

In `upload_service.py`, define class `UploadService`. Initialize `document_repo = DocumentRepository()`, `workspace_repo = WorkspaceRepository()`, `storage_service = StorageService()`.

Define `validate_file(filename: str, content_type: str, size_bytes: int) -> None`. Raise `ValueError` if the file type is not PDF or DOCX. Raise `ValueError` if size exceeds 50MB.

Define `upload_document(workspace_id: str, file_content: bytes, filename: str, content_type: str) -> dict`. Steps: (1) validate the workspace exists; (2) validate the file; (3) generate `document_id = str(uuid.uuid4())`; (4) create the database record with status `"pending"`; (5) save file to disk via `storage_service.save_file`; (6) update the document record with the file path and size; (7) return the document dict. Do not trigger ingestion here — that is the caller's responsibility.

Define a helper `get_file_type(content_type: str) -> str` that maps content type strings to `"pdf"` or `"docx"`.

**Error Verification — Phase 8:**

Test with a small PDF file. Verify the database record appears with `processing_status = "pending"`. Verify the file is saved to the correct path. Verify invalid file types raise errors before any database writes occur.

**Phase 8 Checklist:**
- [x] MIME type validation runs before any write operation
- [x] File size validation runs before any write operation
- [x] Document record is created with `processing_status = "pending"`
- [x] File is saved with correct naming scheme
- [x] File size is updated in the document record after saving

---

## Phase 9 — Document APIs

**Objective:** Expose document upload, status polling, and listing endpoints and wire the background ingestion task to fire automatically after a successful upload.

**Technical Context:**

The upload endpoint is a `POST` that accepts `multipart/form-data` with two fields: `workspace_id` (a form field) and `file` (the file upload). FastAPI handles multipart via `UploadFile` and `Form`. Read the entire file into memory with `await file.read()` — this is fine for the 50MB limit since the prototype runs on a single machine.

The `BackgroundTasks` parameter is injected by FastAPI automatically when you declare it as an endpoint parameter. Adding a task to it schedules execution after the response is sent. Pass the `ingestion_service.ingest_document(document_id, workspace_id)` call as the background task.

The status endpoint is essential for the frontend (and for testing) to poll ingestion progress. It returns the document's `processing_status` field which transitions from `"pending"` → `"processing"` → `"completed"` or `"failed"`.

**Files to Create:**

- `backend/schemas/document_schemas.py`
- `backend/api/document/router.py`

**Files to Modify:**

- `backend/main.py` — include document router

**Micro-Tasks:**

**Task 9.1 — Define document schemas**

In `document_schemas.py`:
- `DocumentUploadResponse`: `success: bool`, `document_id: str`, `status: str`, `message: str`.
- `DocumentStatusResponse`: `document_id: str`, `workspace_id: str`, `processing_status: str`, `total_chunks: int`, `embedding_status: bool`, `file_name: str`.
- `DocumentListResponse`: `documents: list[DocumentStatusResponse]`, `count: int`.

**Task 9.2 — Build the document router**

In `backend/api/document/router.py`, create `router = APIRouter(prefix="/api/v1/document", tags=["Document"])`.

`POST /upload` — async endpoint with parameters `background_tasks: BackgroundTasks`, `workspace_id: str = Form(...)`, `file: UploadFile = File(...)`. Read file bytes, call `upload_service.upload_document(...)`, add `ingestion_service.ingest_document(document_id, workspace_id)` to `background_tasks`, return `DocumentUploadResponse` with status 202 (Accepted).

`GET /status/{document_id}` — returns `DocumentStatusResponse` or 404.

`GET /workspace/{workspace_id}` — returns `DocumentListResponse` for all documents in the workspace.

Note: `ingestion_service` will be imported from `backend/services/document/ingestion_service.py` which is built in Phase 13. For now, define a stub `IngestionService` with an async `ingest_document(document_id, workspace_id)` method that just logs "ingestion not yet implemented". This lets the API layer compile and work before the ingestion pipeline is ready.

**Error Verification — Phase 9:**

Use Swagger UI to upload a small PDF to an existing workspace. Confirm the response is 202 with a document ID and `"processing"` status. Call the status endpoint and confirm it returns `"pending"` (since ingestion is stubbed). Call the list endpoint and confirm the document appears. Try uploading to a nonexistent workspace and confirm 404. Try uploading a `.txt` file and confirm 400.

**Phase 9 Checklist:**
- [x] File upload via Swagger works end-to-end
- [x] Background task fires without crashing (stub logs to console)
- [x] Status endpoint returns current `processing_status`
- [x] Document list returns all documents for workspace
- [x] Uploading to nonexistent workspace returns 404
- [x] Wrong file type returns 400 or 422

---

## Phase 10 — Text Extraction Engine

**Objective:** Build PDF and DOCX extractor classes that convert uploaded files into clean raw text with page-level metadata, using a common extractor interface.

**Technical Context:**

Text extraction is the first step of the ingestion pipeline. The goal is to get as much clean, structured text out of a document as possible while preserving useful metadata like page numbers and headings. Different file types require different libraries and different strategies.

For PDFs, use `pdfplumber` (preferred over PyPDF2 for better text accuracy, especially with columns and tables). Open the PDF and extract text page by page, preserving page numbers. Strip excessive whitespace but retain paragraph breaks. For DOCX, use `python-docx` and iterate over paragraphs, preserving heading information by checking `paragraph.style.name`.

Both extractors implement a common `BaseExtractor` abstract class with a single `extract(file_path: str) -> ExtractionResult` method. The `ExtractionResult` dataclass carries `full_text: str`, `pages: list[PageContent]` (page number + text for PDFs), and `metadata: dict` (document-level metadata like title, author if available).

This abstraction means the ingestion pipeline does not care whether it is processing PDF or DOCX — it calls `extractor.extract()` and gets an `ExtractionResult` back.

**Files to Create:**

- `backend/services/document/extractors/base_extractor.py`
- `backend/services/document/extractors/pdf_extractor.py`
- `backend/services/document/extractors/docx_extractor.py`
- `backend/services/document/extractors/extractor_factory.py`

**Micro-Tasks:**

**Task 10.1 — Define base extractor and result types**

In `base_extractor.py`, define dataclass `PageContent` with `page_number: int` and `text: str`. Define dataclass `ExtractionResult` with `full_text: str`, `pages: list[PageContent]`, `metadata: dict`, `total_pages: int`, `extraction_success: bool`. Define abstract class `BaseExtractor` with abstract method `extract(file_path: str) -> ExtractionResult`.

**Task 10.2 — Build PDFExtractor**

In `pdf_extractor.py`, define `PDFExtractor(BaseExtractor)`. In `extract()`: open with `pdfplumber.open(file_path)`. Iterate over `pdf.pages`, call `page.extract_text()` for each, creating a `PageContent` for each. Handle `None` returns from `extract_text()` by substituting empty string. Join all page texts with `"\n\n"` for `full_text`. Extract metadata from `pdf.metadata` dict. Wrap everything in a try-except — if pdfplumber raises any error, return `ExtractionResult(extraction_success=False, ...)`.

**Task 10.3 — Build DOCXExtractor**

In `docx_extractor.py`, define `DOCXExtractor(BaseExtractor)`. In `extract()`: open with `docx.Document(file_path)`. Iterate over `document.paragraphs`. For each paragraph, check the style name to detect headings (`"Heading 1"`, `"Heading 2"`, etc.). Collect heading-prefixed text. Since DOCX has no pages, create a single `PageContent` with `page_number=1` and the full text. Extract core properties from `document.core_properties` for metadata.

**Task 10.4 — Build ExtractorFactory**

In `extractor_factory.py`, define `ExtractorFactory` with static method `get_extractor(file_type: str) -> BaseExtractor`. Returns `PDFExtractor()` for `"pdf"` and `DOCXExtractor()` for `"docx"`. Raises `ValueError` for unknown types.

**Error Verification — Phase 10:**

Test with a real PDF: `ExtractorFactory.get_extractor("pdf").extract("path/to/test.pdf")`. Confirm `extraction_success=True`, `full_text` is non-empty, and `pages` list has correct count. Test with a DOCX. Try with a corrupted PDF and confirm `extraction_success=False` rather than an unhandled exception.

**Phase 10 Checklist:**
- [x] `PDFExtractor` extracts text page-by-page from a real PDF
- [x] `DOCXExtractor` extracts text and detects headings from a real DOCX
- [x] `ExtractionResult.extraction_success` is `False` on error, never raises unhandled exception
- [x] `ExtractorFactory` returns correct extractor type
- [x] Both extractors populate `metadata` dict

---

## Phase 11 — Text Cleaning Engine

**Objective:** Build a text cleaner that normalizes extracted raw text by removing noise, fixing encoding issues, collapsing excessive whitespace, and preserving meaningful structural elements before chunking.

**Technical Context:**

Raw text from PDFs often contains garbage characters, hyphenated line breaks, repeated spaces, Unicode control characters, and extraction artifacts like `\x0c` (form feed) characters. Cleaning must be surgical — remove noise but never destroy information that could be useful for retrieval.

The cleaning pipeline is a sequence of transformations applied in order: (1) decode/encode to fix Unicode issues, (2) remove control characters except newlines and tabs, (3) fix hyphenated line breaks (words split across lines as `"inter-\nesting"` → `"interesting"`), (4) collapse multiple spaces to single space, (5) collapse more than two consecutive newlines to exactly two (preserving paragraph boundaries), (6) strip leading/trailing whitespace from each line. Do not remove single newlines — they often indicate sentence boundaries within a paragraph.

The cleaner is a stateless utility class with a single public method `clean(text: str) -> str`. All sub-steps are private methods called in sequence.

**Files to Create:**

- `backend/services/document/text_cleaner.py`

**Micro-Tasks:**

**Task 11.1 — Build TextCleaner**

In `text_cleaner.py`, define class `TextCleaner`. Public method `clean(text: str) -> str` calls each private method in sequence and returns the final string. Define the following private methods:

`_fix_encoding(text)` — encode to `utf-8` with `errors='ignore'`, decode back to handle invalid bytes.

`_remove_control_chars(text)` — use `re.sub` to remove Unicode control characters in categories `Cc` and `Cf` except `\n`, `\r`, and `\t`. The regex pattern is `[^\S\n\r\t\x20-\x7E\x80-\xFF]` combined with a `unicodedata.category` check.

`_fix_hyphenated_breaks(text)` — replace `"(\w+)-\n(\w+)"` with `"\1\2"` to rejoin hyphenated words split across lines.

`_normalize_whitespace(text)` — replace multiple horizontal spaces with a single space using `re.sub(r'[ \t]+', ' ', text)`.

`_normalize_newlines(text)` — replace `\r\n` and `\r` with `\n`. Replace three or more consecutive newlines with exactly two newlines (`re.sub(r'\n{3,}', '\n\n', text)`).

`_strip_lines(text)` — split by `\n`, strip each line, rejoin. Remove lines that are purely whitespace.

**Error Verification — Phase 11:**

Pass a sample dirty text string containing form feed characters, hyphenated breaks, and multiple spaces. Confirm the output is clean. Verify that a paragraph with a single newline between sentences is preserved. Verify that three consecutive blank lines become exactly two.

**Phase 11 Checklist:**
- [x] Form feed characters (`\x0c`) are removed
- [x] Hyphenated line breaks are rejoined
- [x] Multiple spaces collapsed to one
- [x] Triple newlines collapsed to double newlines
- [x] Single newlines within paragraphs are preserved
- [x] Empty lines after stripping are removed

---

## Phase 12 — Chunking Engine

**Objective:** Build a recursive text splitter that divides cleaned text into overlapping token-based chunks of configurable size while respecting natural text boundaries like paragraphs, sentences, and words.

**Technical Context:**

Chunking strategy determines retrieval quality more than almost any other configuration choice. The recursive splitter works by attempting to split on natural boundaries in order of priority: paragraph breaks (`\n\n`), then single newlines, then sentences (`. `, `! `, `? `), then spaces, then characters as a last resort. It keeps splitting recursively until all pieces are within the token limit.

Token counting uses `tiktoken` with the `cl100k_base` encoding (used by GPT models and a reasonable approximation for other models). Counting by tokens rather than characters ensures that chunks stay within the embedding model's 256-token context window and the LLM's context limits.

Overlap means that consecutive chunks share `CHUNK_OVERLAP` tokens at their boundaries. This prevents important context from being split across chunk boundaries where neither chunk has the complete sentence. Implement overlap by carrying the last `CHUNK_OVERLAP` tokens from the previous chunk forward into the next chunk's text.

Each chunk carries metadata: `chunk_index` (position in document), `token_count`, `source_text` (the raw chunk text). The chunker does not interact with the database — it returns a list of `ChunkData` objects.

**Files to Create:**

- `backend/services/document/chunking/token_counter.py`
- `backend/services/document/chunking/recursive_chunker.py`

**Micro-Tasks:**

**Task 12.1 — Build TokenCounter**

In `token_counter.py`, define class `TokenCounter`. Initialize with `self.encoder = tiktoken.get_encoding("cl100k_base")`. Define `count(text: str) -> int` that returns `len(self.encoder.encode(text))`. Define `truncate(text: str, max_tokens: int) -> str` that encodes the text, slices the first `max_tokens` tokens, and decodes back.

**Task 12.2 — Build RecursiveChunker**

In `recursive_chunker.py`, define `@dataclasses.dataclass ChunkData` with `text: str`, `chunk_index: int`, `token_count: int`. Define class `RecursiveChunker`.

Initialize with `chunk_size` (from settings, default 512), `chunk_overlap` (default 100), `min_chunk_size` (default 100). Also initialize a `TokenCounter` instance.

Define the main public method `chunk(text: str) -> list[ChunkData]`.

Internally, define `_split_text(text: str, separators: list[str]) -> list[str]`. The separators list is `["\n\n", "\n", ". ", "! ", "? ", " ", ""]`. Find the first separator that splits the text into pieces. If any piece exceeds `chunk_size`, recursively split that piece using the remaining separators. Collect all pieces that are at or below `chunk_size`.

After splitting into pieces, merge them into chunks with overlap. Define `_merge_splits(splits: list[str]) -> list[ChunkData]`. Walk through splits, accumulating token counts. When adding the next split would exceed `chunk_size`, finalize the current chunk and start a new one beginning with the last `chunk_overlap` tokens of the current chunk. Skip chunks below `min_chunk_size`.

The overlap implementation: when starting a new chunk, carry forward tokens from the end of the previous chunk. Get the last `chunk_overlap` tokens using `TokenCounter.truncate` on the reversed text, then reverse again.

**Error Verification — Phase 12:**

Test with a long text (3000+ words). Verify no chunk exceeds `chunk_size` tokens. Verify the last `chunk_overlap` tokens of chunk N appear at the beginning of chunk N+1. Verify no chunk is below `min_chunk_size`. Count total chunks and verify the overlap tokens add up correctly. Test with a very short text (below `min_chunk_size`) and verify it produces exactly one chunk.

**Phase 12 Checklist:**
- [x] No chunk exceeds `CHUNK_SIZE` tokens
- [x] Consecutive chunks share approximately `CHUNK_OVERLAP` tokens at boundary
- [x] Chunks below `MIN_CHUNK_SIZE` are discarded
- [x] Chunker respects paragraph boundaries before falling back to sentence boundaries
- [x] Works on both short (< 512 tokens) and long (> 10,000 tokens) documents
- [x] Returns correct `chunk_index` starting from 0

---

## Phase 13 — Chunk Persistence and Ingestion Orchestration

**Objective:** Build the `IngestionService` that orchestrates the complete document processing pipeline — extract, clean, chunk, embed, store — and replaces the stub from Phase 9 with a functional implementation.

**Technical Context:**

The ingestion service is the pipeline orchestrator. It holds references to the extractor factory, text cleaner, chunker, chunk repository, and (in Phase 16) the vector repository. Its `ingest_document` method sequences these components in the correct order and updates the document's processing status at each stage so that the status endpoint reflects real progress.

Status progression: `"pending"` → `"processing"` (set immediately when ingestion starts) → `"completed"` or `"failed"`. Update the database after each major step so that a crash at any point leaves an auditable state.

The ingestion service stores `ChunkData` objects to SQLite via `ChunkRepository` and passes them to the embedding and FAISS layer (Phases 14-16). For now in Phase 13, it extracts, cleans, chunks, and saves to SQLite only. The embedding step is added in Phase 16 when the FAISS layer exists.

Error handling is critical here: wrap the entire pipeline in a try-except. If any step fails (including file parsing errors), catch the exception, update `processing_status` to `"failed"`, log the error with full traceback, and return without re-raising. Background task failures must be silent — they must not crash the server.

**Files to Modify:**

- `backend/services/document/ingestion_service.py` — replace stub with full implementation

**Micro-Tasks:**

**Task 13.1 — Build IngestionService**

Replace the stub `IngestionService` with a full implementation. Initialize in `__init__`: `extractor_factory = ExtractorFactory()`, `text_cleaner = TextCleaner()`, `chunker = RecursiveChunker(settings)`, `document_repo = DocumentRepository()`, `chunk_repository = ChunkRepository()`, `workspace_repo = WorkspaceRepository()`.

Define `async ingest_document(document_id: str, workspace_id: str) -> None`:
1. Set status to `"processing"` via `document_repo.update_processing_status(document_id, "processing")`.
2. Fetch the document record for file path and file type.
3. Get the correct extractor via `ExtractorFactory.get_extractor(file_type)`.
4. Call `extractor.extract(file_path)`. If `extraction_success=False`, set status to `"failed"` and return.
5. Clean the extracted text with `text_cleaner.clean(result.full_text)`.
6. Chunk the cleaned text with `chunker.chunk(cleaned_text)`.
7. For each `ChunkData`, call `chunk_repository.create_chunk(...)` with a new UUID. Store the page number from the extractor pages if available (map chunk index to page index approximately).
8. Update the document with `document_repo.update_chunk_stats(document_id, total_chunks=len(chunks))`.
9. Update workspace chunk count with `workspace_repo.increment_chunk_count(workspace_id, len(chunks))`.
10. Update workspace document count with `workspace_repo.increment_document_count(workspace_id)`.
11. **Do not set status to `"completed"` yet** — that happens after embedding in Phase 16. For now, set it to a temporary `"chunks_ready"` state so the embedding phase can pick up from here.
12. In the except block: log the full traceback, set status to `"failed"`.

**Error Verification — Phase 13:**

Upload a real PDF (minimum 5 pages). Poll the status endpoint and watch it transition from `"pending"` to `"processing"` to `"chunks_ready"`. Connect to SQLite and run `SELECT COUNT(*) FROM chunks WHERE workspace_id = '...'` — should match the number of chunks generated. Verify token counts are within the configured limits.

**Phase 13 Checklist:**
- [x] Status transitions from `"pending"` to `"processing"` to `"chunks_ready"`
- [x] Chunks are saved to SQLite with correct `workspace_id` and `document_id`
- [x] Workspace `total_chunks` counter is updated correctly
- [x] Workspace `total_documents` counter is updated correctly
- [x] Extraction failure sets status to `"failed"` without crashing the server
- [x] Any exception in ingestion is caught, logged, and status set to `"failed"`

---

## Phase 14 — Embedding Service

**Objective:** Build the embedding provider that loads the `all-MiniLM-L6-v2` Sentence Transformer model once at startup and exposes batch embedding generation for both document chunks and query text.

**Technical Context:**

The embedding model is loaded once and reused for the lifetime of the application. Loading a model takes 3-10 seconds and consumes memory — loading it on every request is unacceptable. Use a singleton pattern: the `EmbeddingProvider` is instantiated once at server startup and imported as a module-level singleton.

The `SentenceTransformer` model `all-MiniLM-L6-v2` maps text to 384-dimensional float32 vectors. For document ingestion, encode chunks in batches (batch_size=64 is a good default) to maximize GPU/CPU utilization. For query-time encoding, encode a single query string and return a single vector as a numpy array.

The embedding vectors are numpy `float32` arrays — FAISS requires `float32` specifically. Always ensure embeddings are normalized before passing to FAISS's IndexFlatIP (inner product = cosine similarity for normalized vectors). Normalize with `sklearn.preprocessing.normalize` or manual `vector / np.linalg.norm(vector)`.

**Files to Create:**

- `backend/providers/embeddings/embedding_provider.py`

**Micro-Tasks:**

**Task 14.1 — Build EmbeddingProvider**

In `embedding_provider.py`, define class `EmbeddingProvider`. In `__init__`, load `SentenceTransformer(settings.EMBEDDING_MODEL)`. Store as `self.model`. Store `self.embedding_dim = 384`.

Define `encode_documents(texts: list[str], batch_size: int = 64) -> np.ndarray`. Call `self.model.encode(texts, batch_size=batch_size, show_progress_bar=False, convert_to_numpy=True, normalize_embeddings=True)`. Returns shape `(N, 384)` float32 array. The `normalize_embeddings=True` parameter handles normalization automatically.

Define `encode_query(query: str) -> np.ndarray`. Call `self.model.encode([query], normalize_embeddings=True, convert_to_numpy=True)[0]`. Returns shape `(384,)` float32 array.

Define `get_embedding_dim() -> int`. Returns `self.embedding_dim`.

At module level, define `_embedding_provider: EmbeddingProvider | None = None` and a function `get_embedding_provider() -> EmbeddingProvider` that lazily initializes the singleton. Call `get_embedding_provider()` from the lifespan startup to preload the model at server start rather than on the first request.

**Error Verification — Phase 14:**

Call `get_embedding_provider().encode_query("test query")`. Confirm shape is `(384,)` and dtype is `float32`. Confirm the vector has unit norm (L2 norm ≈ 1.0). Call `encode_documents(["text1", "text2"])` and confirm shape is `(2, 384)`. Restart the server and confirm model loading completes without memory errors. Check that loading is logged in the startup logs.

**Phase 14 Checklist:**
- [x] Model loads once at server startup via lifespan
- [x] `encode_query` returns shape `(384,)` float32 with unit norm
- [x] `encode_documents` returns shape `(N, 384)` float32
- [x] Singleton is correctly shared across all callers
- [x] No model is reloaded on subsequent calls to `get_embedding_provider()`

---

## Phase 15 — FAISS Initialization

**Objective:** Build the FAISS index manager that creates, saves, loads, and manages one IndexFlatIP index per workspace, stored as files in `storage/vectors/faiss/`.

**Technical Context:**

FAISS `IndexFlatIP` (Inner Product) is the correct index type for normalized embeddings, where inner product equals cosine similarity. It is exact (brute-force) — no approximation — which is appropriate for a prototype where recall matters more than retrieval microseconds. Do not use `IndexIVFFlat` or any approximate index at this stage; they require training and add complexity.

Each workspace has its own FAISS index stored as a binary file: `storage/vectors/faiss/{workspace_id}.index`. Alongside each index, store a chunk ID mapping file: `storage/vectors/faiss/{workspace_id}_ids.json`. This JSON file maps FAISS integer positions (0, 1, 2, ...) to chunk UUIDs. This mapping is essential because FAISS returns integer positions, not your chunk UUIDs — you need to reverse-map positions to get the actual chunk IDs for database lookup.

The FAISS manager keeps loaded indexes in memory in a dict `self._indexes: dict[str, faiss.Index]` and the ID maps in `self._id_maps: dict[str, list[str]]`. If an index is not in memory, load it from disk. If it does not exist on disk, create a new empty one.

**Files to Create:**

- `backend/repositories/vector/faiss_manager.py`

**Micro-Tasks:**

**Task 15.1 — Build FAISSManager**

In `faiss_manager.py`, define class `FAISSManager`. Initialize `self._indexes = {}`, `self._id_maps = {}`, `self.dim = 384`, `self.faiss_path = settings.FAISS_PATH`.

Define `_get_index_path(workspace_id) -> str` and `_get_ids_path(workspace_id) -> str` as path helpers.

Define `get_index(workspace_id: str) -> tuple[faiss.Index, list[str]]`. Check `self._indexes` cache first. If not cached, check if the index file exists — if yes, load with `faiss.read_index(path)` and load the JSON IDs file. If no, create `faiss.IndexFlatIP(self.dim)` and empty IDs list. Store in cache and return.

Define `save_index(workspace_id: str) -> None`. Call `faiss.write_index(index, path)` and write the IDs list to the JSON file.

Define `add_embeddings(workspace_id: str, embeddings: np.ndarray, chunk_ids: list[str]) -> None`. Get the index. Assert `embeddings.dtype == np.float32`. Call `index.add(embeddings)`. Append chunk IDs to the IDs list. Call `save_index(workspace_id)`.

Define `search(workspace_id: str, query_vector: np.ndarray, top_k: int = 50) -> list[tuple[str, float]]`. Get the index. If index is empty (ntotal == 0), return empty list. Call `index.search(query_vector.reshape(1, -1), min(top_k, index.ntotal))`. This returns `(distances, indices)` arrays of shape `(1, K)`. Convert to list of `(chunk_id, score)` tuples by looking up `ids_list[idx]` for each returned index. Filter out indices of -1 (FAISS returns -1 for empty slots).

Define `delete_workspace_index(workspace_id: str) -> None`. Remove from cache. Delete both files if they exist.

**Error Verification — Phase 15:**

Create a FAISS manager. Add 10 random normalized float32 vectors with fake chunk IDs. Call `search` with a random query vector. Confirm you get back at most 10 `(chunk_id, score)` tuples. Confirm scores are between -1 and 1 (cosine similarity). Call `save_index`, then `delete_workspace_index` (clears cache), then `search` again — confirm the index is reloaded from disk correctly.

**Phase 15 Checklist:**
- [x] Index file is saved to `storage/vectors/faiss/{workspace_id}.index`
- [x] IDs mapping file is saved to `storage/vectors/faiss/{workspace_id}_ids.json`
- [x] Index is loaded from disk if not in memory cache
- [x] `search` returns correctly mapped `(chunk_id, score)` pairs
- [x] FAISS -1 indices (empty) are filtered from results
- [x] `delete_workspace_index` removes both files and clears cache

---

## Phase 16 — Vector Persistence

**Objective:** Build the vector repository that bridges the ingestion service and the FAISS manager, and update the ingestion pipeline to generate embeddings and add them to the FAISS index, completing the ingestion workflow.

**Technical Context:**

The vector repository wraps the FAISS manager with a cleaner interface suited to the ingestion pipeline. Its job is to receive a list of chunks from the ingestion service, call the embedding provider to generate embeddings, add those embeddings to the FAISS index, and update the chunk records in SQLite with their FAISS positions as `embedding_ref`.

After this phase, the document status transitions to `"completed"` and the system can answer queries using FAISS retrieval. This is the final step of the ingestion pipeline.

**Files to Create:**

- `backend/repositories/vector/vector_repository.py`

**Files to Modify:**

- `backend/services/document/ingestion_service.py` — add embedding and FAISS steps

**Micro-Tasks:**

**Task 16.1 — Build VectorRepository**

In `vector_repository.py`, define class `VectorRepository`. Initialize `self.faiss_manager = FAISSManager()` and `self.embedding_provider = get_embedding_provider()`.

Define `index_chunks(workspace_id: str, chunks: list[dict]) -> None`. `chunks` is a list of dicts from the chunk repository, each containing `chunk_id` and `chunk_text`. Extract texts as `[c["chunk_text"] for c in chunks]`. Call `embedding_provider.encode_documents(texts)` to get embeddings array. Call `faiss_manager.add_embeddings(workspace_id, embeddings, chunk_ids)`.

Define `search_similar(workspace_id: str, query: str, top_k: int = 50) -> list[tuple[str, float]]`. Encode the query. Call `faiss_manager.search(workspace_id, query_vector, top_k)`. Return the list of `(chunk_id, score)` tuples.

**Task 16.2 — Update IngestionService to add embedding step**

In `ingestion_service.py`, add `self.vector_repo = VectorRepository()` to `__init__`. After step 7 (chunk saved to SQLite), collect all saved chunk dicts. In a new step 8, call `self.vector_repo.index_chunks(workspace_id, chunk_dicts)`. Then update `document_repo.update_chunk_stats` with `embedding_status=True`. Finally, set document status to `"completed"` instead of `"chunks_ready"`.

Update the chunk repository's `update_embedding_ref` for each chunk with its FAISS position (the index position = chunk_index within the document is a reasonable ref string for now).

**Error Verification — Phase 16:**

Upload a new PDF. Poll the status endpoint until it returns `"completed"`. Check SQLite — `embedding_status` should be 1. Check `storage/vectors/faiss/` — both `.index` and `_ids.json` files should exist. Verify the IDs JSON contains the correct chunk UUIDs. Query FAISS directly in a Python shell using `FAISSManager().search(workspace_id, query_vector, 5)` and confirm chunk IDs are returned.

**Phase 16 Checklist:**
- [x] Document status reaches `"completed"` after successful ingestion
- [x] FAISS `.index` and `_ids.json` files exist for the workspace
- [x] All chunk UUIDs are present in the IDs mapping file
- [x] `embedding_status` is 1 (true) in the documents table
- [x] `VectorRepository.search_similar` returns `(chunk_id, score)` pairs after ingestion

---

## Phase 17 — Retrieval MVP (FAISS-Only)

**Objective:** Build the first complete retrieval service using FAISS semantic search, which fetches retrieved chunk IDs, loads the chunk texts from SQLite, and returns a structured list of relevant chunks ready for prompt construction.

**Technical Context:**

The retrieval service is what connects a user's query to the document knowledge base. At this phase, it uses FAISS-only search — no BM25, no RRF, no cross-encoder. It takes a query string, encodes it, runs semantic search, fetches the matching chunk texts from SQLite, and returns them ranked by similarity score.

The output of the retrieval service is always a list of `RetrievedChunk` objects (a dataclass with fields: `chunk_id`, `document_id`, `workspace_id`, `chunk_text`, `score`, `source_file`). This data structure is the contract between the retrieval layer and the prompt builder — it does not change as the retrieval sophistication increases in later phases.

Fetching chunk details from SQLite after FAISS search is a join operation that FAISS cannot perform. After getting `(chunk_id, score)` from FAISS, batch-fetch the chunk records from `ChunkRepository.get_chunks_by_ids(chunk_ids)`, then zip the scores back in. Preserve the FAISS ranking order.

**Files to Create:**

- `backend/models/retrieval.py` — RetrievedChunk dataclass
- `backend/services/retrieval/faiss_retriever.py`

**Micro-Tasks:**

**Task 17.1 — Define RetrievedChunk**

In `backend/models/retrieval.py`, define `@dataclasses.dataclass RetrievedChunk`: `chunk_id: str`, `document_id: str`, `workspace_id: str`, `chunk_text: str`, `score: float`, `source_file: str = ""`, `chunk_index: int = 0`. This is the universal retrieval result type used by all retrieval implementations.

**Task 17.2 — Build FAISSRetriever**

In `faiss_retriever.py`, define class `FAISSRetriever`. Initialize `self.vector_repo = VectorRepository()` and `self.chunk_repo = ChunkRepository()` and `self.doc_repo = DocumentRepository()`.

Define `retrieve(workspace_id: str, query: str, top_k: int = 50) -> list[RetrievedChunk]`. Call `vector_repo.search_similar(workspace_id, query, top_k)` to get `(chunk_id, score)` list. If empty, return empty list. Fetch chunk details for all chunk IDs using `chunk_repo.get_chunks_by_ids(chunk_ids)`. Build a dict of `chunk_id → chunk_dict` for O(1) lookup. For each `(chunk_id, score)` in the original ranked order, look up the chunk dict and fetch the document record for `file_name`. Construct and return `RetrievedChunk` objects preserving the FAISS ranking.

**Error Verification — Phase 17:**

Create a workspace, upload and ingest a PDF, then call `FAISSRetriever().retrieve(workspace_id, "your query here", top_k=5)`. Confirm the returned list has at most 5 items. Confirm each item has `chunk_text` populated. Confirm `score` values are between 0 and 1. Confirm `source_file` is the correct document filename. Verify the results are sorted by score descending.

**Phase 17 Checklist:**
- [x] `retrieve` returns `list[RetrievedChunk]` sorted by score descending
- [x] `chunk_text` is populated from SQLite for each result
- [x] `source_file` correctly identifies the source document
- [x] Empty workspace returns empty list without errors
- [x] `top_k` parameter is respected

---

## Phase 18 — Prompt Builder MVP

**Objective:** Build the first version of the prompt builder that assembles retrieved chunks, system instructions, and a user query into a structured LLM-ready prompt string.

**Technical Context:**

The prompt builder's output is a string passed directly to the LLM. The prompt must be structured to guide the model toward accurate, source-grounded answers. The structure is: System Instructions → Retrieved Evidence → User Query → Response Rules.

System instructions define the model's role and behavior: it is a document intelligence assistant, it should answer only from the provided evidence, it should cite source filenames when making specific claims, and it should explicitly say when it cannot find information in the documents.

Retrieved evidence is formatted as numbered context blocks: `[1] Source: filename.pdf\n\nchunk_text\n\n[2] Source: ...`. Each numbered block clearly marks where a piece of information came from. This formatting primes the model to generate cited responses.

Response rules are appended at the end: format the response in Markdown, use headings for complex answers, cite sources using `[1]`, `[2]` notation, and state "I could not find sufficient information in the uploaded documents" if the evidence is inadequate.

At this phase, the prompt builder does not include conversation history — that is added in Phase 35. It focuses purely on retrieval-grounded response generation.

**Files to Create:**

- `backend/services/llm/prompt_builder.py`

**Micro-Tasks:**

**Task 18.1 — Build PromptBuilder MVP**

In `prompt_builder.py`, define class `PromptBuilder`.

Define `build_system_prompt() -> str`. Return a multi-line string that: identifies the assistant as a document intelligence platform, instructs it to answer exclusively from the provided context, requires citation of source filenames, and instructs it to state insufficient information clearly rather than guessing.

Define `format_context(chunks: list[RetrievedChunk]) -> str`. If chunks is empty, return `"No relevant context found in uploaded documents."`. Otherwise, format as numbered blocks: for each chunk at index `i`, create `f"[{i+1}] Source: {chunk.source_file}\n\n{chunk.chunk_text}\n"`. Join all blocks with `"\n---\n"`.

Define `build_prompt(query: str, chunks: list[RetrievedChunk]) -> tuple[str, str]`. Return a tuple of `(system_prompt, user_prompt)`. The user prompt combines formatted context and the query: `f"Context from uploaded documents:\n\n{formatted_context}\n\nUser Question: {query}\n\nPlease answer based on the above context."`. Keep system prompt and user prompt separate because the Groq API uses a message format with distinct roles.

**Error Verification — Phase 18:**

Call `PromptBuilder().build_prompt("What is RAG?", sample_chunks)`. Print the result and verify the structure is correct. Verify that empty chunks produce the no-context message. Verify source file names appear in the context blocks.

**Phase 18 Checklist:**
- [x] `build_system_prompt` returns a substantive instruction string
- [x] `format_context` numbers blocks starting from 1
- [x] Source filenames are included in each context block
- [x] Empty chunks list returns no-context message
- [x] `build_prompt` returns a tuple of `(system_str, user_str)`

---

## Phase 19 — Groq Integration

**Objective:** Build the Groq provider that connects to the Groq API, sends structured prompts, handles responses, and manages API errors gracefully.

**Technical Context:**

The Groq Python client (`from groq import Groq`) provides a synchronous `client.chat.completions.create()` method. Use it synchronously and wrap it in `asyncio.get_event_loop().run_in_executor(None, ...)` to call it from async FastAPI endpoints without blocking. Or simply mark the calling function as synchronous — FastAPI handles sync functions in a thread pool.

The Groq API uses OpenAI-compatible message format: `[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]`. Map the two strings from the prompt builder to this format.

Always wrap Groq API calls in try-except for `groq.APIError`, `groq.AuthenticationError`, and `groq.RateLimitError`. On any Groq error, raise a custom `GroqUnavailableException` — this signals the failover manager (Phase 38) to switch to the local model. Do not let Groq exceptions propagate uncaught to the API layer.

**Files to Create:**

- `backend/providers/groq/groq_provider.py`

**Micro-Tasks:**

**Task 19.1 — Build GroqProvider**

In `groq_provider.py`, define class `GroqProvider`. In `__init__`, initialize `self.client = Groq(api_key=settings.GROQ_API_KEY)`. Store `self.model_medium = settings.GROQ_MODEL_MEDIUM` and `self.model_expert = settings.GROQ_MODEL_EXPERT`.

Define `generate(system_prompt: str, user_prompt: str, mode: str = "medium") -> str`. Select model based on mode: `"expert"` uses `model_expert`, all others use `model_medium`. Build the messages list. Call `self.client.chat.completions.create(model=model, messages=messages, max_tokens=1500, temperature=0.1)`. Extract and return `response.choices[0].message.content`.

Wrap the entire call in try-except for Groq errors. Catch `Exception` as a fallback and raise `GroqUnavailableException(str(e))`. Define `GroqUnavailableException` as a custom exception class in this file for now (will be moved to the exceptions module in Phase 40).

Define `is_available() -> bool`. Attempt a minimal API call (`max_tokens=1`). Return `True` if successful, `False` on any error.

**Error Verification — Phase 19:**

With a valid Groq API key in `.env`, call `GroqProvider().generate("You are helpful.", "What is 2+2?", mode="medium")`. Confirm a valid string response is returned. Test with an invalid API key and confirm `GroqUnavailableException` is raised rather than an unhandled error.

**Phase 19 Checklist:**
- [x] Valid API call returns a non-empty string
- [x] `mode="expert"` uses a different (larger) model than `mode="medium"`
- [x] Invalid API key raises `GroqUnavailableException`, not an uncaught exception
- [x] `is_available()` returns correct boolean
- [x] `temperature=0.1` is set for deterministic, factual responses

---

## Phase 20 — Chat API MVP

**Objective:** Build the chat service and query endpoint that connects the complete retrieval → prompt building → LLM generation pipeline end-to-end, producing the first fully functional RAG response.

**Technical Context:**

The chat service is the orchestrator for query handling. It coordinates the FAISS retriever, prompt builder, and Groq provider in sequence. It also saves the conversation to SQLite so history is maintained.

The query endpoint accepts a `workspace_id`, `query` string, and `mode` (simple/medium/expert). It validates the workspace, calls the chat service, and returns the response with metadata (model used, retrieval chunk count, processing time).

Processing time is measured with `time.time()` at the start and end of the service call, reported in milliseconds. This is useful observability data, not just for display but for identifying performance bottlenecks.

**Files to Create:**

- `backend/models/chat.py`
- `backend/schemas/chat_schemas.py`
- `backend/services/llm/chat_service.py`
- `backend/api/chat/router.py`

**Files to Modify:**

- `backend/main.py` — include chat router

**Micro-Tasks:**

**Task 20.1 — Define chat schemas**

In `chat_schemas.py`:
- `QueryRequest`: `workspace_id: str`, `query: str` (min_length=1), `mode: str = "medium"` (must be one of `"simple"`, `"medium"`, `"expert"` via Pydantic `Literal`).
- `QueryResponse`: `success: bool`, `response: str`, `model_used: str`, `retrieval_chunks: int`, `processing_time_ms: int`.
- `ChatHistoryResponse`: `messages: list[dict]`, `count: int`.

**Task 20.2 — Build ChatService**

In `chat_service.py`, define class `ChatService`. Initialize `self.retriever = FAISSRetriever()`, `self.prompt_builder = PromptBuilder()`, `self.groq_provider = GroqProvider()`, `self.conversation_repo = ConversationRepository()`, `self.workspace_service = WorkspaceService()`.

Define `handle_query(workspace_id: str, query: str, mode: str) -> dict`. Steps:
1. Verify workspace exists.
2. Retrieve relevant chunks using `self.retriever.retrieve(workspace_id, query, top_k=settings.FAISS_TOP_K)`.
3. Build prompt: `system_prompt, user_prompt = self.prompt_builder.build_prompt(query, chunks)`.
4. Generate response with Groq: `response_text = self.groq_provider.generate(system_prompt, user_prompt, mode)`.
5. Save user message and assistant response to conversation history via `conversation_repo.save_message(...)`.
6. Return dict with `response`, `model_used`, `retrieval_chunks`, `processing_time_ms`.

If Groq raises `GroqUnavailableException`, return a friendly error message for now (full failover in Phase 38).

**Task 20.3 — Build the chat router**

In `backend/api/chat/router.py`, create `router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])`.

`POST /query` — async endpoint, accepts `QueryRequest`, calls `chat_service.handle_query(...)`, returns `QueryResponse`.

`GET /history/{workspace_id}` — returns `ChatHistoryResponse` with all messages for the workspace.

Register the router in `main.py`.

**Error Verification — Phase 20:**

Upload and ingest a PDF. Submit a query via Swagger that should be answerable from the document content. Confirm a non-empty response is returned. Confirm the `retrieval_chunks` count is correct. Check the `conversations` table in SQLite — both the user message and assistant response should be stored. Try a query about something not in the document and verify the model correctly states insufficient information.

**Phase 20 Checklist:**
- [x] Query returns a meaningful response grounded in document content
- [x] Query about absent topics returns "insufficient information" response
- [x] Both user and assistant messages are saved to conversations table
- [x] `retrieval_chunks` in response matches actual chunks retrieved
- [x] `processing_time_ms` is populated and reasonable (< 30,000ms)
- [x] Swagger `POST /api/v1/chat/query` works end-to-end

---

## Phase 21 — MVP Validation — Milestone M1

**Objective:** Validate the complete end-to-end RAG pipeline through systematic testing of all components, fix all identified issues, and confirm Milestone M1 (Working RAG MVP) is achieved before proceeding to the intelligence layer.

**Technical Context:**

Milestone M1 requires a fully functional upload → ingest → retrieve → answer workflow with zero unhandled errors. This phase is dedicated entirely to testing, debugging, and hardening the existing code. No new features are added — only fixes and validations.

Perform the following tests systematically, documenting any failures and fixing them before checking off items.

**Micro-Tasks:**

**Task 21.1 — Full pipeline smoke test**

Create a new workspace, upload a multi-page PDF (minimum 10 pages), poll the status endpoint until `"completed"`, verify chunk count in SQLite, run a query about the document content, verify the response contains accurate information from the document. Repeat with a DOCX file.

**Task 21.2 — Edge case tests**

(a) Upload a PDF with only images (no selectable text) — confirm `extraction_success=False` and status becomes `"failed"`. (b) Upload a file larger than 50MB — confirm 400 error before any ingestion. (c) Upload the same file to the same workspace twice — confirm two separate document records with separate chunk sets. (d) Query an empty workspace — confirm graceful "no documents" response. (e) Delete a workspace with documents — confirm all chunks, FAISS index, and BM25 index (even if empty) are cleaned up.

**Task 21.3 — Concurrency test**

Start two simultaneous document uploads to the same workspace. Confirm both complete successfully without database corruption. Verify the total chunk count in the workspace equals the sum of chunks from both documents.

**Task 21.4 — Error recovery test**

Start the server with an invalid Groq API key. Upload and ingest a document. Submit a query — confirm a user-friendly error message rather than a 500 error. Re-add the valid key, restart, and confirm queries work again.

**Task 21.5 — Data isolation test**

Create two workspaces, upload different documents to each, and query each workspace. Confirm that workspace A's query never returns content from workspace B's documents.

**Error Verification — Phase 21:**

After completing all five task groups above with zero unhandled exceptions, verify the Swagger UI shows all endpoints, the SQLite database has no orphaned rows, and all FAISS indexes have the correct number of vectors.

**Phase 21 Checklist — Milestone M1:**
- [x] Full PDF pipeline: upload → ingest → query works end-to-end
- [x] Full DOCX pipeline: upload → ingest → query works end-to-end
- [x] Image-only PDF gracefully fails ingestion with `"failed"` status
- [x] Oversized file upload returns 400 before ingestion
- [x] Two documents in one workspace both indexed and searchable
- [x] Empty workspace query returns graceful no-document response
- [x] Workspace deletion cleans up all files and database rows
- [x] Two simultaneous uploads complete without database corruption
- [x] Invalid Groq key returns user-friendly error, not 500
- [x] Workspace isolation prevents cross-workspace retrieval
- [x] No unhandled exceptions in any test scenario

---

## Phase 22 — BM25 Indexing

**Objective:** Build the BM25 indexer service that creates and maintains keyword-based retrieval indexes over workspace document chunks.

**Technical Context:**

BM25 (Best Match 25) is a lexical retrieval algorithm that scores documents based on term frequency and inverse document frequency. It excels at exact keyword matching, acronyms, technical terms, and domain-specific phrases that semantic search might miss. For example, if a user searches for "FAISS" and the document contains "FAISS" but the embedding model has poor representation for this acronym, FAISS semantic search might miss it. BM25 will find it reliably.

The `rank_bm25` library provides a `BM25Okapi` class. It requires the corpus to be tokenized: each document (chunk) is represented as a list of lowercase word tokens. Tokenization is simple — lowercase the text and split on whitespace after removing punctuation. Do not use NLTK stop-word removal for this; it removes terms that might be important in technical documents.

The BM25 index is workspace-scoped. When any new document is ingested into a workspace, the entire BM25 index for that workspace must be rebuilt — BM25Okapi does not support incremental updates. Build by fetching all chunks for the workspace from SQLite, tokenizing them, and creating a new `BM25Okapi` instance.

**Files to Create:**

- `backend/services/document/bm25_indexer.py`

**Micro-Tasks:**

**Task 22.1 — Build BM25Indexer**

In `bm25_indexer.py`, define class `BM25Indexer`. Initialize `self.chunk_repo = ChunkRepository()`.

Define `_tokenize(text: str) -> list[str]`. Lowercase the text. Use `re.sub(r'[^a-z0-9\s]', ' ', text)` to replace punctuation with spaces. Split on whitespace. Filter out empty strings. Return the token list.

Define `build_index(workspace_id: str) -> tuple[BM25Okapi, list[str]]`. Fetch all chunks for the workspace from `chunk_repo.get_chunks_by_workspace(workspace_id)`. Extract `chunk_text` and `chunk_id` in order. Tokenize each chunk text. If the corpus is empty, return `(None, [])`. Create `BM25Okapi(tokenized_corpus)`. Return the index and the parallel list of chunk IDs. The order of the chunk IDs list must exactly match the order of documents passed to BM25Okapi.

Define `search(bm25_index: BM25Okapi, chunk_ids: list[str], query: str, top_k: int = 50) -> list[tuple[str, float]]`. Tokenize the query. Call `bm25_index.get_scores(tokenized_query)` to get an array of scores. Use `numpy.argsort(-scores)[:top_k]` to get the top-K indices in descending order. Return list of `(chunk_ids[idx], score)` for each top index, filtering out scores of 0.0.

**Error Verification — Phase 22:**

Build a BM25 index for a workspace with ingested documents. Search for a specific term you know appears in the documents. Confirm the relevant chunks are returned. Search for a term that does not exist and confirm an empty list or zero-score results. Verify the index and chunk_ids list have the same length.

**Phase 22 Checklist:**
- [x] Tokenization correctly lowercases and removes punctuation
- [x] `build_index` returns `(None, [])` for empty workspace gracefully
- [x] `search` returns `(chunk_id, score)` pairs sorted by score descending
- [x] Zero-score results are filtered out
- [x] Chunk IDs list length equals corpus length passed to BM25Okapi

---

## Phase 23 — BM25 Storage

**Objective:** Build the BM25 repository that persists and loads workspace BM25 indexes to/from disk, and integrate BM25 index building into the ingestion pipeline.

**Technical Context:**

BM25Okapi objects are not directly serializable to JSON because they contain numpy arrays and custom Python objects. Use Python's `pickle` module to serialize and deserialize them. Store as `storage/bm25/{workspace_id}.pkl`. Alongside it, store the chunk IDs list as `storage/bm25/{workspace_id}_ids.json` (JSON-serializable list of strings).

BM25 index building is triggered at the end of the ingestion pipeline, after all chunks are stored and embeddings are indexed in FAISS. It must rebuild the entire index because BM25Okapi has no add-document API.

Keep BM25 indexes in memory in a dict cache, same pattern as FAISS. The cache is invalidated when a new document is ingested (forcing a rebuild from SQLite).

**Files to Create:**

- `backend/repositories/bm25/bm25_repository.py`

**Files to Modify:**

- `backend/services/document/ingestion_service.py` — add BM25 index building step

**Micro-Tasks:**

**Task 23.1 — Build BM25Repository**

In `bm25_repository.py`, define class `BM25Repository`. Initialize `self._cache: dict = {}`, `self.bm25_path = settings.BM25_PATH`, `self.indexer = BM25Indexer()`.

Define `_get_index_path(workspace_id)` and `_get_ids_path(workspace_id)` as path helpers.

Define `rebuild_index(workspace_id: str) -> None`. Call `bm25_indexer.build_index(workspace_id)` to get `(bm25_obj, chunk_ids)`. If `bm25_obj` is None, clear the cache entry and delete any existing files. Otherwise, pickle-dump the BM25 object to the index path. JSON-dump the chunk IDs to the IDs path. Update the in-memory cache with `{"index": bm25_obj, "ids": chunk_ids}`.

Define `get_index(workspace_id: str) -> tuple[BM25Okapi | None, list[str]]`. Check cache first. If not cached, check if the pickle file exists — load both files. If not on disk, call `rebuild_index` and load from cache. Return `(bm25_obj, chunk_ids)`.

Define `search(workspace_id: str, query: str, top_k: int = 50) -> list[tuple[str, float]]`. Get the index. If None, return empty list. Call `bm25_indexer.search(bm25_obj, chunk_ids, query, top_k)`.

Define `delete_workspace_index(workspace_id: str) -> None`. Remove cache entry. Delete both files if they exist.

**Task 23.2 — Add BM25 rebuild to ingestion**

In `ingestion_service.py`, add `self.bm25_repo = BM25Repository()` to `__init__`. After the FAISS indexing step (before setting status to `"completed"`), call `self.bm25_repo.rebuild_index(workspace_id)`. Log the completion of BM25 indexing.

**Error Verification — Phase 23:**

Upload a document. After ingestion completes, confirm `storage/bm25/{workspace_id}.pkl` and `{workspace_id}_ids.json` exist. Load the BM25 index via `BM25Repository().get_index(workspace_id)` and search for a known term. Delete the pickle file and call `get_index` again — it should rebuild automatically from SQLite.

**Phase 23 Checklist:**
- [x] BM25 pickle file created at `storage/bm25/{workspace_id}.pkl`
- [x] Chunk IDs JSON file created at `storage/bm25/{workspace_id}_ids.json`
- [x] `rebuild_index` is called at the end of every successful ingestion
- [x] `get_index` rebuilds from SQLite if pickle file is missing
- [x] `delete_workspace_index` removes both files and clears cache
- [x] `search` returns valid results after rebuild

---

## Phase 24 — Hybrid Retrieval

**Objective:** Build the hybrid retriever that executes FAISS semantic search and BM25 lexical search simultaneously and prepares both result sets for fusion.

**Technical Context:**

Hybrid retrieval runs both searches and collects their raw results before any merging or ranking. The two searches are independent — run them sequentially (no async parallelism needed for a prototype). The FAISS search returns cosine similarity scores; the BM25 search returns BM25 scores in a different scale. Do not attempt to normalize or compare these scores directly — the RRF engine in Phase 25 uses only the ranking positions, not the raw scores.

The hybrid retriever's output is a tuple of two ranked lists: `(faiss_results, bm25_results)`, each being a `list[tuple[str, float]]` where the string is a chunk ID. Passing the raw lists to RRF as separate inputs is the correct design.

**Files to Create:**

- `backend/services/retrieval/hybrid_retriever.py`

**Micro-Tasks:**

**Task 24.1 — Build HybridRetriever**

In `hybrid_retriever.py`, define class `HybridRetriever`. Initialize `self.vector_repo = VectorRepository()`, `self.bm25_repo = BM25Repository()`.

Define `retrieve(workspace_id: str, query: str, faiss_top_k: int = 50, bm25_top_k: int = 50) -> tuple[list[tuple[str,float]], list[tuple[str,float]]]`.

Step 1: FAISS search — call `vector_repo.search_similar(workspace_id, query, faiss_top_k)`. If the workspace has no vectors, return `([], [])` immediately.

Step 2: BM25 search — call `bm25_repo.search(workspace_id, query, bm25_top_k)`.

Return the tuple `(faiss_results, bm25_results)`. Each is a list of `(chunk_id, score)` sorted by its own score metric.

**Error Verification — Phase 24:**

Run `HybridRetriever().retrieve(workspace_id, "test query")`. Confirm you get two separate result lists. Verify that the FAISS list and BM25 list may contain different chunk IDs (they often will for technical queries). Verify that each list is independently sorted by its own score metric.

**Phase 24 Checklist:**
- [x] Both FAISS and BM25 searches execute successfully
- [x] Returns a tuple of two independent lists
- [x] Each list is sorted by its own score metric
- [x] Empty workspace returns `([], [])` without errors
- [x] BM25 and FAISS results are independent (may differ for technical queries)

---

## Phase 25 — RRF Engine

**Objective:** Implement Reciprocal Rank Fusion to merge FAISS and BM25 result lists into a single unified ranking that combines the strengths of both retrieval methods.

**Technical Context:**

Reciprocal Rank Fusion merges multiple ranked lists by assigning each item a fused score equal to the sum of `1 / (rank_position + RRF_CONSTANT)` across all lists. The constant 60 is empirically proven to work well — it reduces the influence of top-ranked items slightly to prevent any single retrieval method from dominating the fusion. Items that appear in both lists get contributions from both, naturally boosting consensus results.

The key insight is that RRF works on rank positions, not raw scores. A chunk ranked 1st by FAISS and 10th by BM25 gets a higher RRF score than one ranked 5th by FAISS and 30th by BM25. You never need to normalize FAISS cosine scores against BM25 BM25 scores — just their positions matter.

Items that appear in only one list still get their RRF contribution from that one list. Items in both lists get contributions from both and naturally rank higher.

**Files to Create:**

- `backend/services/retrieval/rrf_engine.py`

**Micro-Tasks:**

**Task 25.1 — Build RRFEngine**

In `rrf_engine.py`, define class `RRFEngine`. Initialize `self.rrf_constant = settings.RRF_CONSTANT` (default 60).

Define `fuse(ranked_lists: list[list[tuple[str, float]]], top_n: int = 20) -> list[tuple[str, float]]`. `ranked_lists` is a variable-length list of ranked results (supporting future extension beyond just two lists).

Algorithm: create a `defaultdict(float)` called `rrf_scores`. For each list in `ranked_lists`, enumerate its items. For item at index `i` (0-based), add `1.0 / (i + 1 + self.rrf_constant)` to `rrf_scores[chunk_id]`. After processing all lists, sort the dict by value descending. Return the top `top_n` items as `list[(chunk_id, rrf_score)]`.

**Error Verification — Phase 25:**

Create two ranked lists with some overlapping chunk IDs and some unique ones. Call `RRFEngine().fuse([list1, list2], top_n=10)`. Verify that items appearing in both lists rank higher than items in only one list. Verify the output is sorted by RRF score descending. Verify the output length is at most `top_n`.

**Phase 25 Checklist:**
- [x] Items in both lists rank higher than items in one list only
- [x] Output is sorted by RRF score descending
- [x] Output length is at most `top_n`
- [x] Works correctly when one of the input lists is empty
- [x] Works with the specific constant of 60

---

## Phase 26 — Cross-Encoder Reranking Service

**Objective:** Integrate the `cross-encoder/ms-marco-MiniLM-L-6-v2` model to rerank the top-20 RRF candidates using deep query-document relevance scoring, improving retrieval precision.

**Technical Context:**

Cross-encoders are fundamentally different from bi-encoders (Sentence Transformers). Bi-encoders encode query and document separately into embeddings, then compare them with cosine similarity. Cross-encoders take the `(query, document)` pair as a joint input and output a single relevance score. This is computationally more expensive but significantly more accurate because the model sees the relationship between query and document jointly, not independently.

Because cross-encoders are slow, run them only on the top-20 RRF candidates, not all 50+50=100 raw results. The cross-encoder model `ms-marco-MiniLM-L-6-v2` from Sentence Transformers is fast enough for 20 candidates without perceptible latency.

Use `CrossEncoder` from `sentence_transformers`. Scores are raw logits and can be negative or positive (not bounded). Higher is better. Filter out pairs with score below `settings.CROSS_ENCODER_MIN_SCORE` (0.60 from config). Return the top 5 that pass the threshold.

The cross-encoder is loaded once as a singleton, same as the embedding model.

**Files to Create:**

- `backend/providers/embeddings/cross_encoder_provider.py`
- `backend/services/retrieval/cross_encoder_service.py`

**Micro-Tasks:**

**Task 26.1 — Build CrossEncoderProvider**

In `cross_encoder_provider.py`, define class `CrossEncoderProvider`. In `__init__`, load `CrossEncoder(settings.CROSS_ENCODER_MODEL)` and store as `self.model`. Use `get_cross_encoder_provider()` singleton pattern identical to `get_embedding_provider()`. Add preloading to the lifespan startup.

Define `predict(query: str, texts: list[str]) -> list[float]`. Create pairs as `[[query, text] for text in texts]`. Call `self.model.predict(pairs)`. Return a list of float scores, one per text.

**Task 26.2 — Build CrossEncoderService**

In `cross_encoder_service.py`, define class `CrossEncoderService`. Initialize `self.provider = get_cross_encoder_provider()`, `self.chunk_repo = ChunkRepository()`, `self.doc_repo = DocumentRepository()`.

Define `rerank(query: str, candidates: list[tuple[str, float]], top_n: int = 5) -> list[RetrievedChunk]`. `candidates` is a list of `(chunk_id, rrf_score)` from the RRF engine.

Step 1: Fetch chunk texts for all candidate IDs from `chunk_repo.get_chunks_by_ids([c[0] for c in candidates])`. Build a dict `chunk_id → chunk_dict`.

Step 2: Get cross-encoder scores. Call `provider.predict(query, [chunk_dict["chunk_text"] for chunk_id, _ in candidates])`. Get a list of float scores.

Step 3: Zip chunk IDs with cross-encoder scores. Filter out pairs where score < `settings.CROSS_ENCODER_MIN_SCORE`. Sort the remaining by cross-encoder score descending. Take top `top_n`.

Step 4: For each selected chunk, fetch the document record for `file_name`. Construct and return `list[RetrievedChunk]` sorted by cross-encoder score.

**Error Verification — Phase 26:**

Feed the cross-encoder service with a realistic query and 20 candidate chunks from a real ingested document. Verify that returned chunks are fewer than or equal to 5. Verify they are sorted by cross-encoder score. Verify that highly relevant chunks score above 0.60 and irrelevant ones are filtered out.

**Phase 26 Checklist:**
- [x] Cross-encoder model loads once at startup via lifespan
- [x] Chunks below `CROSS_ENCODER_MIN_SCORE` are filtered
- [x] Returns at most `top_n` reranked chunks
- [x] Results are sorted by cross-encoder score descending
- [x] Empty candidates list returns empty list without errors
- [x] `RetrievedChunk` objects are correctly populated

---

## Phase 27 — Context Compression

**Objective:** Build the context compressor that removes near-duplicate chunks from the cross-encoder output and ensures the final context passed to the LLM is concise and non-redundant.

**Technical Context:**

Near-duplicate chunks occur when the same paragraph appears in multiple chunks due to overlap, or when two chunks from the same document section are nearly identical. Sending duplicates wastes tokens and confuses the LLM by making it weight the same information twice.

Near-duplicate detection uses sequence similarity rather than exact string matching. Use `difflib.SequenceMatcher` to compute the similarity ratio between pairs of chunk texts. If two chunks have a ratio above `settings.NEAR_DUPLICATE_THRESHOLD` (0.90), keep only the one with the higher cross-encoder score (which should already be first since the input is sorted by score).

After deduplication, ensure the final context has between 3 and 5 chunks. If fewer than 3 chunks remain after deduplication and score filtering, the retrieval confidence engine (Phase 28) will flag this as `LOW` confidence.

**Files to Create:**

- `backend/services/retrieval/context_compressor.py`

**Micro-Tasks:**

**Task 27.1 — Build ContextCompressor**

In `context_compressor.py`, define class `ContextCompressor`. Initialize `self.similarity_threshold = 0.90`, `self.max_chunks = settings.CONTEXT_MAX_CHUNKS` (5), `self.min_chunks = 3`.

Define `compress(chunks: list[RetrievedChunk]) -> list[RetrievedChunk]`.

Step 1: Deduplicate. Initialize `keep = []`. For each chunk, compare its text against all already-kept chunks using `difflib.SequenceMatcher(None, chunk.chunk_text, kept_chunk.chunk_text).ratio()`. If the ratio exceeds `similarity_threshold` against any kept chunk, skip this chunk. Otherwise, add it to `keep`.

Step 2: Truncate to max_chunks. Return `keep[:self.max_chunks]`.

Step 3: If the resulting list has fewer than `min_chunks`, still return what's available (the confidence engine will handle the warning).

Define `get_final_chunk_count(chunks: list[RetrievedChunk]) -> int`. Returns `len(chunks)`.

**Error Verification — Phase 27:**

Create a list of 5 chunks where two are nearly identical (>90% similarity). Call `compress()` and verify the duplicate is removed. Verify that non-duplicate chunks are all kept. Verify that output length never exceeds `max_chunks`.

**Phase 27 Checklist:**
- [x] Near-duplicate chunks (>90% similarity) are removed
- [x] The higher-scored chunk is kept when duplicates exist (input is pre-sorted)
- [x] Output length never exceeds `CONTEXT_MAX_CHUNKS`
- [x] Works correctly with input of fewer than 3 chunks
- [x] `SequenceMatcher` comparison is applied pairwise (not just sequential pairs)

---

## Phase 28 — Retrieval Confidence Engine

**Objective:** Build the confidence engine that evaluates whether the retrieved context is sufficient to answer a query, preventing hallucinated responses when evidence is weak.

**Technical Context:**

The confidence threshold defined in the spec is: `cross_encoder_score >= 0.60 AND at least 2 relevant chunks`. If these conditions are not met, the response should be "I could not find sufficient information in uploaded documents" rather than a hallucinated answer. This is the single most important anti-hallucination mechanism in the system.

The confidence engine also provides the chat service with a `confidence_level` field (`"HIGH"`, `"MEDIUM"`, `"LOW"`) that changes prompt behavior. HIGH confidence (3-5 chunks above threshold) triggers a detailed response. MEDIUM (1-2 chunks) triggers a cautious response noting limited evidence. LOW (0 chunks) triggers the fallback response without calling the LLM at all.

**Files to Create:**

- `backend/services/retrieval/confidence_engine.py`

**Micro-Tasks:**

**Task 28.1 — Build ConfidenceEngine**

In `confidence_engine.py`, define `ConfidenceLevel` as a string enum or constants: `"HIGH"`, `"MEDIUM"`, `"LOW"`. Define dataclass `ConfidenceResult` with `level: str`, `sufficient: bool`, `chunk_count: int`, `message: str`.

Define class `ConfidenceEngine`. Initialize `self.min_score = settings.CROSS_ENCODER_MIN_SCORE` (0.60), `self.min_chunks_for_high = 3`.

Define `evaluate(chunks: list[RetrievedChunk]) -> ConfidenceResult`.

Count chunks that pass the score threshold: `passing = [c for c in chunks if c.score >= self.min_score]`. (Note: after cross-encoder reranking, all chunks should already pass since cross_encoder_service filters below threshold. This provides a double-check.)

If `len(passing) == 0`: return `ConfidenceResult(level="LOW", sufficient=False, chunk_count=0, message="I could not find sufficient information in the uploaded documents to answer this question.")`.

If `len(passing) < 2`: return `ConfidenceResult(level="MEDIUM", sufficient=True, chunk_count=len(passing), message="Limited relevant information found. Answer may be incomplete.")`.

If `len(passing) >= 2`: return `ConfidenceResult(level="HIGH", sufficient=True, chunk_count=len(passing), message="")`.

**Error Verification — Phase 28:**

Test with 0 chunks — confirm `LOW, sufficient=False`. Test with 1 chunk at score 0.7 — confirm `MEDIUM, sufficient=True`. Test with 3 chunks at scores 0.7, 0.75, 0.8 — confirm `HIGH, sufficient=True`.

**Phase 28 Checklist:**
- [x] 0 passing chunks returns `LOW` confidence with `sufficient=False`
- [x] 1 passing chunk returns `MEDIUM` confidence with `sufficient=True`
- [x] 2+ passing chunks returns `HIGH` confidence with `sufficient=True`
- [x] `LOW` confidence message matches the specified fallback text exactly
- [x] `ConfidenceResult.chunk_count` reflects passing chunks count

---

## Phase 29 — Source Attribution

**Objective:** Build the source attributor that tracks which source documents contributed to the context, enabling the response to cite specific documents and enabling the API to return retrieval metadata.

**Technical Context:**

Source attribution answers the question: "which documents were used to generate this answer?" It aggregates the unique source documents from the retrieved chunks and formats them for display. This information is included in the API response and can be shown to users as citations.

Source attribution is a lightweight aggregation step — it does not change the chunks or their content. It reads `source_file` and `document_id` from the `RetrievedChunk` objects and produces a deduplicated list of source documents.

**Files to Create:**

- `backend/services/retrieval/source_attributor.py`

**Micro-Tasks:**

**Task 29.1 — Build SourceAttributor**

In `source_attributor.py`, define dataclass `SourceDocument` with `document_id: str`, `file_name: str`, `chunk_count: int` (how many chunks from this document contributed).

Define class `SourceAttributor`. Define `extract_sources(chunks: list[RetrievedChunk]) -> list[SourceDocument]`. Group chunks by `document_id`. For each unique document, count contributing chunks. Return a list of `SourceDocument` sorted by `chunk_count` descending (most-referenced document first).

Define `format_sources_text(sources: list[SourceDocument]) -> str`. Returns a formatted string like `"Sources: [1] filename1.pdf (3 chunks), [2] filename2.docx (1 chunk)"`. Used for including source info at the end of LLM responses.

**Phase 29 Checklist:**
- [x] Chunks from the same document are grouped correctly
- [x] `chunk_count` reflects actual contributing chunks per document
- [x] Sources are sorted by `chunk_count` descending
- [x] `format_sources_text` produces a readable citation string

---

## Phase 30 — Markdown Response Engine and Full Retrieval Pipeline Integration

**Objective:** Build the response formatter that validates and standardizes LLM Markdown output, then wire the complete retrieval pipeline (Hybrid → RRF → CrossEncoder → Compress → Confidence → Prompt → LLM) into the chat service, replacing the Phase 20 FAISS-only MVP.

**Technical Context:**

The `ResponseFormatter` validates that the LLM output is valid Markdown. It also appends source citations from the `SourceAttributor` to the end of the response, ensuring users always see where the answer came from.

More importantly, this phase completes the full pipeline by updating the `ChatService` to use all intelligence components together. The pipeline becomes: `HybridRetriever` → `RRFEngine` → `CrossEncoderService` → `ContextCompressor` → `ConfidenceEngine` → (if sufficient) `PromptBuilder` + `GroqProvider` → `ResponseFormatter`.

**Files to Create:**

- `backend/services/llm/response_formatter.py`

**Files to Modify:**

- `backend/services/llm/chat_service.py` — replace FAISS-only pipeline with full pipeline

**Micro-Tasks:**

**Task 30.1 — Build ResponseFormatter**

In `response_formatter.py`, define class `ResponseFormatter`.

Define `validate_and_clean(text: str) -> str`. Strip leading/trailing whitespace. Ensure the response is non-empty. If the response is empty, return a fallback string. Fix common Markdown formatting issues: ensure code blocks are closed (equal number of triple backticks), ensure no raw HTML tags (strip `<br>` etc.).

Define `append_sources(response_text: str, sources: list[SourceDocument]) -> str`. If sources is non-empty, append `"\n\n---\n\n" + source_attributor.format_sources_text(sources)` to the response.

**Task 30.2 — Update ChatService to use the full pipeline**

In `chat_service.py`, replace the `FAISSRetriever` with `HybridRetriever`. Add all components: `RRFEngine`, `CrossEncoderService`, `ContextCompressor`, `ConfidenceEngine`, `SourceAttributor`, `ResponseFormatter`.

Update `handle_query` to execute the full pipeline in sequence: (1) hybrid retrieve → (2) RRF fuse → (3) fetch chunk details for RRF top-20 → (4) cross-encoder rerank → (5) compress → (6) evaluate confidence → (7) if LOW confidence, return the fallback message immediately without calling LLM → (8) build prompt with compressed chunks → (9) generate via Groq → (10) format response → (11) append sources → (12) save to conversation → (13) return.

For step 3, after RRF returns `(chunk_id, rrf_score)` pairs, you need the chunk texts to pass to the cross-encoder. Fetch them from `ChunkRepository.get_chunks_by_ids`. Convert to a temporary `RetrievedChunk` list using the RRF score as the `score` field — the cross-encoder will overwrite these scores.

**Error Verification — Phase 30:**

Run the full pipeline on a real document query. Verify all pipeline stages execute (add timing logs for each stage). Verify the response includes source citations at the bottom. Verify that a query about a completely unrelated topic returns the LOW-confidence fallback message. Check that `processing_time_ms` in the API response is reasonable (typically 2,000–15,000ms for the full pipeline).

**Phase 30 Checklist — Milestone M2:**
- [x] Full pipeline: Hybrid → RRF → CrossEncoder → Compress → Confidence → LLM
- [x] LOW confidence returns fallback message without calling LLM
- [x] HIGH confidence returns cited, source-attributed Markdown response
- [x] Source citations appear at the end of responses
- [x] `retrieval_chunks` in API response matches final chunk count (3-5)
- [x] `processing_time_ms` is logged for the full pipeline
- [x] `ResponseFormatter` produces valid Markdown
- [x] Entire pipeline executes without unhandled exceptions

---

## Phase 31 — Conversation Storage Wiring

**Objective:** Ensure conversation history is saved correctly to SQLite after every query, with proper role tagging, model attribution, and retrieval metadata recorded for each exchange.

**Technical Context:**

This phase consolidates the conversation saving logic that was partially added in Phase 20. Each query-response pair generates two rows in the `conversations` table: one with `role="user"` and one with `role="assistant"`. The assistant message also records `model_used` and `retrieval_chunks`. Ordering is by `created_at` timestamp.

Verify that conversations are workspace-isolated — a query to workspace A must not appear in workspace B's history. Verify that the history endpoint returns messages in chronological order (oldest first), which requires reversing the `DESC` query from the repository.

**Files to Modify:**

- `backend/services/llm/chat_service.py` — ensure both user and assistant messages are saved with correct metadata
- `backend/repositories/sqlite/conversation_repository.py` — verify `get_recent_messages` returns chronological order

**Micro-Tasks:**

**Task 31.1 — Verify and fix conversation saving**

In `handle_query`, confirm two `conversation_repo.save_message()` calls are made for every successful query: first the user message (`role="user"`, `model_used=None`, `retrieval_chunks=0`), then the assistant message (`role="assistant"`, `model_used=model_name`, `retrieval_chunks=final_chunk_count`). Both must use the same `workspace_id` but different `message_id` UUIDs.

**Task 31.2 — Verify history ordering**

In `conversation_repository.py`, confirm `get_recent_messages` queries with `ORDER BY created_at DESC LIMIT ?` but then reverses the Python list before returning, so the oldest of the last 5 messages is first. This "last 5 messages in chronological order" is the correct behavior for prompt context.

**Phase 31 Checklist:**
- [x] User message saved before assistant message for each query
- [x] Assistant message includes `model_used` and `retrieval_chunks`
- [x] `GET /api/v1/chat/history/{workspace_id}` returns all messages in chronological order
- [x] Workspace isolation verified: workspace A history has no workspace B messages

---

## Phase 32 — Recent Context Window

**Objective:** Build the context window manager that retrieves the last N conversation messages for a workspace and formats them as an LLM-readable conversation history.

**Technical Context:**

The last 5 messages (configurable via `RECENT_CHAT_WINDOW`) provide the LLM with short-term context about the ongoing conversation. This enables follow-up questions ("what about the second point you mentioned?") to be understood correctly.

The context window is formatted as an alternating `User: ... | Assistant: ...` exchange history and inserted into the prompt between system instructions and retrieved evidence. It tells the model what was already discussed so it doesn't repeat itself or misunderstand references to earlier turns.

**Files to Create:**

- `backend/services/memory/context_window.py`

**Micro-Tasks:**

**Task 32.1 — Build ContextWindow**

In `context_window.py`, define class `ContextWindow`. Initialize `self.conversation_repo = ConversationRepository()`, `self.window_size = settings.RECENT_CHAT_WINDOW`.

Define `get_recent_context(workspace_id: str) -> list[dict]`. Call `conversation_repo.get_recent_messages(workspace_id, limit=self.window_size)`. Return the message list (already in chronological order from the repository).

Define `format_for_prompt(messages: list[dict]) -> str`. If empty, return `""`. Format as: for each message, `f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['message']}"`. Join with `"\n"`. Prefix with `"Recent Conversation:\n"`.

**Phase 32 Checklist:**
- [x] Returns at most `RECENT_CHAT_WINDOW` messages
- [x] Messages are in chronological order
- [x] `format_for_prompt` produces readable conversation history string
- [x] Empty conversation returns empty string without errors

---

## Phase 33 — Summary Generator

**Objective:** Build the summarization service that periodically compresses workspace conversation history into a concise summary, maintaining long-term context without unlimited token growth.

**Technical Context:**

Every 10 messages (configurable via `SUMMARY_UPDATE_INTERVAL`), the system summarizes all conversation history into a compressed form. This summary replaces the raw history as the long-term context signal. The summary is generated by calling the LLM with a compact prompt asking it to summarize the conversation. This uses a small number of tokens at write-time to save a larger number at read-time.

The trigger: after saving each assistant message, check if the total message count for the workspace is a multiple of `SUMMARY_UPDATE_INTERVAL`. If yes, trigger summarization. This check is cheap (integer modulo) and runs synchronously after every query.

**Files to Create:**

- `backend/services/memory/summarization_service.py`

**Micro-Tasks:**

**Task 33.1 — Build SummarizationService**

In `summarization_service.py`, define class `SummarizationService`. Initialize `self.conversation_repo = ConversationRepository()`, `self.groq_provider = GroqProvider()`, `self.interval = settings.SUMMARY_UPDATE_INTERVAL`.

Define `should_summarize(workspace_id: str) -> bool`. Get `message_count = conversation_repo.get_message_count(workspace_id)`. Return `message_count > 0 and message_count % self.interval == 0`.

Define `generate_summary(workspace_id: str) -> str | None`. Fetch all messages with `conversation_repo.get_all_messages(workspace_id)`. Build a compact conversation string. Call Groq with a system prompt: `"Summarize the following conversation concisely, preserving key topics, questions asked, and information provided."` Return the summary string or `None` if Groq fails.

**Phase 33 Checklist:**
- [x] `should_summarize` triggers at exactly every `SUMMARY_UPDATE_INTERVAL` messages
- [x] Summary is generated from the complete conversation history
- [x] Groq failure returns `None` without crashing
- [x] Summary is a non-empty, coherent condensation of the conversation

---

## Phase 34 — Workspace Summary Store

**Objective:** Build the workspace summary repository and integrate the summarization service into the chat flow so that summaries are automatically generated and persisted after every interval.

**Files to Create:**

- `backend/repositories/sqlite/workspace_summary_repository.py`

**Files to Modify:**

- `backend/services/llm/chat_service.py` — trigger summarization after each query

**Micro-Tasks:**

**Task 34.1 — Build WorkspaceSummaryRepository**

In `workspace_summary_repository.py`, define `WorkspaceSummaryRepository(BaseRepository)` with methods:
- `upsert_summary(workspace_id: str, summary_text: str) -> dict` — use `INSERT OR REPLACE INTO workspace_summaries (summary_id, workspace_id, summary_text, last_updated) VALUES (...)`. Generate a new UUID each time (the UNIQUE constraint on `workspace_id` handles deduplication).
- `get_summary(workspace_id: str) -> dict | None` — fetch the summary for a workspace.
- `delete_summary(workspace_id: str)` — for workspace cleanup.

**Task 34.2 — Wire summarization into ChatService**

In `chat_service.py`, add `self.summarization_service = SummarizationService()`, `self.summary_repo = WorkspaceSummaryRepository()`. After saving the assistant message, check `summarization_service.should_summarize(workspace_id)`. If True, call `summary = summarization_service.generate_summary(workspace_id)`, and if summary is not None, call `summary_repo.upsert_summary(workspace_id, summary)`. Log the summarization event.

**Phase 34 Checklist:**
- [x] Summary is generated after every `SUMMARY_UPDATE_INTERVAL` messages
- [x] `workspace_summaries` table is updated after each summarization
- [x] Only one summary row exists per workspace (UNIQUE constraint enforced)
- [x] Summarization failure is logged but does not affect query response

---

## Phase 35 — Context Builder

**Objective:** Build the context builder that assembles the complete LLM context package by merging retrieved chunks, recent conversation history, workspace summary, and workspace metadata into a unified structured input.

**Technical Context:**

The context builder is the component that gathers all contextual inputs from different sources and hands them to the prompt builder in a clean structure. It sits between the retrieval pipeline and the prompt builder. Its output is a `ContextPackage` dataclass containing everything the prompt builder needs.

By having this dedicated layer, the prompt builder remains a pure text formatter — it never queries databases or calls services. All data gathering is the context builder's responsibility.

**Files to Create:**

- `backend/models/context.py` — ContextPackage dataclass
- `backend/services/memory/context_builder.py`

**Micro-Tasks:**

**Task 35.1 — Define ContextPackage**

In `backend/models/context.py`, define `@dataclasses.dataclass ContextPackage` with: `query: str`, `workspace_id: str`, `workspace_name: str`, `retrieved_chunks: list[RetrievedChunk]`, `recent_messages: list[dict]`, `workspace_summary: str`, `confidence: ConfidenceResult`, `sources: list[SourceDocument]`, `mode: str`.

**Task 35.2 — Build ContextBuilder**

In `context_builder.py`, define class `ContextBuilder`. Initialize all sub-components: `HybridRetriever`, `RRFEngine`, `CrossEncoderService`, `ContextCompressor`, `ConfidenceEngine`, `SourceAttributor`, `ContextWindow`, `WorkspaceSummaryRepository`, `WorkspaceRepository`.

Define `async build(workspace_id: str, query: str, mode: str) -> ContextPackage`. Executes the complete retrieval pipeline (Phases 24-29) and memory pipeline (Phases 32-34 reading only) to assemble a `ContextPackage`. This consolidates what was previously scattered across `ChatService.handle_query`.

**Task 35.3 — Refactor ChatService to use ContextBuilder**

Move all retrieval and memory logic from `ChatService.handle_query` into `ContextBuilder.build`. The `ChatService` now calls `context_builder.build(...)` to get a `ContextPackage`, checks `context.confidence.sufficient`, builds the prompt, calls the LLM, formats the response, saves to history, and returns.

**Phase 35 Checklist:**
- [x] `ContextPackage` contains all required fields
- [x] `ContextBuilder.build` executes complete retrieval + memory pipeline
- [x] `ChatService` is simplified to: build context → generate → format → save
- [x] Workspace summary is included in context package when available
- [x] Recent messages are included in context package

---

## Phase 36 — Advanced Prompt Engineering

**Objective:** Upgrade the prompt builder to use the full `ContextPackage`, incorporating conversation history, workspace summary, mode-specific instructions, and adaptive formatting based on confidence level.

**Technical Context:**

The prompt structure after Phase 36 is the complete Retrieval-Grounded Prompt Engineering architecture described in the docs: System Instructions → Workspace Context (summary + recent history) → Retrieved Document Evidence → User Query → Response Rules.

Different modes adjust the response style: Simple mode uses a brief, direct response style. Medium mode uses standard response with headings and bullet points. Expert mode uses detailed analytical response with citations, technical depth, and structured sections.

Confidence level adjusts the response rules: HIGH confidence generates full answers. MEDIUM confidence generates answers with a caveat about limited evidence. LOW confidence never reaches the prompt builder (blocked by the chat service before this point).

**Files to Modify:**

- `backend/services/llm/prompt_builder.py` — full rewrite to accept `ContextPackage`

**Micro-Tasks:**

**Task 36.1 — Rewrite PromptBuilder for ContextPackage**

Rewrite `PromptBuilder` with a single public method `build_from_context(context: ContextPackage) -> tuple[str, str]` that replaces the MVP `build_prompt` method.

`build_system_prompt(mode: str) -> str` — now includes mode-specific instructions. For Expert mode, instruct the model to provide detailed technical analysis with section headers and citations. For Medium mode, instruct concise but complete responses with citations. For Simple mode, instruct brief, direct answers.

`format_workspace_context(summary: str, recent_messages: list[dict]) -> str` — combines the workspace summary and recent conversation. If summary exists, include it. Format recent messages as the conversation context window.

`format_retrieved_evidence(chunks: list[RetrievedChunk]) -> str` — same as Phase 18 but potentially adds confidence caveat for MEDIUM confidence.

`format_response_rules(mode: str, confidence_level: str) -> str` — adds instructions for response format, citation style, and confidence caveat if applicable.

**Phase 36 Checklist — Milestone M3:**
- [x] `build_from_context` uses all fields of `ContextPackage`
- [x] Workspace summary appears in prompt when available
- [x] Recent conversation history appears in prompt
- [x] Expert mode prompts produce more detailed responses than Simple mode
- [x] MEDIUM confidence includes caveat in response rules
- [x] Prompt never exceeds a reasonable token count (add a truncation safety check)

---

## Phase 37 — Qwen Local Model Integration

**Objective:** Integrate the `Qwen2.5-3B` local model as a secondary LLM provider accessible via Ollama's local HTTP API, which is simpler and more resource-efficient than loading the model via Hugging Face transformers.

**Technical Context:**

Use Ollama (`ollama.ai`) rather than `transformers` to run Qwen2.5:3b locally. Ollama exposes a local HTTP API at `http://localhost:11434/api/generate` that accepts a JSON payload with the model name and prompt. The user must have Ollama installed and have run `ollama pull qwen2.5:3b` before this feature works. The provider should detect if Ollama is not running and return a helpful error.

The prompt format for Qwen via Ollama is a single string that combines system and user prompts: `[INST] <<SYS>>{system_prompt}<</SYS>> {user_prompt} [/INST]`. Ollama streams responses by default — use `stream: False` in the request body to get a complete response at once, which simplifies the integration significantly.

**Files to Create:**

- `backend/providers/qwen/qwen_provider.py`

**Micro-Tasks:**

**Task 37.1 — Build QwenProvider**

In `qwen_provider.py`, define class `QwenProvider`. Initialize `self.base_url = "http://localhost:11434/api/generate"`, `self.model = settings.LOCAL_MODEL_NAME`.

Define `generate(system_prompt: str, user_prompt: str) -> str`. Format the combined prompt string. Build the request payload: `{"model": self.model, "prompt": combined_prompt, "stream": False, "options": {"temperature": 0.1, "num_predict": 1000}}`. Use `requests.post(self.base_url, json=payload, timeout=120)`. Parse `response.json()["response"]`. Wrap in try-except — catch `requests.exceptions.ConnectionError` and raise `QwenUnavailableException("Ollama not running or not accessible")`. Catch all other exceptions and raise `QwenUnavailableException(str(e))`.

Define `is_available() -> bool`. Send a small test request. Return `True` if successful, `False` on any error.

**Phase 37 Checklist:**
- [x] `QwenProvider.generate` sends request to Ollama API
- [x] Ollama not running raises `QwenUnavailableException`, not unhandled error
- [x] `is_available()` returns correct boolean based on Ollama status
- [x] Response is correctly extracted from `response.json()["response"]`
- [x] Timeout is set (120 seconds) to handle slow local inference

---

## Phase 38 — Failover Manager

**Objective:** Build the LLM failover manager that automatically routes generation requests to Groq, and falls back to Qwen if Groq is unavailable, ensuring uninterrupted service.

**Technical Context:**

The failover manager is the single point of contact for all LLM generation requests. The chat service calls the failover manager instead of calling Groq or Qwen directly. The manager tries Groq first for medium and expert modes. If Groq raises `GroqUnavailableException`, it retries with Qwen and logs the fallback event. For Simple mode, it goes directly to Qwen.

The failover logic does not retry Groq multiple times — one attempt per request. Retrying would increase latency unacceptably. The `model_used` field in the response tells the client which model was actually used.

**Files to Create:**

- `backend/services/llm/failover_manager.py`

**Files to Modify:**

- `backend/services/llm/chat_service.py` — use `FailoverManager` instead of `GroqProvider` directly

**Micro-Tasks:**

**Task 38.1 — Build FailoverManager**

In `failover_manager.py`, define class `FailoverManager`. Initialize `self.groq = GroqProvider()`, `self.qwen = QwenProvider()`.

Define `generate(system_prompt: str, user_prompt: str, mode: str) -> tuple[str, str]`. Returns `(response_text, model_used_name)`.

If mode is `"simple"`: try Qwen, fall back to Groq if Qwen unavailable.

If mode is `"medium"` or `"expert"`: try Groq first. If `GroqUnavailableException` is raised, log the event with warning level, try Qwen. If Qwen also raises `QwenUnavailableException`, return `("Both AI models are currently unavailable. Please try again later.", "none")`.

Return `(response_text, model_name_used)`.

**Phase 38 Checklist:**
- [x] `"simple"` mode always attempts Qwen first
- [x] `"medium"` and `"expert"` modes attempt Groq first
- [x] Groq failure triggers automatic Qwen fallback
- [x] Both models unavailable returns a user-friendly message, not a crash
- [x] `model_used` in the response correctly identifies which model was invoked
- [x] Fallback events are logged at WARNING level

---

## Phase 39 — Retrieval Failover

**Objective:** Add graceful degradation logic to the retrieval pipeline so that if Cross-Encoder reranking fails, the system falls back to RRF results; if BM25 fails, the system uses FAISS only; if FAISS fails, the pipeline reports LOW confidence gracefully.

**Technical Context:**

The retrieval pipeline has three optional enhancement layers: BM25, RRF, and Cross-Encoder. Each can fail independently. Graceful degradation means: if any optional layer fails, the system continues with the best available results rather than raising an unhandled exception. The confidence engine then assesses what remains.

Each degradation scenario should be logged as a WARNING, not silently swallowed. Developers need to know the system is operating in a degraded mode.

**Files to Modify:**

- `backend/services/memory/context_builder.py` — wrap each retrieval stage in try-except with fallback

**Micro-Tasks:**

**Task 39.1 — Wrap retrieval stages with fallback logic**

In `ContextBuilder.build`, wrap each retrieval stage:

BM25 stage: if `bm25_repo.search(...)` raises any exception, log `WARNING: BM25 search failed, using FAISS-only`, set `bm25_results = []`. RRF still runs with one input list.

CrossEncoder stage: if `cross_encoder_service.rerank(...)` raises any exception, log `WARNING: Cross-encoder reranking failed, using RRF results`, convert the top-5 RRF results directly to `RetrievedChunk` objects using the chunk data fetched for cross-encoder input.

FAISS stage: if `vector_repo.search_similar(...)` raises any exception, log `ERROR: FAISS search failed`, set `faiss_results = []`. The confidence engine will evaluate `LOW` confidence from this point.

**Phase 39 Checklist:**
- [x] BM25 failure falls back to FAISS-only without exception propagation
- [x] Cross-encoder failure falls back to RRF top-N results
- [x] FAISS failure sets `faiss_results = []` and confidence evaluates to `LOW`
- [x] Every fallback event is logged at WARNING or ERROR level
- [x] Confidence engine correctly handles degraded results

---

## Phase 40 — Exception Framework

**Objective:** Build centralized custom exception classes and FastAPI exception handlers that convert all domain exceptions into consistent, user-friendly HTTP responses with proper status codes.

**Technical Context:**

Every exception in this system should be a custom exception with a clear name and message. Catching `Exception` broadly and returning HTTP 500 is unacceptable — it leaks implementation details and provides no actionable information to clients. The exception framework defines the full hierarchy and registers handlers with FastAPI.

Define exception classes in a hierarchy: `AppException` (base) → domain-specific exceptions. Each exception has an HTTP status code attribute. FastAPI exception handlers catch these and return JSON error responses with `{"success": false, "error": "...", "detail": "..."}`.

**Files to Create:**

- `backend/core/exceptions/exceptions.py`
- `backend/core/exceptions/handlers.py`

**Files to Modify:**

- `backend/main.py` — register exception handlers
- All service files — replace generic `ValueError` raises with proper custom exceptions

**Micro-Tasks:**

**Task 40.1 — Define exception hierarchy**

In `exceptions.py`, define: `AppException(Exception)` with `status_code: int` and `detail: str`. Then subclass: `WorkspaceNotFoundException(AppException)` (404), `DocumentNotFoundException(AppException)` (404), `WorkspaceAlreadyExistsException(AppException)` (409), `InvalidFileTypeException(AppException)` (400), `FileTooLargeException(AppException)` (400), `IngestionFailedException(AppException)` (500), `RetrievalFailedException(AppException)` (500), `GroqUnavailableException(AppException)` (503), `QwenUnavailableException(AppException)` (503).

**Task 40.2 — Register exception handlers**

In `handlers.py`, define `register_exception_handlers(app: FastAPI)`. Register a handler for `AppException` that returns `JSONResponse(status_code=exc.status_code, content={"success": False, "error": type(exc).__name__, "detail": exc.detail})`. Register a handler for general `Exception` that logs the full traceback at ERROR level and returns HTTP 500 with a generic message.

In `main.py`, call `register_exception_handlers(app)`.

**Task 40.3 — Replace all generic exceptions in service files**

Go through every service file that currently raises `ValueError` or generic `Exception`. Replace them with the appropriate custom exception class from Phase 40.1. This includes: `WorkspaceService` raises `WorkspaceNotFoundException`, `WorkspaceAlreadyExistsException`; `UploadService` raises `InvalidFileTypeException`, `FileTooLargeException`, `WorkspaceNotFoundException`.

**Phase 40 Checklist:**
- [x] `AppException` is the base class for all custom exceptions
- [x] Each exception class has a correct HTTP status code
- [x] FastAPI exception handler returns consistent JSON structure
- [x] 404 exceptions return `{"success": false, "error": "WorkspaceNotFoundException", ...}`
- [x] Generic `Exception` handler logs full traceback before returning 500
- [x] All service files use custom exceptions, not generic `ValueError`
- [x] Swagger UI shows correct status codes for error responses

---

## Phase 41 — Structured Logging

**Objective:** Upgrade the logging system to produce structured, context-rich log entries for every significant operation, enabling efficient debugging and operational observability.

**Technical Context:**

Every significant operation must produce a log entry with context: which workspace, which document, which query, how long it took, what model was used, how many chunks were retrieved. Without this, debugging a failure at 2am means reading generic "something went wrong" messages.

Upgrade the logging format to include a `request_id` field (generated per request using a FastAPI middleware) that links all log entries for a single request. Use Python's logging `extra` parameter to attach contextual fields.

Define a `get_logger(__name__)` helper that all modules use. The logger configuration adds a formatter that includes the extra fields if present.

**Files to Modify:**

- `backend/core/logging/logger.py` — enhanced logging setup
- `backend/main.py` — add request ID middleware
- Key service files — add structured log entries at appropriate points

**Micro-Tasks:**

**Task 41.1 — Add request ID middleware**

In `main.py`, define a simple Starlette middleware that generates a `request_id = str(uuid.uuid4())[:8]` for each request and adds it to the request's state. Log `request_id` at the start of every API endpoint call.

**Task 41.2 — Add structured log entries to key services**

In `chat_service.py`, log at INFO level: query received (workspace_id, query_length), retrieval completed (chunk_count, duration_ms), LLM generation completed (model_used, response_length, duration_ms). In `ingestion_service.py`, log: ingestion started (document_id), extraction completed (page_count), chunking completed (chunk_count), embedding completed (duration_ms), BM25 indexed. In `context_builder.py`, log retrieval stage durations.

**Phase 41 Checklist:**
- [x] Every API request has a unique `request_id` in logs
- [x] Ingestion pipeline logs each stage with duration
- [x] Query pipeline logs retrieval count and LLM duration
- [x] Fallback events are logged at WARNING level
- [x] Errors include full traceback in log file

---

## Phase 42 — Health Monitoring

**Objective:** Build system and model health check endpoints that expose the status of all critical subsystems (database, FAISS, embedding model, Groq, Qwen) for operational visibility.

**Files to Create:**

- `backend/services/system/health_service.py`
- `backend/api/system/router.py`
- `backend/schemas/system_schemas.py`

**Files to Modify:**

- `backend/main.py` — include system router

**Micro-Tasks:**

**Task 42.1 — Build HealthService**

In `health_service.py`, define class `HealthService`. Define `check_database() -> dict` — run `SELECT 1` and return `{"status": "ok"}` or `{"status": "error", "detail": str(e)}`. Define `check_embedding_model() -> dict` — encode a test string and return ok/error. Define `check_groq() -> dict` — call `GroqProvider().is_available()`. Define `check_qwen() -> dict` — call `QwenProvider().is_available()`. Define `get_full_health() -> dict` — run all checks and return a combined health report dict.

**Task 42.2 — Build the system router**

In `backend/api/system/router.py`, define `router = APIRouter(prefix="/api/v1/system", tags=["System"])`. Define `GET /health` that returns full health report. Define `GET /model-status` that returns just the LLM provider statuses.

**Phase 42 Checklist:**
- [x] `GET /api/v1/system/health` returns status for all subsystems
- [x] Database down is detected and reported correctly
- [x] Groq unavailable is detected and reported
- [x] Qwen unavailable is detected and reported
- [x] Overall status is `"degraded"` if any check fails, `"healthy"` if all pass

---

## Phase 43 — Analytics Collector

**Objective:** Build the analytics service that increments usage counters after every query and updates document/storage statistics after every ingestion.

**Files to Create:**

- `backend/services/analytics/analytics_service.py`

**Files to Modify:**

- `backend/services/llm/chat_service.py` — increment query and model usage counters
- `backend/services/document/ingestion_service.py` — update document and storage stats

**Micro-Tasks:**

**Task 43.1 — Build AnalyticsService**

In `analytics_service.py`, define class `AnalyticsService`. Initialize `self.analytics_repo = AnalyticsRepository()`.

Define `record_query(workspace_id: str, model_used: str) -> None`. Call `analytics_repo.increment_query_count(workspace_id)`. If `model_used` contains `"groq"`, call `increment_groq_requests`. If it contains `"qwen"`, call `increment_local_requests`.

Define `update_document_stats(workspace_id: str) -> None`. Fetch the workspace's total document count and chunk count from the workspace record. Compute total storage from the sum of all document file sizes. Call `analytics_repo.update_storage_stats(...)`.

**Task 43.2 — Wire analytics into chat and ingestion**

In `chat_service.py`, after saving conversation, call `analytics_service.record_query(workspace_id, model_used)`. In `ingestion_service.py`, after successful ingestion, call `analytics_service.update_document_stats(workspace_id)`.

**Phase 43 Checklist:**
- [x] Every successful query increments `total_queries`
- [x] Groq usage increments `groq_requests`
- [x] Local model usage increments `local_model_requests`
- [x] Post-ingestion `total_documents` and `total_chunks` are updated
- [x] Analytics row exists for every workspace (initialized in Phase 5)

---

## Phase 44 — Analytics Persistence and API Exposure — Milestone M4

**Objective:** Expose the analytics data via a REST endpoint, verify all analytics are being collected correctly, and confirm Milestone M4 (Reliable and Observable Backend) is achieved.

**Files to Create:**

- `backend/api/analytics/router.py`
- `backend/schemas/analytics_schemas.py`

**Files to Modify:**

- `backend/main.py` — include analytics router

**Micro-Tasks:**

**Task 44.1 — Define analytics schemas**

In `analytics_schemas.py`, define `AnalyticsResponse` with all fields from the analytics table plus a `last_updated` field.

**Task 44.2 — Build the analytics router**

`GET /api/v1/analytics/{workspace_id}` — returns `AnalyticsResponse` for the workspace, or 404 if the workspace doesn't exist.

**Task 44.3 — Final system validation — Milestone M4**

Perform the following end-to-end validation:

(1) Create a workspace. Upload three documents. Verify all ingest to `"completed"`. Check the analytics endpoint — `total_documents` should be 3.

(2) Submit 12 queries (triggering the summary generator at 10 messages). Verify that `total_queries` is 12 after all queries. Verify a workspace summary exists in `workspace_summaries`. Verify that subsequent queries include summary context in their prompts.

(3) Call `GET /api/v1/system/health`. Verify all subsystems report correctly.

(4) Disable Groq by setting an invalid key in `.env` (without restarting — update the settings at runtime is not supported; restart with invalid key). Restart the server. Submit a query in `"medium"` mode. Verify automatic fallback to Qwen. Re-enable Groq.

(5) Submit a query with exact keywords from a document. Verify BM25 contributes relevant results (check via the retrieval debug log showing FAISS vs BM25 chunk IDs).

(6) Verify complete workspace deletion removes: database rows (all 6 tables), FAISS files, BM25 files, upload directory.

**Phase 44 Checklist — Milestone M4:**
- [x] `GET /api/v1/analytics/{workspace_id}` returns accurate metrics
- [x] `total_queries` increments correctly with each query
- [x] Groq and local model request counts are tracked separately
- [x] Workspace summary is created after 10+ messages
- [x] Workspace summary context appears in prompt (verify via prompt debug log)
- [x] `GET /api/v1/system/health` returns accurate subsystem statuses
- [x] Groq → Qwen fallover works correctly on restart with invalid Groq key
- [x] BM25 results appear alongside FAISS results in retrieval log
- [x] Full workspace deletion cleans all six data locations
- [x] Zero unhandled 500 errors across all test scenarios
- [x] All API endpoints documented in Swagger UI

---


## Phase 45 - Frontend Project Initialization

**Phase 45 Checklist:**
- [x] Initialize Next.js project in rontend/
- [x] Configure NEXT_PUBLIC_API_URL
- [x] Tailwind CSS configured properly

---

## Phase 46 - Core API Client

**Phase 46 Checklist:**
- [x] Create src/lib/api.ts
- [x] Implement fetch wrappers for all endpoints
- [x] Error handling properly unwraps backend exceptions

---

## Phase 47 - Global Layout and Theming

**Phase 47 Checklist:**
- [x] Setup global application layout
- [x] Add Sidebar component for navigation
- [x] Apply modern aesthetic (dark/light mode variables)

---

## Phase 48 - Workspace Dashboard

**Phase 48 Checklist:**
- [x] Grid view of workspaces at /
- [x] Modal to create new workspaces
- [x] Basic workspace metadata displayed

---

## Phase 49 - Workspace Detail View

**Phase 49 Checklist:**
- [x] Layout for specific workspace workspaces/[id]/layout.tsx
- [x] Tabbed navigation (Chat, Documents, Analytics)

---

## Phase 50 - Document Ingestion UI

**Phase 50 Checklist:**
- [x] Drag-and-drop document upload interface
- [x] Display list of uploaded documents
- [x] Processing status is shown for each document

---

## Phase 51 - Chat Interface (UI)

**Phase 51 Checklist:**
- [x] Chat visual interface (messages, input box)
- [x] Render messages with markdown

---

## Phase 52 - Chat Integration & Memory

**Phase 52 Checklist:**
- [x] Fetch conversation history on mount
- [x] Send queries to backend API
- [x] Render retrieved chunks and source citations

---

## Phase 53 - Prompt Mode Toggles

**Phase 53 Checklist:**
- [x] UI selector for Simple/Medium/Expert modes
- [x] Pass selected mode to backend chat endpoint

---

## Phase 54 - Analytics Dashboard

**Phase 54 Checklist:**
- [x] Fetch telemetry data from /api/v1/analytics/{workspace_id}
- [x] Visualize queries, model usage, and storage

---

## Phase 55 - System Health Monitor

**Phase 55 Checklist:**
- [x] Fetch health from /api/v1/system/health
- [x] Display status indicators for subsystems

---

## Phase 56 - Final Polish & End-to-End Validation

**Phase 56 Checklist:**
- [x] Framer-motion transitions added
- [x] End-to-end validation (Create -> Upload -> Chat -> Analytics)

## Milestone Summary

| Milestone | Phase | Completion Criterion |
|-----------|-------|---------------------|
| **M1** | Phase 21 | Upload a PDF, ask a question, receive a source-cited answer via FAISS + Groq |
| **M2** | Phase 30 | Full Hybrid + RRF + CrossEncoder + Confidence pipeline operational |
| **M3** | Phase 36 | Context-aware conversational RAG with workspace memory and dynamic prompting |
| **M4** | Phase 44 | Complete backend: failover, logging, health monitoring, analytics all verified |

---

## Cross-Cutting Rules for the Coding Agent

These rules apply to every single phase without exception.

**Imports:** Never use relative imports inside `backend/` beyond one level. Prefer absolute imports from the package root: `from backend.services.workspace.workspace_service import WorkspaceService`. This prevents mysterious `ImportError` messages.

**No circular imports:** If module A imports B and B imports A, you have a circular import. Prevent this by keeping the dependency direction strictly one-way: `api → services → repositories → database`. Never import an `api` module from a `services` module.

**Settings access:** Always access settings via `get_settings()`, never by reading `os.environ` directly in domain code. The only file that reads the environment directly is `settings.py`.

**Singletons:** The embedding provider, cross-encoder provider, and database connection are singletons. Never instantiate them more than once. Use the `get_*` factory functions with `lru_cache`.

**Error visibility:** Never silently swallow exceptions in service code. Either handle them with a meaningful response, log them and re-raise, or log them and return a defined fallback value. Silent `except: pass` is forbidden.

**Phase completion gate:** Before marking any checklist item as done, run the specific verification described in that phase. A phase is only complete when every checklist item has been manually verified. If a verification reveals a bug in a previous phase, fix the previous phase first, re-run its verification, then continue.

**File existence check:** Before writing to any file path (FAISS, BM25, uploads), confirm the parent directory exists. Use `os.makedirs(dir, exist_ok=True)` at the top of any write operation rather than assuming directories exist.

**UTF-8 everywhere:** All file operations use `encoding="utf-8"` explicitly. Never rely on system default encoding.