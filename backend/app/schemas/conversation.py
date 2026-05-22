from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import MongoModel


MessageRole = Literal["user", "assistant", "system"]


class ConversationCreate(BaseModel):
    title: str = "New conversation"


class Conversation(MongoModel):
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    last_message_preview: str | None = None


class MessageCreate(BaseModel):
    conversation_id: str
    role: MessageRole
    content: str = Field(min_length=1)


class Message(MongoModel):
    conversation_id: str
    role: MessageRole
    content: str
    created_at: datetime
