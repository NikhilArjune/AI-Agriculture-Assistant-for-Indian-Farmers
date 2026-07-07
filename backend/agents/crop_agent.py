import logging

from agents.state import AgriState
from tools.profile_tool import fetch_farmer_profile
from tools.rag_tool import rag_search
from tools.crop_tool import get_crop_calendar
from services.llm_service import generate_text

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are Krishi Sahayak, an expert crop advisory agent for Indian farmers.
Use the farmer profile, crop calendar data, and retrieved knowledge to give precise,
actionable advice. Respond in the farmer's language ({language}).
Format: plain text only — no markdown."""


def run_crop_agent(state: AgriState) -> AgriState:
    user_id = state["user_id"]
    query = state["query"]
    language = state.get("language", "en")

    # 1. Fetch farmer profile
    profile = fetch_farmer_profile(user_id)
    crops = profile.get("primary_crops", [])
    location = profile.get("location", {})

    # 2. Crop calendar lookup from MongoDB
    calendar_data = {}
    for crop in crops[:3]:
        calendar_data[crop] = get_crop_calendar.invoke(
            {"crop_name": crop, "state": location.get("state", "")}
        )

    # 3. RAG retrieval
    rag_query = f"crop advisory {query} {' '.join(crops)}"
    rag_results = rag_search.invoke({"query": rag_query, "top_k": 5})
    context_chunks = [r["text"] for r in rag_results]
    sources = [r["source"] for r in rag_results]

    # 4. Build prompt and call LLM
    context_str = "\n\n".join(context_chunks)
    calendar_str = "\n".join(
        f"{crop}: {info}" for crop, info in calendar_data.items()
    )

    prompt = f"""{_SYSTEM_PROMPT.format(language=language)}

Farmer Profile:
- Name: {profile.get('full_name', 'Farmer')}
- Location: {location.get('district', '')}, {location.get('state', '')}
- Crops: {', '.join(crops)}
- Soil: {profile.get('soil_type', 'unknown')}
- Irrigation: {profile.get('irrigation_type', 'unknown')}

Crop Calendar:
{calendar_str}

Knowledge Base Context:
{context_str}

Farmer Query: {query}

Advisory:"""

    response = generate_text(
        prompt,
        (
            f"For {', '.join(crops) or 'your crop'}, follow local sowing windows, "
            "maintain timely irrigation, monitor pests weekly, and consult your KVK "
            "for variety and dosage recommendations specific to your district."
        ),
        history=state.get("history", ""),
    )

    logger.info("CropAgent: responded for user=%s crops=%s", user_id, crops)

    return {
        **state,
        "farmer_profile": profile,
        "retrieved_context": context_chunks,
        "sources": sources,
        "agent_response": response,
        "confidence": 0.85,
        "tool_outputs": {"calendar": calendar_data, "rag_count": len(rag_results)},
    }
