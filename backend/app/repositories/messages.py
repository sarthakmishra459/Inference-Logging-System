from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.time import utc_now
from app.schemas.common import serialize_doc
from app.schemas.conversation import MessageRole


class MessageRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def create(self, conversation_id: str, role: MessageRole, content: str) -> dict[str, Any]:
        result = await self.db.messages.insert_one(
            {
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "created_at": utc_now(),
            }
        )
        doc = await self.db.messages.find_one({"_id": result.inserted_id})
        return serialize_doc(doc)

    async def list_for_conversation(self, conversation_id: str, limit: int = 100) -> list[dict[str, Any]]:
        cursor = (
            self.db.messages.find({"conversation_id": conversation_id})
            .sort("created_at", 1)
            .limit(limit)
        )
        return [serialize_doc(doc) async for doc in cursor]
