from datetime import datetime
from typing import Literal, Optional

from beanie import Document, Indexed
from pydantic import Field


class User(Document):
    phone: Indexed(str, unique=True)
    email: Optional[Indexed(str, unique=True)] = None
    password_hash: str
    role: Literal["farmer", "admin", "agent"] = "farmer"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
