import logging

from agents.state import AgriState
from tools.profile_tool import fetch_farmer_profile
from tools.soil_tool import analyze_soil
from tools.rag_tool import rag_search
from services.llm_service import generate_text

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are Krishi Sahayak, a soil and fertilizer advisory expert.
Using the soil analysis and IARI fertilizer guidelines, provide:
1. Soil health summary
2. Deficiencies identified (NPK + micronutrients)
3. Fertilizer recommendation (organic and chemical options with exact dosage)
4. Application schedule aligned to crop growth stage
5. Long-term soil health tips

Respond in the farmer's language ({language}). Plain text only."""


def run_soil_agent(state: AgriState) -> AgriState:
    user_id = state["user_id"]
    query = state.get("query", "What fertilizer should I use?")
    language = state.get("language", "en")
    soil_inputs = state.get("tool_outputs", {}).get("soil_inputs", {})

    profile = fetch_farmer_profile(user_id)
    crops = profile.get("primary_crops", [])

    # Analyze soil data
    analysis = analyze_soil.invoke(
        {"soil_inputs": soil_inputs, "crop_name": crops[0] if crops else ""}
    )

    # RAG retrieval from IARI guidelines
    rag_query = f"fertilizer recommendation {' '.join(crops)} soil {soil_inputs.get('soil_type', '')}"
    rag_results = rag_search.invoke({"query": rag_query, "top_k": 5})
    context_chunks = [r["text"] for r in rag_results]
    sources = [r["source"] for r in rag_results]

    prompt = f"""{_SYSTEM_PROMPT.format(language=language)}

Farmer Crops: {', '.join(crops)}
Query: {query}

Soil Inputs:
{soil_inputs}

Soil Analysis:
{analysis}

IARI / KVK Guidelines:
{chr(10).join(context_chunks)}

Fertilizer Plan:"""

    response = generate_text(
        prompt,
        "Soil analysis completed. Use soil-test based fertilizer application and confirm final dosage with your local KVK or soil testing lab.",
        history=state.get("history", ""),
    )

    logger.info("SoilAgent: user=%s crops=%s", user_id, crops)

    return {
        **state,
        "farmer_profile": profile,
        "retrieved_context": context_chunks,
        "sources": sources,
        "agent_response": response,
        "confidence": 0.83,
        "tool_outputs": {**state.get("tool_outputs", {}), "soil_analysis": analysis},
    }
