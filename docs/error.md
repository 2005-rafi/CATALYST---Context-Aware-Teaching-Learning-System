# Terminal
```bash
INFO:     Will watch for changes in these directories: ['F:\\Studies\\Project\\11. NLP\\RAG Application\\Implementation_2']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [16672] using WatchFiles
INFO:     Started server process [18376]
INFO:     Waiting for application startup.
2026-10-02 16:56:47,792 | backend.core.startup.lifespan | INFO | Application starting
2026-10-02 16:56:47,796 | backend.core.startup.lifespan | INFO | Preloading embedding models...
2026-10-02 16:56:47,796 | backend.providers.embeddings.embedding_provider | INFO | Initializing embedding model: sentence-transformers/all-MiniLM-L6-v2
2026-10-02 16:56:47,797 | sentence_transformers.base.model | INFO | No device provided, using cpu
2026-10-02 16:56:48,287 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/modules.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:48,306 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/sentence-transformers/all-MiniLM-L6-v2/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/modules.json "HTTP/1.1 200 OK"
2026-10-02 16:56:48,543 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/config_sentence_transformers.json "HTTP/1.1 307 Temporary Redirect"
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
2026-10-02 16:56:48,544 | huggingface_hub.utils._http | WARNING | Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
2026-10-02 16:56:48,565 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/sentence-transformers/all-MiniLM-L6-v2/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/config_sentence_transformers.json "HTTP/1.1 200 OK"
2026-10-02 16:56:48,566 | sentence_transformers.base.model | INFO | Loading SentenceTransformer model from sentence-transformers/all-MiniLM-L6-v2.
2026-10-02 16:56:48,799 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/config_sentence_transformers.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:48,819 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/sentence-transformers/all-MiniLM-L6-v2/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/config_sentence_transformers.json "HTTP/1.1 200 OK"
2026-10-02 16:56:49,055 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/README.md "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:49,078 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/sentence-transformers/all-MiniLM-L6-v2/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/README.md "HTTP/1.1 200 OK"
2026-10-02 16:56:49,313 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/modules.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:49,333 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/sentence-transformers/all-MiniLM-L6-v2/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/modules.json "HTTP/1.1 200 OK"
2026-10-02 16:56:49,567 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/sentence_bert_config.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:49,587 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/sentence-transformers/all-MiniLM-L6-v2/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/sentence_bert_config.json "HTTP/1.1 200 OK"
2026-10-02 16:56:49,820 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/adapter_config.json "HTTP/1.1 404 Not Found"
2026-10-02 16:56:50,057 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/config.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:50,076 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/sentence-transformers/all-MiniLM-L6-v2/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/config.json "HTTP/1.1 200 OK"
Loading weights: 100%|███████████████████████████████████████████████████████████████████████████████████████████| 103/103 [00:00<00:00, 5685.81it/s]
2026-10-02 16:56:50,437 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/processor_config.json "HTTP/1.1 404 Not Found"
2026-10-02 16:56:50,800 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/preprocessor_config.json "HTTP/1.1 404 Not Found"
2026-10-02 16:56:51,040 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/video_preprocessor_config.json "HTTP/1.1 404 Not Found"
2026-10-02 16:56:51,319 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/preprocessor_config.json "HTTP/1.1 404 Not Found"
2026-10-02 16:56:51,557 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/tokenizer_config.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:51,576 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/sentence-transformers/all-MiniLM-L6-v2/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/tokenizer_config.json "HTTP/1.1 200 OK"
2026-10-02 16:56:51,807 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/config.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:51,828 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/sentence-transformers/all-MiniLM-L6-v2/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/config.json "HTTP/1.1 200 OK"
2026-10-02 16:56:52,066 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/config.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:52,084 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/sentence-transformers/all-MiniLM-L6-v2/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/config.json "HTTP/1.1 200 OK"
2026-10-02 16:56:52,318 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/tokenizer_config.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:52,337 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/sentence-transformers/all-MiniLM-L6-v2/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/tokenizer_config.json "HTTP/1.1 200 OK"
2026-10-02 16:56:52,575 | httpx | INFO | HTTP Request: GET https://huggingface.co/api/models/sentence-transformers/all-MiniLM-L6-v2/tree/main/additional_chat_templates?recursive=false&expand=false "HTTP/1.1 404 Not Found"
2026-10-02 16:56:52,815 | httpx | INFO | HTTP Request: GET https://huggingface.co/api/models/sentence-transformers/all-MiniLM-L6-v2/tree/main?recursive=true&expand=false "HTTP/1.1 200 OK"
2026-10-02 16:56:53,093 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/1_Pooling/config.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:53,110 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/sentence-transformers/all-MiniLM-L6-v2/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/1_Pooling%2Fconfig.json "HTTP/1.1 200 OK"
2026-10-02 16:56:53,351 | httpx | INFO | HTTP Request: GET https://huggingface.co/api/models/sentence-transformers/all-MiniLM-L6-v2 "HTTP/1.1 200 OK"
2026-10-02 16:56:53,361 | sentence_transformers.base.model | INFO | No device provided, using cpu
2026-10-02 16:56:53,593 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2/resolve/main/modules.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:53,825 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2/resolve/main/modules.json "HTTP/1.1 404 Not Found"
2026-10-02 16:56:53,827 | sentence_transformers.base.model | INFO | No modules.json found for cross-encoder/ms-marco-MiniLM-L-6-v2, initializing a new CrossEncoder model.
2026-10-02 16:56:54,062 | httpx | INFO | HTTP Request: GET https://huggingface.co/api/models/cross-encoder/ms-marco-MiniLM-L-6-v2 "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:54,306 | httpx | INFO | HTTP Request: GET https://huggingface.co/api/models/cross-encoder/ms-marco-MiniLM-L6-v2 "HTTP/1.1 200 OK"
2026-10-02 16:56:54,540 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2/resolve/main/config.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:54,776 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2/resolve/main/config.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:54,796 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/cross-encoder/ms-marco-MiniLM-L6-v2/233902d25c440f23af6f7d6e94d2946bac0bee0a/config.json "HTTP/1.1 200 OK"
2026-10-02 16:56:55,033 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2/resolve/main/adapter_config.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:55,269 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2/resolve/main/adapter_config.json "HTTP/1.1 404 Not Found"
2026-10-02 16:56:55,508 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2/resolve/main/config.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:55,746 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2/resolve/main/config.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:55,766 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/cross-encoder/ms-marco-MiniLM-L6-v2/233902d25c440f23af6f7d6e94d2946bac0bee0a/config.json "HTTP/1.1 200 OK"
Loading weights: 100%|███████████████████████████████████████████████████████████████████████████████████████████| 105/105 [00:00<00:00, 6828.57it/s]
2026-10-02 16:56:56,051 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2/resolve/main/processor_config.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:56,284 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2/resolve/main/processor_config.json "HTTP/1.1 404 Not Found"
2026-10-02 16:56:56,520 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2/resolve/main/preprocessor_config.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:56,760 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2/resolve/main/preprocessor_config.json "HTTP/1.1 404 Not Found"
2026-10-02 16:56:57,002 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2/resolve/main/video_preprocessor_config.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:57,237 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2/resolve/main/video_preprocessor_config.json "HTTP/1.1 404 Not Found"
2026-10-02 16:56:57,467 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2/resolve/main/preprocessor_config.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:57,698 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2/resolve/main/preprocessor_config.json "HTTP/1.1 404 Not Found"
2026-10-02 16:56:57,935 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2/resolve/main/tokenizer_config.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:58,170 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2/resolve/main/tokenizer_config.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:58,189 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/cross-encoder/ms-marco-MiniLM-L6-v2/233902d25c440f23af6f7d6e94d2946bac0bee0a/tokenizer_config.json "HTTP/1.1 200 OK"
2026-10-02 16:56:58,426 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2/resolve/main/config.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:58,663 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2/resolve/main/config.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:58,682 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/cross-encoder/ms-marco-MiniLM-L6-v2/233902d25c440f23af6f7d6e94d2946bac0bee0a/config.json "HTTP/1.1 200 OK"
2026-10-02 16:56:58,927 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2/resolve/main/config.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:59,158 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2/resolve/main/config.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:59,176 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/cross-encoder/ms-marco-MiniLM-L6-v2/233902d25c440f23af6f7d6e94d2946bac0bee0a/config.json "HTTP/1.1 200 OK"
2026-10-02 16:56:59,413 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2/resolve/main/tokenizer_config.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:59,649 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2/resolve/main/tokenizer_config.json "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:56:59,673 | httpx | INFO | HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/cross-encoder/ms-marco-MiniLM-L6-v2/233902d25c440f23af6f7d6e94d2946bac0bee0a/tokenizer_config.json "HTTP/1.1 200 OK"
2026-10-02 16:56:59,913 | httpx | INFO | HTTP Request: GET https://huggingface.co/api/models/cross-encoder/ms-marco-MiniLM-L-6-v2/tree/main/additional_chat_templates?recursive=false&expand=false "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:57:00,146 | httpx | INFO | HTTP Request: GET https://huggingface.co/api/models/cross-encoder/ms-marco-MiniLM-L6-v2/tree/main/additional_chat_templates?recursive=false&expand=false "HTTP/1.1 404 Not Found"
2026-10-02 16:57:00,384 | httpx | INFO | HTTP Request: GET https://huggingface.co/api/models/cross-encoder/ms-marco-MiniLM-L-6-v2/tree/main?recursive=true&expand=false "HTTP/1.1 307 Temporary Redirect"
2026-10-02 16:57:00,655 | httpx | INFO | HTTP Request: GET https://huggingface.co/api/models/cross-encoder/ms-marco-MiniLM-L6-v2/tree/main?recursive=true&expand=false "HTTP/1.1 200 OK"
2026-10-02 16:57:00,689 | backend.core.startup.lifespan | INFO | All systems initialized
INFO:     Application startup complete.
INFO:     127.0.0.1:50330 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:65039 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:57966 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:61707 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:53335 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:61340 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:49855 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:53796 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:54370 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:53308 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:53966 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:50805 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:53255 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:52872 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:59422 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:55155 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:52406 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:49367 - "GET /api/v1/system/health HTTP/1.1" 200 OK
INFO:     127.0.0.1:52058 - "GET /api/v1/system/health HTTP/1.1" 200 OK
```