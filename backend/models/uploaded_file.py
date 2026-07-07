from datetime import datetime
from typing import Literal, Optional

from beanie import Document, PydanticObjectId
from pydantic import Field


class UploadedFile(Document):
    farmer_id: PydanticObjectId
    session_id: str
    original_filename: str
    stored_filename: str
    file_url: str
    file_type: Literal["image", "pdf", "document"] = "image"
    mime_type: str = ""
    size_bytes: int = 0
    purpose: Literal["disease_detection", "soil_report", "kyc", "other"] = "other"
    is_processed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "uploaded_files"
        indexes = [
            [("farmer_id", 1), ("created_at", -1)],
            [("session_id", 1)],
        ]
