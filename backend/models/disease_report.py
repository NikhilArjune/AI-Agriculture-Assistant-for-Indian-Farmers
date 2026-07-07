from datetime import datetime
from typing import Optional

from beanie import Document, PydanticObjectId
from pydantic import Field


class DiseaseReport(Document):
    farmer_id: PydanticObjectId
    session_id: str
    crop_name: str
    image_url: Optional[str] = None
    detected_disease: str
    confidence: float = 0.0
    treatment_plan: str
    prevention_tips: str = ""
    sources: list[str] = Field(default_factory=list)
    language: str = "en"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "disease_reports"
        indexes = [
            [("farmer_id", 1), ("created_at", -1)],
            [("detected_disease", 1)],
        ]
