import logging

from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import Settings
from app.repositories.inference_logs import InferenceLogRepository
from app.schemas.ingest import InferenceLogCreate

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self, repository: InferenceLogRepository, settings: Settings):
        self.repository = repository
        self.settings = settings

    async def ingest(self, payload: InferenceLogCreate) -> dict:
        return await self.repository.create(payload)

    async def ingest_best_effort(self, payload: InferenceLogCreate) -> None:
        try:
            await self._ingest_with_retry(payload)
        except Exception:
            logger.exception("Inference log ingestion failed")

    async def _ingest_with_retry(self, payload: InferenceLogCreate) -> None:
        attempts = max(1, self.settings.ingestion_retries + 1)

        @retry(stop=stop_after_attempt(attempts), wait=wait_exponential(multiplier=0.2, max=2))
        async def run() -> None:
            await self.ingest(payload)

        await run()
