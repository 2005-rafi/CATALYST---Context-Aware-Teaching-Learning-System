# Terminal
```bash
INFO:     Will watch for changes in these directories: ['F:\\Studies\\Project\\11. NLP\\RAG Application\\Implementation_2']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [22248] using WatchFiles
INFO:     Started server process [3080]
INFO:     Waiting for application startup.
2026-10-02 18:32:56 | INFO     | backend.core.startup.lifespan | Application starting
2026-10-02 18:32:56 | INFO     | backend.core.startup.lifespan | Preloading embedding models...
2026-10-02 18:32:56 | INFO     | backend.providers.embeddings.embedding_provider | Loading embedding model offline from local store: storage\models\embeddings\sentence-transformers_all-MiniLM-L6-v2
Loading weights: 100%|███████████████████████████████████████████████████████████████████████████████████████████| 103/103 [00:00<00:00, 5307.16it/s]
2026-10-02 18:32:56 | INFO     | backend.providers.embeddings.cross_encoder_provider | Loading cross-encoder model offline from local store: storage\models\cross_encoder\cross-encoder_ms-marco-MiniLM-L-6-v2
Loading weights: 100%|███████████████████████████████████████████████████████████████████████████████████████████| 105/105 [00:00<00:00, 4996.56it/s]
2026-10-02 18:32:56 | INFO     | backend.core.startup.lifespan | All systems initialized
INFO:     Application startup complete.
2026-10-02 18:33:05 | INFO     | backend.main | [eb18057a] --> GET /api/v1/workspace/
2026-10-02 18:33:05 | INFO     | backend.main | [eb18057a] <-- GET /api/v1/workspace/ - Status: 200 (4.0ms)
INFO:     127.0.0.1:59215 - "GET /api/v1/workspace/ HTTP/1.1" 200 OK
2026-10-02 18:33:07 | INFO     | backend.main | [8e327cff] --> GET /api/v1/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c
2026-10-02 18:33:07 | INFO     | backend.main | [8e327cff] <-- GET /api/v1/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c - Status: 200 (5.2ms)
INFO:     127.0.0.1:59215 - "GET /api/v1/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c HTTP/1.1" 200 OK
2026-10-02 18:33:07 | INFO     | backend.main | [c11f1605] --> GET /api/v1/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c
2026-10-02 18:33:07 | INFO     | backend.main | [c11f1605] <-- GET /api/v1/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c - Status: 200 (3.9ms)
INFO:     127.0.0.1:59215 - "GET /api/v1/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c HTTP/1.1" 200 OK
INFO:     127.0.0.1:55728 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:55728 - "GET /api/v1/system/health HTTP/1.1" 200 OK
2026-10-02 18:33:07 | INFO     | backend.main | [a0cba21e] --> GET /api/v1/chat/history/d23b3143-2b9c-4bd1-bd5a-e71d9666935c
2026-10-02 18:33:07 | INFO     | backend.main | [a0cba21e] <-- GET /api/v1/chat/history/d23b3143-2b9c-4bd1-bd5a-e71d9666935c - Status: 200 (4.3ms)
INFO:     127.0.0.1:55728 - "GET /api/v1/chat/history/d23b3143-2b9c-4bd1-bd5a-e71d9666935c HTTP/1.1" 200 OK
2026-10-02 18:33:07 | INFO     | backend.main | [d2bccbdc] --> GET /api/v1/chat/history/d23b3143-2b9c-4bd1-bd5a-e71d9666935c
2026-10-02 18:33:07 | INFO     | backend.main | [d2bccbdc] <-- GET /api/v1/chat/history/d23b3143-2b9c-4bd1-bd5a-e71d9666935c - Status: 200 (3.0ms)
INFO:     127.0.0.1:59215 - "GET /api/v1/chat/history/d23b3143-2b9c-4bd1-bd5a-e71d9666935c HTTP/1.1" 200 OK
2026-10-02 18:33:12 | INFO     | backend.main | [2e43902e] --> GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c
2026-10-02 18:33:12 | INFO     | backend.main | [2e43902e] <-- GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c - Status: 200 (4.3ms)
INFO:     127.0.0.1:59215 - "GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c HTTP/1.1" 200 OK
2026-10-02 18:33:12 | INFO     | backend.main | [8bd6de11] --> GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c
2026-10-02 18:33:12 | INFO     | backend.main | [8bd6de11] <-- GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c - Status: 200 (3.4ms)
INFO:     127.0.0.1:55728 - "GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c HTTP/1.1" 200 OK
2026-10-02 18:33:15 | INFO     | backend.main | [8abf0181] --> OPTIONS /api/v1/document/cd4a2104-3911-4835-9c56-d4e2633d0afc
2026-10-02 18:33:15 | INFO     | backend.main | [8abf0181] <-- OPTIONS /api/v1/document/cd4a2104-3911-4835-9c56-d4e2633d0afc - Status: 200 (0.7ms)
INFO:     127.0.0.1:55728 - "OPTIONS /api/v1/document/cd4a2104-3911-4835-9c56-d4e2633d0afc HTTP/1.1" 200 OK
2026-10-02 18:33:15 | INFO     | backend.main | [5910e52e] --> DELETE /api/v1/document/cd4a2104-3911-4835-9c56-d4e2633d0afc
2026-10-02 18:33:15 | INFO     | backend.services.document.document_deletion_service | Deleted physical file: storage/uploads/workspaces\d23b3143-2b9c-4bd1-bd5a-e71d9666935c\cd4a2104-3911-4835-9c56-d4e2633d0afc_TN-Std12-Zoology-EM.pdf
2026-10-02 18:33:15 | INFO     | backend.main | [9a805ae3] --> GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c
2026-10-02 18:33:15 | INFO     | backend.main | [9a805ae3] <-- GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c - Status: 200 (2.7ms)
INFO:     127.0.0.1:59215 - "GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c HTTP/1.1" 200 OK
2026-10-02 18:33:15 | INFO     | backend.services.document.document_deletion_service | Deleted chunks for document: cd4a2104-3911-4835-9c56-d4e2633d0afc
2026-10-02 18:33:15 | INFO     | backend.services.document.document_deletion_service | Document deletion complete: cd4a2104-3911-4835-9c56-d4e2633d0afc (workspace=d23b3143-2b9c-4bd1-bd5a-e71d9666935c, chunks=523)
2026-10-02 18:33:15 | INFO     | backend.main | [5910e52e] <-- DELETE /api/v1/document/cd4a2104-3911-4835-9c56-d4e2633d0afc - Status: 204 (79.1ms)
INFO:     127.0.0.1:55728 - "DELETE /api/v1/document/cd4a2104-3911-4835-9c56-d4e2633d0afc HTTP/1.1" 204 No Content
2026-10-02 18:33:15 | INFO     | backend.main | [46d51e26] --> GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c
2026-10-02 18:33:15 | INFO     | backend.main | [46d51e26] <-- GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c - Status: 200 (3.8ms)
INFO:     127.0.0.1:55728 - "GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c HTTP/1.1" 200 OK
INFO:     127.0.0.1:62607 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:54891 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:54891 - "GET /api/v1/system/health HTTP/1.1" 200 OK
2026-10-02 18:34:54 | INFO     | backend.main | [7395c371] --> POST /api/v1/document/upload
2026-10-02 18:34:55 | INFO     | backend.main | [7395c371] <-- POST /api/v1/document/upload - Status: 202 (1527.6ms)
INFO:     127.0.0.1:54891 - "POST /api/v1/document/upload HTTP/1.1" 202 Accepted
2026-10-02 18:34:55 | INFO     | backend.services.document.ingestion_service | Running pipeline stage: ExtractorStage
2026-10-02 18:34:55 | INFO     | backend.main | [09064111] --> GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c
Consider using the pymupdf_layout package for a greatly improved page layout analysis.
2026-10-02 18:34:56 | INFO     | backend.main | [09064111] <-- GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c - Status: 200 (753.6ms)
INFO:     127.0.0.1:54891 - "GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c HTTP/1.1" 200 OK
INFO:     127.0.0.1:54891 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:54891 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:52817 - "GET /api/v1/system/health HTTP/1.1" 200 OK
2026-10-02 18:35:39 | INFO     | backend.services.document.ingestion_service | Extraction completed
2026-10-02 18:35:39 | INFO     | backend.services.document.ingestion_service | Running pipeline stage: SanitizerStage
2026-10-02 18:35:39 | INFO     | backend.services.document.ingestion_service | Running pipeline stage: ChunkingStage
2026-10-02 18:35:40 | INFO     | backend.services.document.ingestion_service | Chunking completed
2026-10-02 18:35:40 | INFO     | backend.services.document.ingestion_service | Running pipeline stage: SQLCacheStage
2026-10-02 18:35:40 | INFO     | backend.services.document.ingestion_service | Running pipeline stage: VectorIngestionStage
2026-10-02 18:35:56 | INFO     | backend.services.document.ingestion_service | Embedding completed
2026-10-02 18:35:56 | INFO     | backend.services.document.ingestion_service | Running pipeline stage: LexicalIngestionStage
2026-10-02 18:35:56 | INFO     | backend.services.document.ingestion_service | BM25 indexed
INFO:     127.0.0.1:56244 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:56244 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:56977 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:59935 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:65494 - "GET /api/v1/system/health HTTP/1.1" 200 OK
2026-10-02 18:54:26 | INFO     | backend.main | [68949f0f] --> GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c
2026-10-02 18:54:26 | INFO     | backend.main | [4076423b] --> GET /api/v1/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c
2026-10-02 18:54:26 | INFO     | backend.main | [68949f0f] <-- GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c - Status: 200 (6.7ms)
INFO:     127.0.0.1:61189 - "GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c HTTP/1.1" 200 OK
2026-10-02 18:54:26 | INFO     | backend.main | [4076423b] <-- GET /api/v1/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c - Status: 200 (13.1ms)
INFO:     127.0.0.1:54344 - "GET /api/v1/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c HTTP/1.1" 200 OK
INFO:     127.0.0.1:59442 - "GET /api/v1/system/health HTTP/1.1" 200 OK
2026-10-02 18:54:30 | INFO     | backend.main | [9ce9e740] --> GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c
2026-10-02 18:54:30 | INFO     | backend.main | [9ce9e740] <-- GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c - Status: 200 (3.2ms)
INFO:     127.0.0.1:59442 - "GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c HTTP/1.1" 200 OK
```