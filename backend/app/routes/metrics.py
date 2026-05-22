from typing import Annotated

from fastapi import APIRouter, Depends

from app.repositories.inference_logs import InferenceLogRepository
from app.routes.deps import get_inference_log_repository
from app.schemas.metrics import DashboardMetrics

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/dashboard", response_model=DashboardMetrics)
async def dashboard_metrics(
    repository: Annotated[InferenceLogRepository, Depends(get_inference_log_repository)],
) -> dict:
    return await repository.dashboard_metrics()
