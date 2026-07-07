from datetime import datetime
from typing import Optional

from beanie import Document, PydanticObjectId
from pydantic import Field


class CropAdvisory(Document):
    farmer_id: PydanticObjectId
    session_id: str
    crop_name: str
    query: str
    advisory_text: str
    sources: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    language: str = "en"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "crop_advisories"
        indexes = [
            [("farmer_id", 1), ("created_at", -1)],
            [("session_id", 1)],
        ]
