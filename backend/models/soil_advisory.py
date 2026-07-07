from datetime import datetime
from typing import Optional

from beanie import Document, PydanticObjectId
from pydantic import Field


class SoilAdvisory(Document):
    farmer_id: PydanticObjectId
    session_id: str
    crop_name: str
    soil_type: str = ""
    ph_level: Optional[float] = None
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    advisory_text: str
    fertilizer_plan: str = ""
    sources: list[str] = Field(default_factory=list)
    language: str = "en"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "soil_advisories"
        indexes = [
            [("farmer_id", 1), ("created_at", -1)],
        ]
