import uuid

from fastapi import APIRouter, Depends

from agents.graph import get_graph_with_checkpointer
from agents.state import AgriState
from core.dependencies import require_farmer
from models.farmer_profile import FarmerProfile
from models.user import User
from schemas.disease import DiseaseDetectRequest, DiseaseDetectResponse

router = APIRouter(prefix="/disease", tags=["disease"])


@router.post("/detect", response_model=DiseaseDetectResponse)
async def detect_disease(payload: DiseaseDetectRequest, current_user: User = Depends(require_farmer)):
    profile = await FarmerProfile.find_one(FarmerProfile.user_id == current_user.id)

    session_id = payload.session_id or str(uuid.uuid4())
    query = f"Disease detection for {payload.crop_name or 'crop'}" if payload.crop_name else "Detect disease from image"

    initial_state = AgriState(
        user_id=str(current_user.id),
        session_id=session_id,
        query=query,
        language=payload.language or (profile.preferred_lang if profile else "en"),
        history="",
        intent="disease",
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

    tool_out = result.get("tool_outputs", {})
    disease_result = tool_out.get("disease_detection", {})

    return DiseaseDetectResponse(
        detected_plant=disease_result.get("plant", ""),
        detected_disease=disease_result.get("disease", "Unknown"),
        confidence=result.get("confidence", 0.0),
        treatment_plan=result["agent_response"],
        prevention_tips=disease_result.get("details", ""),
        sources=result.get("sources", []),
        requires_human_help=result.get("requires_human_help", False),
    )
