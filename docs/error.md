# Terminal
```bashINFO:     Will watch for changes in these directories: ['F:\\Studies\\Project\\11. NLP\\RAG Application\\Implementation_2']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [15128] using WatchFiles
INFO:     Started server process [22716]
INFO:     Waiting for application startup.
2026-10-02 18:14:57 | INFO     | backend.core.startup.lifespan | Application starting
2026-10-02 18:14:57 | INFO     | backend.core.startup.lifespan | Preloading embedding models...
2026-10-02 18:14:57 | INFO     | backend.providers.embeddings.embedding_provider | Loading embedding model offline from local store: storage\models\embeddings\sentence-transformers_all-MiniLM-L6-v2
Loading weights: 100%|███████████████████████████████████████████████████████████████████████████████████████████| 103/103 [00:00<00:00, 4558.64it/s]
2026-10-02 18:14:57 | INFO     | backend.providers.embeddings.cross_encoder_provider | Loading cross-encoder model offline from local store: storage\models\cross_encoder\cross-encoder_ms-marco-MiniLM-L-6-v2
Loading weights: 100%|███████████████████████████████████████████████████████████████████████████████████████████| 105/105 [00:00<00:00, 4820.19it/s]
2026-10-02 18:14:57 | INFO     | backend.core.startup.lifespan | All systems initialized
INFO:     Application startup complete.
INFO:     127.0.0.1:55243 - "GET /api/v1/system/health HTTP/1.1" 200 OK
2026-10-02 18:15:15 | INFO     | backend.main | [1d693de0] --> GET /api/v1/workspace/
2026-10-02 18:15:15 | INFO     | backend.main | [1d693de0] <-- GET /api/v1/workspace/ - Status: 200 (4.2ms)
INFO:     127.0.0.1:57391 - "GET /api/v1/workspace/ HTTP/1.1" 200 OK
INFO:     127.0.0.1:57391 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:57391 - "GET /api/v1/system/health HTTP/1.1" 200 OK
2026-10-02 18:15:17 | INFO     | backend.main | [02100563] --> GET /api/v1/workspace/
2026-10-02 18:15:17 | INFO     | backend.main | [02100563] <-- GET /api/v1/workspace/ - Status: 200 (3.8ms)
INFO:     127.0.0.1:60899 - "GET /api/v1/workspace/ HTTP/1.1" 200 OK
INFO:     127.0.0.1:58217 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:61082 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:63833 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:60523 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:54808 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:50817 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:59440 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:53097 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:54205 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:51675 - "GET /api/v1/system/health HTTP/1.1" 200 OK
2026-10-02 18:17:47 | INFO     | backend.main | [f5cfe465] --> OPTIONS /api/v1/workspace/
2026-10-02 18:17:47 | INFO     | backend.main | [f5cfe465] <-- OPTIONS /api/v1/workspace/ - Status: 200 (0.6ms)
INFO:     127.0.0.1:57475 - "OPTIONS /api/v1/workspace/ HTTP/1.1" 200 OK
2026-10-02 18:17:47 | INFO     | backend.main | [817f7168] --> POST /api/v1/workspace/
2026-10-02 18:17:47 | INFO     | backend.main | [817f7168] <-- POST /api/v1/workspace/ - Status: 201 (14.9ms)
INFO:     127.0.0.1:57475 - "POST /api/v1/workspace/ HTTP/1.1" 201 Created
2026-10-02 18:17:47 | INFO     | backend.main | [9753e4ce] --> GET /api/v1/workspace/
2026-10-02 18:17:47 | INFO     | backend.main | [9753e4ce] <-- GET /api/v1/workspace/ - Status: 200 (3.4ms)
INFO:     127.0.0.1:57475 - "GET /api/v1/workspace/ HTTP/1.1" 200 OK
INFO:     127.0.0.1:62042 - "GET /api/v1/system/health HTTP/1.1" 200 OK
2026-10-02 18:17:50 | INFO     | backend.main | [37b9cf4e] --> GET /api/v1/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c
2026-10-02 18:17:50 | INFO     | backend.main | [37b9cf4e] <-- GET /api/v1/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c - Status: 200 (4.3ms)
INFO:     127.0.0.1:62042 - "GET /api/v1/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c HTTP/1.1" 200 OK
2026-10-02 18:17:50 | INFO     | backend.main | [c76802cd] --> GET /api/v1/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c
2026-10-02 18:17:50 | INFO     | backend.main | [c76802cd] <-- GET /api/v1/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c - Status: 200 (4.2ms)
INFO:     127.0.0.1:57475 - "GET /api/v1/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c HTTP/1.1" 200 OK
2026-10-02 18:17:50 | INFO     | backend.main | [bc211d68] --> GET /api/v1/chat/history/d23b3143-2b9c-4bd1-bd5a-e71d9666935c
2026-10-02 18:17:50 | INFO     | backend.main | [bc211d68] <-- GET /api/v1/chat/history/d23b3143-2b9c-4bd1-bd5a-e71d9666935c - Status: 200 (3.7ms)
INFO:     127.0.0.1:57475 - "GET /api/v1/chat/history/d23b3143-2b9c-4bd1-bd5a-e71d9666935c HTTP/1.1" 200 OK
2026-10-02 18:17:50 | INFO     | backend.main | [8a8d45ff] --> GET /api/v1/chat/history/d23b3143-2b9c-4bd1-bd5a-e71d9666935c
2026-10-02 18:17:50 | INFO     | backend.main | [8a8d45ff] <-- GET /api/v1/chat/history/d23b3143-2b9c-4bd1-bd5a-e71d9666935c - Status: 200 (3.3ms)
INFO:     127.0.0.1:62042 - "GET /api/v1/chat/history/d23b3143-2b9c-4bd1-bd5a-e71d9666935c HTTP/1.1" 200 OK
2026-10-02 18:17:53 | INFO     | backend.main | [30442d60] --> GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c
2026-10-02 18:17:53 | INFO     | backend.main | [30442d60] <-- GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c - Status: 200 (3.7ms)
INFO:     127.0.0.1:62042 - "GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c HTTP/1.1" 200 OK
2026-10-02 18:17:53 | INFO     | backend.main | [e2097801] --> GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c
2026-10-02 18:17:53 | INFO     | backend.main | [e2097801] <-- GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c - Status: 200 (4.3ms)
INFO:     127.0.0.1:57475 - "GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c HTTP/1.1" 200 OK
2026-10-02 18:17:56 | INFO     | backend.main | [d96d4e86] --> GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c
2026-10-02 18:17:56 | INFO     | backend.main | [d96d4e86] <-- GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c - Status: 200 (15.0ms)
INFO:     127.0.0.1:57475 - "GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c HTTP/1.1" 200 OK
INFO:     127.0.0.1:57475 - "GET /api/v1/system/health HTTP/1.1" 200 OK
2026-10-02 18:18:02 | INFO     | backend.main | [8c9ad9c1] --> POST /api/v1/document/upload
2026-10-02 18:18:04 | INFO     | backend.main | [8c9ad9c1] <-- POST /api/v1/document/upload - Status: 202 (1338.1ms)
INFO:     127.0.0.1:49727 - "POST /api/v1/document/upload HTTP/1.1" 202 Accepted
2026-10-02 18:18:04 | INFO     | backend.services.document.ingestion_service | Running pipeline stage: ExtractorStage
2026-10-02 18:18:04 | INFO     | backend.main | [06e83765] --> GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c
2026-10-02 18:18:04 | INFO     | backend.main | [06e83765] <-- GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c - Status: 200 (138.9ms)
INFO:     127.0.0.1:49727 - "GET /api/v1/document/workspace/d23b3143-2b9c-4bd1-bd5a-e71d9666935c HTTP/1.1" 200 OK
INFO:     127.0.0.1:49727 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:65315 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:54649 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:59927 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:63852 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:50608 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:58625 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:63351 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:58361 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:64543 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:65108 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:50873 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:63623 - "GET /api/v1/system/health HTTP/1.1" 200 OK
2026-10-02 18:20:12 | INFO     | backend.services.document.ingestion_service | Extraction completed
2026-10-02 18:20:12 | INFO     | backend.services.document.ingestion_service | Running pipeline stage: SanitizerStage
2026-10-02 18:20:13 | INFO     | backend.services.document.ingestion_service | Running pipeline stage: ChunkingStage
2026-10-02 18:20:14 | INFO     | backend.services.document.ingestion_service | Chunking completed
2026-10-02 18:20:14 | INFO     | backend.services.document.ingestion_service | Running pipeline stage: SQLCacheStage
2026-10-02 18:20:19 | INFO     | backend.services.document.ingestion_service | Running pipeline stage: VectorIngestionStage
INFO:     127.0.0.1:63623 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:53569 - "GET /api/v1/system/health HTTP/1.1" 200 OK
F:\Studies\Project\11. NLP\RAG Application\Implementation_2\backend\repositories\vector\faiss_manager.py:21: FutureWarning: The `get_sentence_embedding_dimension` method has been renamed to `get_embedding_dimension`.
  self._dimension = get_embedding_provider().model.get_sentence_embedding_dimension()
2026-10-02 18:20:38 | INFO     | backend.services.document.ingestion_service | Embedding completed
2026-10-02 18:20:38 | INFO     | backend.services.document.ingestion_service | Running pipeline stage: LexicalIngestionStage
2026-10-02 18:20:38 | INFO     | backend.services.document.ingestion_service | BM25 indexed
INFO:     127.0.0.1:56913 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:55269 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:51857 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:59461 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:58539 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:61308 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:63607 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:61259 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:61259 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:63411 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:52963 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:57180 - "GET /api/v1/system/health HTTP/1.1" 200 OK

```