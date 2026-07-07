import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from agents.graph import get_graph_with_checkpointer
from agents.state import AgriState
from core.dependencies import require_farmer
from models.farmer_profile import FarmerProfile
from models.user import User
from tools.crop_tool import get_crop_calendar

router = APIRouter(prefix="/crops", tags=["crops"])


class CropAdvisoryRequest(BaseModel):
    crop_name: str
    query: str = ""
    session_id: str = ""


class CropCalendarResponse(BaseModel):
    crop_name: str
    state: str
    sowing_window: str
    harvest_window: str
    varieties: list[str]
    care_tips: list[str]


class CropAdvisoryResponse(BaseModel):
    session_id: str
    crop_name: str
    advisory_text: str
    sources: list[str]
    confidence: float
    requires_human_help: bool


@router.get("/calendar/{crop_name}", response_model=CropCalendarResponse)
async def crop_calendar(crop_name: str, current_user: User = Depends(require_farmer)):
    profile = await FarmerProfile.find_one(FarmerProfile.user_id == current_user.id)
    state = profile.location.state if profile else ""

    result = get_crop_calendar.invoke({"crop_name": crop_name.lower(), "state": state})
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return CropCalendarResponse(
        crop_name=crop_name,
        state=state,
        sowing_window=result.get("sowing_window", ""),
        harvest_window=result.get("harvest_window", ""),
        varieties=result.get("varieties", []),
        care_tips=result.get("care_tips", []),
    )


@router.post("/advisory", response_model=CropAdvisoryResponse)
async def crop_advisory(payload: CropAdvisoryRequest, current_user: User = Depends(require_farmer)):
    profile = await FarmerProfile.find_one(FarmerProfile.user_id == current_user.id)
    if not profile:
        raise HTTPException(status_code=400, detail="Complete your farmer profile first.")

    session_id = payload.session_id or str(uuid.uuid4())
    query = payload.query or f"Crop advisory for {payload.crop_name}"

    initial_state = AgriState(
        user_id=str(current_user.id),
        session_id=session_id,
        query=query,
        language=profile.preferred_lang,
        intent="crop",
        active_agent="",
        image_base64=None,
        farmer_profile={},
        retrieved_context=[],
        tool_outputs={"crop_name": payload.crop_name},
        agent_response="",
        confidence=0.0,
        requires_human_help=False,
        sources=[],
        messages=[],
    )

    graph = await get_graph_with_checkpointer()
    config = {"configurable": {"thread_id": session_id}}
    result = await graph.ainvoke(initial_state, config=config)

    return CropAdvisoryResponse(
        session_id=session_id,
        crop_name=payload.crop_name,
        advisory_text=result["agent_response"],
        sources=result.get("sources", []),
        confidence=result.get("confidence", 0.0),
        requires_human_help=result.get("requires_human_help", False),
    )
