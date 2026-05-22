from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.common import MongoModel


RequestStatus = Literal["success", "error"]


class TokenUsage(BaseModel):
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)


class InferenceLogCreate(BaseModel):
    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    latency_ms: int = Field(ge=0)
    token_usage: TokenUsage = Field(default_factory=TokenUsage)
    started_at: datetime
    completed_at: datetime
    status: RequestStatus
    conversation_id: str | None = None
    input_preview: str | None = Field(default=None, max_length=500)
    output_preview: str | None = Field(default=None, max_length=500)
    error: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class InferenceLog(MongoModel):
    provider: str
    model: str
    latency_ms: int
    input_tokens: int
    output_tokens: int
    total_tokens: int
    started_at: datetime
    completed_at: datetime
    created_at: datetime
    status: RequestStatus
    conversation_id: str | None = None
    input_preview: str | None = None
    output_preview: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class IngestResponse(BaseModel):
    id: str
    status: str = "accepted"
