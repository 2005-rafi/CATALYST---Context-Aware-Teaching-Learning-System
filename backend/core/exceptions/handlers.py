import logging
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from backend.core.exceptions.exceptions import AppException

logger = logging.getLogger(__name__)

def _build_error_payload(request: Request, error_type: str, detail: str | list | dict, status_code: int) -> dict:
    request_id = getattr(request.state, "request_id", "unknown")
    return {
        "success": False,
        "error": error_type,
        "detail": detail,
        "status_code": status_code,
        "request_id": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.warning(f"[{getattr(request.state, 'request_id', 'unknown')}] AppException {type(exc).__name__}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content=_build_error_payload(request, type(exc).__name__, exc.detail, exc.status_code)
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        formatted_errors = []
        for err in exc.errors():
            field = " -> ".join(str(loc) for loc in err.get("loc", []))
            formatted_errors.append(f"{field}: {err.get('msg', 'Invalid value')}")
        detail_msg = "; ".join(formatted_errors) if formatted_errors else "Request validation failed"
        logger.warning(f"[{getattr(request.state, 'request_id', 'unknown')}] Validation error: {detail_msg}")
        return JSONResponse(
            status_code=422,
            content=_build_error_payload(request, "ValidationError", detail_msg, 422)
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(f"[{getattr(request.state, 'request_id', 'unknown')}] HTTP {exc.status_code}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content=_build_error_payload(request, "HTTPException", str(exc.detail), exc.status_code)
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"[{getattr(request.state, 'request_id', 'unknown')}] Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=_build_error_payload(request, "InternalServerError", "An unexpected server error occurred.", 500)
        )
