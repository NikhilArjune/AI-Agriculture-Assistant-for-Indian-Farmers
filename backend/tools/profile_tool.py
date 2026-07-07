import logging
from datetime import datetime
from typing import Any

from bson import ObjectId
from langchain_core.tools import tool
from pymongo import MongoClient

from core.config import settings

logger = logging.getLogger(__name__)


def fetch_farmer_profile(user_id: str) -> dict:
    """Fetch a farmer profile from sync LangGraph nodes."""
    try:
        client = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=5000)
        profile = client[settings.mongo_db_name]["farmer_profiles"].find_one({"user_id": ObjectId(user_id)})
        client.close()
        return _json_safe(profile or {})
    except Exception as exc:
        logger.warning("ProfileTool: could not fetch profile for %s: %s", user_id, exc)
        return {}


def _json_safe(value: Any) -> Any:
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    return value


@tool
def get_farmer_profile(user_id: str) -> dict:
    """Fetch the farmer's profile from MongoDB by user_id."""
    return fetch_farmer_profile(user_id)
