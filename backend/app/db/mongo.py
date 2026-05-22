from collections.abc import AsyncIterator

from fastapi import Depends, Request
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, TEXT

from app.core.config import Settings, get_settings


async def connect_mongo(settings: Settings) -> AsyncIOMotorClient:
    client: AsyncIOMotorClient = AsyncIOMotorClient(settings.mongodb_uri, uuidRepresentation="standard")
    db = client[settings.mongodb_db]
    await create_indexes(db)
    return client


async def create_indexes(db: AsyncIOMotorDatabase) -> None:
    await db.conversations.create_index([("updated_at", DESCENDING)])
    await db.conversations.create_index([("title", TEXT)])
    await db.messages.create_index([("conversation_id", ASCENDING), ("created_at", ASCENDING)])
    await db.messages.create_index([("created_at", DESCENDING)])
    await db.inference_logs.create_index([("created_at", DESCENDING)])
    await db.inference_logs.create_index([("provider", ASCENDING), ("model", ASCENDING)])
    await db.inference_logs.create_index([("conversation_id", ASCENDING), ("created_at", DESCENDING)])
    await db.inference_logs.create_index([("status", ASCENDING)])


async def get_database(request: Request) -> AsyncIterator[AsyncIOMotorDatabase]:
    yield request.app.state.mongo_client[get_settings().mongodb_db]


DatabaseDep = Depends(get_database)
