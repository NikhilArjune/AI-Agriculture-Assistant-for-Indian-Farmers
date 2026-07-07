import logging

from agents.state import AgriState
from tools.profile_tool import fetch_farmer_profile
from tools.rag_tool import rag_search
from services.llm_service import generate_text

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are Krishi Sahayak, a general agriculture expert for Indian farmers.
Answer the farmer's question using the retrieved knowledge base information.
Be accurate, practical, and specific to Indian farming conditions.
If you are not certain, say so and recommend consulting the local KVK officer.

Respond in the farmer's language ({language}). Plain text only."""


def _is_greeting(query: str) -> bool:
    return query.lower().strip() in {"hi", "hello", "hey", "hii", "namaste", "namaskar"}


def run_rag_agent(state: AgriState) -> AgriState:
    user_id = state["user_id"]
    query = state.get("query", "")
    language = state.get("language", "en")

    profile = fetch_farmer_profile(user_id)
    crops = profile.get("primary_crops", [])
    location = profile.get("location", {})

    if _is_greeting(query):
        response = (
            "Namaste! I am Krishi Sahayak, your agriculture assistant. "
            "Ask me about crops, pests, diseases, weather, market prices, soil, or government schemes."
        )
        return {
            **state,
            "farmer_profile": profile,
            "retrieved_context": [],
            "sources": [],
            "agent_response": response,
            "confidence": 0.9,
            "tool_outputs": {"rag_count": 0},
        }

    # Enrich query with profile context for better retrieval
    enriched_query = f"{query} {' '.join(crops)} {location.get('state', '')}"
    rag_results = rag_search.invoke({"query": enriched_query, "top_k": 6})
    context_chunks = [r["text"] for r in rag_results]
    sources = [r["source"] for r in rag_results]
    avg_score = sum(r.get("score", 0.5) for r in rag_results) / max(len(rag_results), 1)

    context_str = "\n\n".join(context_chunks)

    prompt = f"""{_SYSTEM_PROMPT.format(language=language)}

Farmer Profile:
- Crops: {', '.join(crops)}
- Location: {location.get('district', '')}, {location.get('state', '')}
- Soil: {profile.get('soil_type', 'unknown')}

Knowledge Base:
{context_str}

Farmer's Question: {query}

Answer:"""

    response = generate_text(
        prompt,
        "I could not generate a detailed answer right now. Please consult your local KVK officer for field-specific advice.",
        history=state.get("history", ""),
    )

    confidence = min(avg_score, 0.95)
    logger.info("RAGAgent: user=%s rag_hits=%d avg_score=%.2f", user_id, len(rag_results), avg_score)

    return {
        **state,
        "farmer_profile": profile,
        "retrieved_context": context_chunks,
        "sources": sources,
        "agent_response": response,
        "confidence": confidence,
        "tool_outputs": {"rag_count": len(rag_results)},
    }
