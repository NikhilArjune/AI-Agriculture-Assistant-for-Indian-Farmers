from datetime import datetime
from typing import Literal

from beanie import Document, PydanticObjectId
from pydantic import Field


class WeatherAlert(Document):
    farmer_id: PydanticObjectId
    district: str
    state: str
    alert_type: Literal["rain", "drought", "frost", "heatwave", "cyclone", "general"] = "general"
    severity: Literal["low", "medium", "high", "critical"] = "low"
    advisory_text: str
    valid_from: datetime = Field(default_factory=datetime.utcnow)
    valid_until: datetime = Field(default_factory=datetime.utcnow)
    is_sent: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "weather_alerts"
        indexes = [
            [("farmer_id", 1), ("created_at", -1)],
            [("district", 1), ("state", 1)],
            [("valid_until", 1)],
        ]
