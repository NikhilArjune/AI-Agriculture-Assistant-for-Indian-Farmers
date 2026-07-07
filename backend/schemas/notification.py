from typing import Literal, Optional

from pydantic import BaseModel


class NotificationCreate(BaseModel):
    type: Literal["weather", "market", "scheme", "disease", "crop", "general"] = "general"
    message: str
    channel: Literal["push", "sms", "email"] = "push"


class NotificationResponse(BaseModel):
    id: str
    type: str
    message: str
    channel: str
    is_sent: bool
    is_read: bool
    created_at: str


class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]
    unread_count: int
