from typing import Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    session_id: str = ""
    language: str = "en"
    image_base64: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    response: str
    intent: str
    agent_used: str
    confidence: float
    sources: list[str] = []
    requires_human_help: bool = False
    language: str = "en"


class ChatHistoryItem(BaseModel):
    role: str
    content: str
    agent_used: Optional[str] = None
    created_at: str


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: list[ChatHistoryItem]
