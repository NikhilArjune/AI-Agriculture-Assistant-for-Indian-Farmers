from datetime import datetime
from typing import Literal, Optional

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    lat: float = 0.0
    lng: float = 0.0


class Location(BaseModel):
    state: str = ""
    district: str = ""
    village: str = ""
    coordinates: Coordinates = Field(default_factory=Coordinates)


class FarmerProfile(Document):
    user_id: PydanticObjectId
    full_name: str
    preferred_lang: Literal["hi", "en", "te", "ta", "mr", "pa", "bn", "kn"] = "en"
    location: Location = Field(default_factory=Location)
    farm_size_acres: float = 0.0
    soil_type: str = ""
    irrigation_type: Literal["drip", "flood", "rainfed", "sprinkler"] = "rainfed"
    primary_crops: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "farmer_profiles"
        indexes = [
            [("user_id", 1)],
            [("location.district", 1)],
            [("location.state", 1)],
        ]
