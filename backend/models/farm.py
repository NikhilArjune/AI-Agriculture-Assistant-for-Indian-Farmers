from datetime import datetime

from beanie import Document, PydanticObjectId
from pydantic import Field


class Farm(Document):
    farmer_id: PydanticObjectId
    farm_name: str = ""
    size_acres: float = 0.0
    soil_type: str = ""
    irrigation_source: str = ""
    location_description: str = ""
    current_crops: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "farms"
        indexes = [
            [("farmer_id", 1)],
        ]
