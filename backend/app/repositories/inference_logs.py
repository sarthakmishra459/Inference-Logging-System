from datetime import timedelta
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.time import utc_now
from app.schemas.common import serialize_doc
from app.schemas.ingest import InferenceLogCreate


class InferenceLogRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def create(self, payload: InferenceLogCreate) -> dict[str, Any]:
        data = payload.model_dump()
        token_usage = data.pop("token_usage")
        doc = {
            **data,
            "input_tokens": token_usage["input_tokens"],
            "output_tokens": token_usage["output_tokens"],
            "total_tokens": token_usage["total_tokens"],
            "created_at": utc_now(),
        }
        result = await self.db.inference_logs.insert_one(doc)
        saved = await self.db.inference_logs.find_one({"_id": result.inserted_id})
        return serialize_doc(saved)

    async def dashboard_metrics(self) -> dict[str, Any]:
        since = utc_now() - timedelta(days=7)
        pipeline = [
            {"$match": {"created_at": {"$gte": since}}},
            {
                "$facet": {
                    "summary": [
                        {
                            "$group": {
                                "_id": None,
                                "total_requests": {"$sum": 1},
                                "total_tokens": {"$sum": "$total_tokens"},
                                "average_latency_ms": {"$avg": "$latency_ms"},
                                "errors": {
                                    "$sum": {"$cond": [{"$eq": ["$status", "error"]}, 1, 0]}
                                },
                            }
                        }
                    ],
                    "requests_over_time": [
                        {
                            "$group": {
                                "_id": {
                                    "$dateToString": {
                                        "format": "%Y-%m-%dT%H:00:00Z",
                                        "date": "$created_at",
                                    }
                                },
                                "requests": {"$sum": 1},
                                "errors": {
                                    "$sum": {"$cond": [{"$eq": ["$status", "error"]}, 1, 0]}
                                },
                            }
                        },
                        {"$sort": {"_id": 1}},
                    ],
                    "provider_usage": [
                        {"$group": {"_id": "$provider", "value": {"$sum": 1}}},
                        {"$sort": {"value": -1}},
                    ],
                    "model_usage": [
                        {"$group": {"_id": "$model", "value": {"$sum": 1}}},
                        {"$sort": {"value": -1}},
                    ],
                }
            },
        ]
        results = await self.db.inference_logs.aggregate(pipeline).to_list(length=1)
        data = results[0] if results else {}
        summary = (data.get("summary") or [{}])[0]
        total = summary.get("total_requests", 0) or 0
        errors = summary.get("errors", 0) or 0
        return {
            "average_latency_ms": round(summary.get("average_latency_ms") or 0, 2),
            "total_requests": total,
            "total_tokens": summary.get("total_tokens", 0) or 0,
            "error_rate": round((errors / total) * 100, 2) if total else 0,
            "requests_over_time": [
                {"timestamp": row["_id"], "requests": row["requests"], "errors": row["errors"]}
                for row in data.get("requests_over_time", [])
            ],
            "provider_usage": [
                {"name": row["_id"] or "unknown", "value": row["value"]}
                for row in data.get("provider_usage", [])
            ],
            "model_usage": [
                {"name": row["_id"] or "unknown", "value": row["value"]}
                for row in data.get("model_usage", [])
            ],
        }
