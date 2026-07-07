import uuid

from fastapi import APIRouter, Depends, HTTPException

from agents.graph import get_graph_with_checkpointer
from agents.state import AgriState
from core.dependencies import require_farmer
from models.farmer_profile import FarmerProfile
from models.user import User
from schemas.market import MarketPriceRequest, MarketPriceResponse

router = APIRouter(prefix="/market", tags=["market"])


@router.post("/prices", response_model=MarketPriceResponse)
async def get_market_prices(payload: MarketPriceRequest, current_user: User = Depends(require_farmer)):
    profile = await FarmerProfile.find_one(FarmerProfile.user_id == current_user.id)
    if not profile:
        raise HTTPException(status_code=400, detail="Complete your farmer profile first.")

    session_id = payload.session_id or str(uuid.uuid4())

    initial_state = AgriState(
        user_id=str(current_user.id),
        session_id=session_id,
        query=f"Market prices for {payload.commodity} in {payload.district}, {payload.state}",
        language=profile.preferred_lang,
        intent="market",
        active_agent="",
        image_base64=None,
        farmer_profile={},
        retrieved_context=[],
        tool_outputs={
            "commodity": payload.commodity,
            "district": payload.district,
            "state": payload.state,
        },
        agent_response="",
        confidence=0.0,
        requires_human_help=False,
        sources=[],
        messages=[],
    )

    graph = await get_graph_with_checkpointer()
    config = {"configurable": {"thread_id": session_id}}
    result = await graph.ainvoke(initial_state, config=config)

    market_data = result.get("tool_outputs", {}).get("market_prices", [])
    trend = result.get("tool_outputs", {}).get("trend", {}).get("trend", "unknown")
    return MarketPriceResponse(
        commodity=payload.commodity,
        district=payload.district,
        prices=market_data,
        recommendation=result["agent_response"],
        trend=trend,
        sources=result.get("sources", []),
    )
