from collections.abc import AsyncIterator
from contextlib import suppress

from google import genai
from google.genai import types

from app.core.config import Settings
from app.sdk.base import LLMMessage, LLMStreamResult, LLMUsage


class GeminiProvider:
    provider_name = "gemini"

    def __init__(self, settings: Settings):
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is required")
        self.settings = settings
        self.client = genai.Client(api_key=settings.gemini_api_key)

    def _to_prompt(self, messages: list[LLMMessage]) -> str:
        formatted = []
        for message in messages:
            role = "Assistant" if message.role == "assistant" else "User"
            formatted.append(f"{role}: {message.content}")
        formatted.append("Assistant:")
        return "\n\n".join(formatted)

    async def stream(self, messages: list[LLMMessage], model: str | None = None) -> LLMStreamResult:
        selected_model = model or self.settings.gemini_model
        prompt = self._to_prompt(messages)
        usage = LLMUsage()

        async def iterator() -> AsyncIterator[str]:
            response_stream = await self.client.aio.models.generate_content_stream(
                model=selected_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=2048,
                ),
            )
            async for chunk in response_stream:
                if chunk.usage_metadata:
                    with suppress(Exception):
                        usage.input_tokens = chunk.usage_metadata.prompt_token_count or 0
                        usage.output_tokens = chunk.usage_metadata.candidates_token_count or 0
                        usage.total_tokens = chunk.usage_metadata.total_token_count or 0
                text = getattr(chunk, "text", None)
                if text:
                    yield text

        return LLMStreamResult(chunks=iterator(), usage=usage)
