from typing import Any

from bson import ObjectId
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.time import utc_now
from app.schemas.common import serialize_doc


def _oid(value: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ObjectId(value)


class ConversationRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def create(self, title: str = "New conversation") -> dict[str, Any]:
        now = utc_now()
        result = await self.db.conversations.insert_one(
            {
                "title": title,
                "created_at": now,
                "updated_at": now,
                "message_count": 0,
                "last_message_preview": None,
            }
        )
        doc = await self.db.conversations.find_one({"_id": result.inserted_id})
        return serialize_doc(doc)

    async def list(self, limit: int = 50) -> list[dict[str, Any]]:
        cursor = self.db.conversations.find({}).sort("updated_at", -1).limit(limit)
        return [serialize_doc(doc) async for doc in cursor]

    async def get(self, conversation_id: str) -> dict[str, Any] | None:
        doc = await self.db.conversations.find_one({"_id": _oid(conversation_id)})
        return serialize_doc(doc) if doc else None

    async def touch(
        self,
        conversation_id: str,
        *,
        title: str | None = None,
        last_message_preview: str | None = None,
        increment_messages: int = 0,
    ) -> None:
        update: dict[str, Any] = {"$set": {"updated_at": utc_now()}}
        if title:
            update["$set"]["title"] = title
        if last_message_preview is not None:
            update["$set"]["last_message_preview"] = last_message_preview[:180]
        if increment_messages:
            update["$inc"] = {"message_count": increment_messages}
        await self.db.conversations.update_one({"_id": _oid(conversation_id)}, update)

    async def delete(self, conversation_id: str) -> bool:
        oid = _oid(conversation_id)
        result = await self.db.conversations.delete_one({"_id": oid})
        await self.db.messages.delete_many({"conversation_id": conversation_id})
        await self.db.inference_logs.delete_many({"conversation_id": conversation_id})
        return result.deleted_count > 0
