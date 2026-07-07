import uuid
from datetime import datetime

from fastapi import APIRouter, Depends

from agents.graph import get_graph_with_checkpointer
from agents.state import AgriState
from core.dependencies import require_farmer
from models.chat_history import ChatMessage
from models.farmer_profile import FarmerProfile
from models.user import User
from schemas.chat import ChatHistoryItem, ChatHistoryResponse, ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])

# Number of most-recent messages fed back to the LLM as conversation context.
_HISTORY_TURNS = 6


async def _load_history(session_id: str, farmer_id) -> str:
    """Build a plain-text transcript of the last few turns for LLM context."""
    recent = await (
        ChatMessage.find(
            ChatMessage.session_id == session_id,
            ChatMessage.farmer_id == farmer_id,
        )
        .sort("-created_at")
        .limit(_HISTORY_TURNS)
        .to_list()
    )
    recent.reverse()  # oldest → newest
    lines = [
        f"{'Farmer' if m.role == 'user' else 'Assistant'}: {m.content}"
        for m in recent
    ]
    return "\n".join(lines)


@router.post("/", response_model=ChatResponse)
async def chat(payload: ChatRequest, current_user: User = Depends(require_farmer)):
    profile = await FarmerProfile.find_one(FarmerProfile.user_id == current_user.id)

    session_id = payload.session_id or str(uuid.uuid4())
    language = payload.language or (profile.preferred_lang if profile else "en")

    history = await _load_history(session_id, current_user.id)

    initial_state = AgriState(
        user_id=str(current_user.id),
        session_id=session_id,
        query=payload.query,
        language=language,
        history=history,
        intent="",
        active_agent="",
        image_base64=payload.image_base64,
        farmer_profile={},
        retrieved_context=[],
        tool_outputs={},
        agent_response="",
        confidence=0.0,
        requires_human_help=False,
        sources=[],
        messages=[],
    )

    graph = await get_graph_with_checkpointer()
    config = {"configurable": {"thread_id": session_id}}
    result = await graph.ainvoke(initial_state, config=config)

    # Persist to chat history
    for role, content in [("user", payload.query), ("assistant", result["agent_response"])]:
        msg = ChatMessage(
            farmer_id=current_user.id,
            session_id=session_id,
            role=role,
            content=content if role == "user" else result["agent_response"],
            intent=result.get("intent") if role == "assistant" else None,
            agent_used=result.get("active_agent") if role == "assistant" else None,
            confidence=result.get("confidence") if role == "assistant" else None,
            sources=result.get("sources", []) if role == "assistant" else [],
            language=result.get("language", "en"),
            has_image=bool(payload.image_base64),
        )
        await msg.insert()

    return ChatResponse(
        session_id=session_id,
        response=result["agent_response"],
        intent=result.get("intent", ""),
        agent_used=result.get("active_agent", ""),
        confidence=result.get("confidence", 0.0),
        sources=result.get("sources", []),
        requires_human_help=result.get("requires_human_help", False),
        language=result.get("language", "en"),
    )


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_history(session_id: str, current_user: User = Depends(require_farmer)):
    messages = await ChatMessage.find(
        ChatMessage.session_id == session_id,
        ChatMessage.farmer_id == current_user.id,
    ).sort("+created_at").to_list()

    items = [
        ChatHistoryItem(
            role=m.role,
            content=m.content,
            agent_used=m.agent_used,
            created_at=m.created_at.isoformat(),
        )
        for m in messages
    ]

    return ChatHistoryResponse(session_id=session_id, messages=items)
