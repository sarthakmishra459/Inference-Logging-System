import asyncio
import json
import logging
from collections.abc import AsyncIterator

from app.core.config import Settings
from app.core.time import utc_now
from app.repositories.conversations import ConversationRepository
from app.repositories.messages import MessageRepository
from app.schemas.chat import ChatRequest
from app.schemas.ingest import InferenceLogCreate, TokenUsage
from app.sdk.base import LLMMessage, LLMProvider
from app.services.ingestion import IngestionService
from app.services.title import generate_title

logger = logging.getLogger(__name__)


def preview(text: str | None, limit: int = 500) -> str | None:
    if text is None:
        return None
    compact = " ".join(text.split())
    return compact[:limit]


class ChatService:
    def __init__(
        self,
        conversations: ConversationRepository,
        messages: MessageRepository,
        ingestion: IngestionService,
        provider: LLMProvider,
        settings: Settings,
    ):
        self.conversations = conversations
        self.messages = messages
        self.ingestion = ingestion
        self.provider = provider
        self.settings = settings

    async def stream_chat(self, request: ChatRequest) -> AsyncIterator[bytes]:
        conversation = None
        is_new = request.conversation_id is None
        if request.conversation_id:
            conversation = await self.conversations.get(request.conversation_id)
        if not conversation:
            conversation = await self.conversations.create(generate_title(request.message))
            is_new = True

        conversation_id = conversation["_id"]
        if is_new:
            yield self._event("conversation", {"conversation_id": conversation_id, "title": conversation["title"]})

        await self.messages.create(conversation_id, "user", request.message)
        await self.conversations.touch(
            conversation_id,
            title=generate_title(request.message) if is_new else None,
            last_message_preview=request.message,
            increment_messages=1,
        )

        history_docs = await self.messages.list_for_conversation(conversation_id)
        history = [LLMMessage(role=doc["role"], content=doc["content"]) for doc in history_docs]

        output_parts: list[str] = []
        started_at = utc_now()
        status = "success"
        error_message: str | None = None
        stream_result = None
        cancelled = False

        try:
            stream_result = await asyncio.wait_for(
                self.provider.stream(history, model=request.model),
                timeout=self.settings.llm_request_timeout_seconds,
            )
            async for chunk in stream_result.chunks:
                output_parts.append(chunk)
                yield self._event("token", {"text": chunk})
        except asyncio.CancelledError:
            status = "error"
            error_message = "client_cancelled"
            cancelled = True
            raise
        except Exception as exc:
            status = "error"
            error_message = str(exc)
            logger.exception("Chat streaming failed")
            yield self._event("error", {"message": "The model request failed. Please try again."})
        finally:
            completed_at = utc_now()
            latency_ms = int((completed_at - started_at).total_seconds() * 1000)
            assistant_text = "".join(output_parts)

            if assistant_text:
                await self.messages.create(conversation_id, "assistant", assistant_text)
                await self.conversations.touch(
                    conversation_id,
                    last_message_preview=assistant_text,
                    increment_messages=1,
                )

            usage = stream_result.usage if stream_result else None
            await self.ingestion.ingest_best_effort(
                InferenceLogCreate(
                    provider=self.provider.provider_name,
                    model=request.model or self.settings.gemini_model,
                    latency_ms=max(latency_ms, 0),
                    token_usage=TokenUsage(
                        input_tokens=usage.input_tokens if usage else 0,
                        output_tokens=usage.output_tokens if usage else 0,
                        total_tokens=usage.total_tokens if usage else 0,
                    ),
                    started_at=started_at,
                    completed_at=completed_at,
                    status=status,
                    conversation_id=conversation_id,
                    input_preview=preview(request.message),
                    output_preview=preview(assistant_text),
                    error=error_message,
                    metadata={"streaming": True},
                )
            )
            if not cancelled:
                yield self._event("done", {"conversation_id": conversation_id})

    def _event(self, event: str, payload: dict) -> bytes:
        return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n".encode("utf-8")
