from datetime import datetime
from typing import Optional

from beanie import Document
from pydantic import Field


class GovernmentScheme(Document):
    scheme_name: str
    ministry: str = ""
    scheme_type: str = ""
    description: str
    benefits: str
    eligibility_criteria: str
    application_process: str = ""
    documents_required: list[str] = Field(default_factory=list)
    target_states: list[str] = Field(default_factory=list)
    target_crops: list[str] = Field(default_factory=list)
    max_land_acres: Optional[float] = None
    min_land_acres: Optional[float] = None
    application_url: str = ""
    is_active: bool = True
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "government_schemes"
        indexes = [
            [("target_states", 1)],
            [("target_crops", 1)],
            [("is_active", 1)],
            [("scheme_name", "text"), ("description", "text")],
        ]
