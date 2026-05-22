from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol


@dataclass
class LLMMessage:
    role: str
    content: str


@dataclass
class LLMUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


@dataclass
class LLMStreamResult:
    chunks: AsyncIterator[str]
    usage: LLMUsage = field(default_factory=LLMUsage)


@dataclass
class LLMCallMetadata:
    provider: str
    model: str
    started_at: datetime
    completed_at: datetime | None = None
    latency_ms: int = 0
    status: str = "success"
    error: str | None = None
    usage: LLMUsage = field(default_factory=LLMUsage)


class LLMProvider(Protocol):
    provider_name: str

    async def stream(self, messages: list[LLMMessage], model: str | None = None) -> LLMStreamResult:
        ...
