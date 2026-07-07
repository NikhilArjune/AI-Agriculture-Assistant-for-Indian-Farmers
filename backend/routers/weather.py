import uuid

from fastapi import APIRouter, Depends, HTTPException

from agents.graph import get_graph_with_checkpointer
from agents.state import AgriState
from core.dependencies import require_farmer
from models.farmer_profile import FarmerProfile
from models.user import User
from schemas.weather import WeatherAdvisoryRequest, WeatherAdvisoryResponse

router = APIRouter(prefix="/weather", tags=["weather"])


@router.post("/advisory", response_model=WeatherAdvisoryResponse)
async def weather_advisory(payload: WeatherAdvisoryRequest, current_user: User = Depends(require_farmer)):
    profile = await FarmerProfile.find_one(FarmerProfile.user_id == current_user.id)
    if not profile:
        raise HTTPException(status_code=400, detail="Complete your farmer profile first.")

    session_id = payload.session_id or str(uuid.uuid4())

    initial_state = AgriState(
        user_id=str(current_user.id),
        session_id=session_id,
        query=f"Weather advisory for lat={payload.lat} lng={payload.lng}",
        language=profile.preferred_lang,
        intent="weather",
        active_agent="",
        image_base64=None,
        farmer_profile={},
        retrieved_context=[],
        tool_outputs={"lat": payload.lat, "lng": payload.lng},
        agent_response="",
        confidence=0.0,
        requires_human_help=False,
        sources=[],
        messages=[],
    )

    graph = await get_graph_with_checkpointer()
    config = {"configurable": {"thread_id": session_id}}
    result = await graph.ainvoke(initial_state, config=config)

    weather_data = result.get("tool_outputs", {}).get("weather", {})
    return WeatherAdvisoryResponse(
        advisory_text=result["agent_response"],
        temperature_c=weather_data.get("temperature_c", 0.0),
        humidity_percent=weather_data.get("humidity", 0.0),
        rainfall_mm=weather_data.get("rainfall_mm", 0.0),
        wind_speed_kmh=weather_data.get("wind_speed", 0.0),
        sources=result.get("sources", []),
    )
