from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import Settings, get_settings
from app.db.mongo import get_database
from app.repositories.conversations import ConversationRepository
from app.repositories.inference_logs import InferenceLogRepository
from app.repositories.messages import MessageRepository
from app.sdk.gemini import GeminiProvider
from app.services.chat import ChatService
from app.services.ingestion import IngestionService


SettingsDep = Annotated[Settings, Depends(get_settings)]
DbDep = Annotated[AsyncIOMotorDatabase, Depends(get_database)]


def get_conversation_repository(db: DbDep) -> ConversationRepository:
    return ConversationRepository(db)


def get_message_repository(db: DbDep) -> MessageRepository:
    return MessageRepository(db)


def get_inference_log_repository(db: DbDep) -> InferenceLogRepository:
    return InferenceLogRepository(db)


def get_ingestion_service(
    repository: Annotated[InferenceLogRepository, Depends(get_inference_log_repository)],
    settings: SettingsDep,
) -> IngestionService:
    return IngestionService(repository, settings)


def get_gemini_provider(settings: SettingsDep) -> GeminiProvider:
    return GeminiProvider(settings)


def get_chat_service(
    conversations: Annotated[ConversationRepository, Depends(get_conversation_repository)],
    messages: Annotated[MessageRepository, Depends(get_message_repository)],
    ingestion: Annotated[IngestionService, Depends(get_ingestion_service)],
    provider: Annotated[GeminiProvider, Depends(get_gemini_provider)],
    settings: SettingsDep,
) -> ChatService:
    return ChatService(conversations, messages, ingestion, provider, settings)
