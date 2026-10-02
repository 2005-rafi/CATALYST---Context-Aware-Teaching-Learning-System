Based on the implementation roadmap we've finalized, I would simplify and align the folder hierarchy directly to the actual phases and pipelines. Your previous structure is good architecturally, but it still has a few layers (such as `pipelines/`) that may become redundant for an MVP.

I would recommend the following:

```text
project-root/
│
├── frontend/
│   │
│   ├── app/
│   │
│   ├── components/
│   │   ├── workspace/
│   │   ├── upload/
│   │   ├── chat/
│   │   ├── analytics/
│   │   └── shared/
│   │
│   ├── services/
│   │
│   ├── store/
│   │
│   ├── hooks/
│   │
│   ├── models/
│   │
│   ├── utils/
│   │
│   ├── constants/
│   │
│   └── styles/
│
│
├── backend/
│   │
│   ├── api/
│   │   ├── workspace/
│   │   ├── document/
│   │   ├── chat/
│   │   ├── analytics/
│   │   └── system/
│   │
│   ├── services/
│   │   ├── workspace/
│   │   ├── document/
│   │   ├── retrieval/
│   │   ├── memory/
│   │   ├── llm/
│   │   └── analytics/
│   │
│   ├── repositories/
│   │   ├── sqlite/
│   │   ├── vector/
│   │   └── bm25/
│   │
│   ├── providers/
│   │   ├── embeddings/
│   │   ├── groq/
│   │   └── qwen/
│   │
│   ├── schemas/
│   │
│   ├── models/
│   │
│   ├── core/
│   │   ├── config/
│   │   ├── logging/
│   │   ├── exceptions/
│   │   └── startup/
│   │
│   ├── utils/
│   │
│   ├── tests/
│   │
│   └── logs/
│
│
├── storage/
│   │
│   ├── uploads/
│   │   └── workspaces/
│   │
│   ├── sqlite/
│   │
│   ├── vectors/
│   │   └── faiss/
│   │
│   ├── bm25/
│   │
│   ├── cache/
│   │
│   └── exports/
│
│
├── secrets/
│   │
│   ├── .env
│   │
│   └── templates/
│
│
└── docs/
```

Why this version is better:

* Only **4 top-level engineering folders**:

  * `frontend`
  * `backend`
  * `storage`
  * `secrets`

* Directly maps to your implementation phases:

  * Workspace Management
  * Document Processing
  * Retrieval
  * Memory
  * LLM
  * Analytics

* Removes the extra `pipelines/` layer because orchestration can live inside Services for the MVP.

* Keeps all persistent data completely outside application code:

  * SQLite DB
  * FAISS indexes
  * BM25 indexes
  * Uploaded documents
  * Cached artifacts

* `secrets/.env` becomes the single location for:

  * Groq API Key
  * HuggingFace Token
  * Model Configuration
  * Retrieval Configuration Overrides
  * Debug Flags

Example:

```env
GROQ_API_KEY=
HF_TOKEN=

ENABLE_BM25=true
ENABLE_RRF=true
ENABLE_CROSS_ENCODER=true
ENABLE_LOCAL_MODEL=true

LOG_LEVEL=INFO
```

* Easier deployment:

```text
frontend/
backend/
storage/
secrets/
```

Everything important lives inside these four folders, which makes backup, debugging, local deployment, and future Dockerization significantly easier.

This structure is lean, maps directly to your architecture decisions, and is unlikely to require major refactoring during development. It also keeps the codebase aligned with the phased implementation plan we've defined. Based on the current design, this would be my final recommended hierarchy. It remains consistent with the earlier architecture while reducing unnecessary nesting and complexity. 
