import time
import uuid
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.core.startup.lifespan import lifespan
from backend.core.exceptions.handlers import register_exception_handlers
from backend.core.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

from backend.api.workspace.router import router as workspace_router
from backend.api.document.router import router as document_router
from backend.api.chat.router import router as chat_router
from backend.api.system.router import router as system_router
from backend.api.analytics.router import router as analytics_router

app = FastAPI(title="RAG Document Intelligence", version="1.0.0", lifespan=lifespan)

# CORS configuration
is_wildcard = "*" in settings.ALLOWED_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=not is_wildcard,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS", "PUT", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Response-Time-MS"],
)

app.include_router(workspace_router)
app.include_router(document_router)
app.include_router(chat_router)
app.include_router(system_router)
app.include_router(analytics_router)

# Register Exception Handlers
register_exception_handlers(app)

@app.middleware("http")
async def request_lifecycle_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    start_time = time.perf_counter()
    
    is_health_poll = request.url.path in ["/api/v1/system/health", "/"]
    
    if not is_health_poll:
        logger.info(f"[{request_id}] --> {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    duration_ms = (time.perf_counter() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-MS"] = f"{duration_ms:.2f}"
    
    status_code = response.status_code
    msg = f"[{request_id}] <-- {request.method} {request.url.path} - Status: {status_code} ({duration_ms:.1f}ms)"
    
    if not is_health_poll or status_code >= 400:
        if 500 <= status_code < 600:
            logger.error(msg)
        elif 400 <= status_code < 500:
            logger.warning(msg)
        else:
            logger.info(msg)
        
    return response

@app.get("/")
def root_status():
    return {"status": "operational", "service": "RAG Document Intelligence API", "version": "1.0.0"}
