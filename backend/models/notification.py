from datetime import datetime
from typing import Literal, Optional

from beanie import Document, PydanticObjectId
from pydantic import Field


class Notification(Document):
    farmer_id: PydanticObjectId
    type: Literal["weather", "market", "scheme", "disease", "crop", "general"] = "general"
    message: str
    channel: Literal["push", "sms", "email"] = "push"
    is_sent: bool = False
    is_read: bool = False
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "notifications"
        indexes = [
            [("farmer_id", 1), ("is_read", 1), ("created_at", -1)],
            [("is_sent", 1)],
        ]
