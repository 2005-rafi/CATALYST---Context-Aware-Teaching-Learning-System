"""System health and operational diagnostic API endpoints."""
from fastapi import APIRouter, Depends
from backend.services.system.health_service import HealthService
from backend.schemas.system import HealthResponse
from backend.core.dependencies import get_health_service

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/health", response_model=HealthResponse)
def get_health(service: HealthService = Depends(get_health_service)):
    """Get overall system health and subsystem statuses."""
    return service.get_full_health()


@router.get("/model-status")
def get_model_status(service: HealthService = Depends(get_health_service)):
    """Get live availability statuses for Groq and Ollama/Qwen models."""
    return {
        "groq": service.check_groq(),
        "qwen": service.check_qwen()
    }


@router.get("/metrics")
def get_system_metrics():
    """Return runtime memory and resource usage for observability on cloud environments."""
    try:
        import psutil
        import os
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        return {
            "rss_mb": round(mem_info.rss / 1024 / 1024, 2),
            "vms_mb": round(mem_info.vms / 1024 / 1024, 2),
            "cpu_percent": process.cpu_percent(interval=None),
            "threads_count": process.num_threads() if hasattr(process, "num_threads") else 1,
            "status": "healthy"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "degraded"
        }

