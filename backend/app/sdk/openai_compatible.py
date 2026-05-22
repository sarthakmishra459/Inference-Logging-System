from collections.abc import AsyncIterator

from app.sdk.base import LLMMessage, LLMStreamResult


class OpenAICompatibleProvider:
    provider_name = "openai-compatible"

    async def stream(self, messages: list[LLMMessage], model: str | None = None) -> LLMStreamResult:
        async def iterator() -> AsyncIterator[str]:
            raise RuntimeError("OpenAI compatible provider is not configured in this deployment")
            yield ""

        return LLMStreamResult(chunks=iterator())
