from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.ingest import InferenceLogCreate, IngestResponse
from app.services.ingestion import IngestionService
from app.routes.deps import get_ingestion_service

router = APIRouter(tags=["ingestion"])


@router.post("/ingest", response_model=IngestResponse, status_code=202)
async def ingest(
    payload: InferenceLogCreate,
    service: Annotated[IngestionService, Depends(get_ingestion_service)],
) -> IngestResponse:
    log = await service.ingest(payload)
    return IngestResponse(id=log["_id"])
