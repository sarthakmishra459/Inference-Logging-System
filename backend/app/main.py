import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.time import utc_now
from app.db.mongo import connect_mongo
from app.routes import chat, conversations, ingest, metrics

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.mongo_client = await connect_mongo(settings)
    logger.info("Connected to MongoDB database %s", settings.mongodb_db)
    try:
        yield
    finally:
        app.state.mongo_client.close()
        logger.info("MongoDB connection closed")


app = FastAPI(
    title="Inference Logging System API",
    version="0.1.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "timestamp": utc_now()}


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> ORJSONResponse:
    logger.exception("Unhandled error for %s", request.url.path)
    return ORJSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "timestamp": utc_now().isoformat()},
    )


app.include_router(chat.router)
app.include_router(conversations.router)
app.include_router(ingest.router)
app.include_router(metrics.router)
