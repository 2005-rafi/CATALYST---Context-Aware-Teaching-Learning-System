from fastapi import APIRouter, Depends
from backend.services.system.health_service import HealthService
from backend.schemas.system_schemas import HealthResponse
from backend.core.dependencies import get_health_service

router = APIRouter(prefix="/api/v1/system", tags=["System"])


@router.get("/health", response_model=HealthResponse)
def get_health(service: HealthService = Depends(get_health_service)):
    return service.get_full_health()


@router.get("/model-status")
def get_model_status(service: HealthService = Depends(get_health_service)):
    return {
        "groq": service.check_groq(),
        "qwen": service.check_qwen()
    }
