from datetime import datetime
from typing import Literal, Optional

from beanie import Document, PydanticObjectId
from pydantic import Field


class ChatMessage(Document):
    farmer_id: PydanticObjectId
    session_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    intent: Optional[str] = None
    agent_used: Optional[str] = None
    confidence: Optional[float] = None
    sources: list[str] = Field(default_factory=list)
    language: str = "en"
    has_image: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "chat_history"
        indexes = [
            [("farmer_id", 1), ("session_id", 1), ("created_at", 1)],
            [("session_id", 1)],
            [("created_at", -1)],
        ]
