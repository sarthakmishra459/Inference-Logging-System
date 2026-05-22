from datetime import datetime
from typing import Any

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class MongoModel(BaseModel):
    id: str = Field(alias="_id")

    model_config = ConfigDict(populate_by_name=True)


def serialize_doc(doc: dict[str, Any]) -> dict[str, Any]:
    data = dict(doc)
    if "_id" in data and isinstance(data["_id"], ObjectId):
        data["_id"] = str(data["_id"])
    return data


class ErrorResponse(BaseModel):
    detail: str
    timestamp: datetime
