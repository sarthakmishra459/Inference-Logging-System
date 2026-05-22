from pydantic import BaseModel, Field

from app.schemas.conversation import Message


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    conversation_id: str | None = None
    model: str | None = None


class ChatCreatedEvent(BaseModel):
    conversation_id: str
    title: str


class ConversationDetail(BaseModel):
    conversation_id: str
    title: str
    messages: list[Message]
