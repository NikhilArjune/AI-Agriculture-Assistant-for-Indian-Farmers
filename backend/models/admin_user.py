from datetime import datetime
from typing import Literal

from beanie import Document, Indexed
from pydantic import Field


class AdminUser(Document):
    email: Indexed(str, unique=True)
    password_hash: str
    full_name: str
    role: Literal["super_admin", "admin", "support"] = "support"
    permissions: list[str] = Field(default_factory=list)
    is_active: bool = True
    last_login: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "admin_users"
