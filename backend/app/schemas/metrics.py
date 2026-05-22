from pydantic import BaseModel


class TimeBucket(BaseModel):
    timestamp: str
    requests: int
    errors: int


class UsageBucket(BaseModel):
    name: str
    value: int


class DashboardMetrics(BaseModel):
    average_latency_ms: float
    total_requests: int
    total_tokens: int
    error_rate: float
    requests_over_time: list[TimeBucket]
    provider_usage: list[UsageBucket]
    model_usage: list[UsageBucket]
