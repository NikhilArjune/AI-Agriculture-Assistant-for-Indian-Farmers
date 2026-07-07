from typing import Literal, Optional

from pydantic import BaseModel, Field


class CoordinatesSchema(BaseModel):
    lat: float = 0.0
    lng: float = 0.0


class LocationSchema(BaseModel):
    state: str = ""
    district: str = ""
    village: str = ""
    coordinates: CoordinatesSchema = Field(default_factory=CoordinatesSchema)


class FarmerProfileCreate(BaseModel):
    full_name: str
    preferred_lang: Literal["hi", "en", "te", "ta", "mr", "pa", "bn", "kn"] = "en"
    location: LocationSchema = Field(default_factory=LocationSchema)
    farm_size_acres: float = 0.0
    soil_type: str = ""
    irrigation_type: Literal["drip", "flood", "rainfed", "sprinkler"] = "rainfed"
    primary_crops: list[str] = Field(default_factory=list)


class FarmerProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    preferred_lang: Optional[Literal["hi", "en", "te", "ta", "mr", "pa", "bn", "kn"]] = None
    location: Optional[LocationSchema] = None
    farm_size_acres: Optional[float] = None
    soil_type: Optional[str] = None
    irrigation_type: Optional[Literal["drip", "flood", "rainfed", "sprinkler"]] = None
    primary_crops: Optional[list[str]] = None


class FarmerProfileResponse(BaseModel):
    id: str
    user_id: str
    full_name: str
    preferred_lang: str
    location: LocationSchema
    farm_size_acres: float
    soil_type: str
    irrigation_type: str
    primary_crops: list[str]
