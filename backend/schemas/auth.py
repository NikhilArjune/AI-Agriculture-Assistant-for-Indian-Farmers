from typing import Literal, Optional

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=6, max_length=72)
    full_name: str = Field(..., min_length=2)
    role: Literal["farmer", "admin", "agent"] = "farmer"


class LoginRequest(BaseModel):
    phone: str
    password: str = Field(..., min_length=1, max_length=72)


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: str
    phone: str
    email: Optional[str] = None
    role: str
    is_active: bool
