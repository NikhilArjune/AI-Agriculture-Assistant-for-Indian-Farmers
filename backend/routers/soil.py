import uuid

from fastapi import APIRouter, Depends, HTTPException

from agents.graph import get_graph_with_checkpointer
from agents.state import AgriState
from core.dependencies import require_farmer
from models.farmer_profile import FarmerProfile
from models.user import User
from schemas.soil import SoilAdvisoryRequest, SoilAdvisoryResponse

router = APIRouter(prefix="/soil", tags=["soil"])


@router.post("/advisory", response_model=SoilAdvisoryResponse)
async def soil_advisory(payload: SoilAdvisoryRequest, current_user: User = Depends(require_farmer)):
    profile = await FarmerProfile.find_one(FarmerProfile.user_id == current_user.id)
    if not profile:
        raise HTTPException(status_code=400, detail="Complete your farmer profile first.")

    session_id = payload.session_id or str(uuid.uuid4())

    initial_state = AgriState(
        user_id=str(current_user.id),
        session_id=session_id,
        query=f"Soil advisory for {payload.crop_name}",
        language=profile.preferred_lang,
        intent="soil",
        active_agent="",
        image_base64=None,
        farmer_profile={},
        retrieved_context=[],
        tool_outputs={
            "crop_name": payload.crop_name,
            "soil_type": payload.soil_type,
            "ph_level": payload.ph_level,
            "nitrogen": payload.nitrogen,
            "phosphorus": payload.phosphorus,
            "potassium": payload.potassium,
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

    soil_out = result.get("tool_outputs", {}).get("soil_analysis", {})
    return SoilAdvisoryResponse(
        advisory_text=result["agent_response"],
        fertilizer_plan=soil_out.get("fertilizer_plan", ""),
        deficiencies=soil_out.get("deficiencies", []),
        recommendations=soil_out.get("recommendations", []),
        sources=result.get("sources", []),
        requires_human_help=result.get("requires_human_help", False),
    )
