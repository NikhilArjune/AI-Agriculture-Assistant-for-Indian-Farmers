import logging

from agents.state import AgriState
from tools.profile_tool import fetch_farmer_profile
from tools.scheme_tool import search_schemes, check_eligibility
from tools.rag_tool import rag_search
from services.llm_service import generate_text

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are Krishi Sahayak, a government scheme advisor for Indian farmers.
Using the matched schemes and farmer profile, explain:
1. Which schemes the farmer is eligible for
2. Benefits of each scheme
3. Required documents
4. How to apply (steps + link)

Respond in the farmer's language ({language}). Plain text only."""


def run_scheme_agent(state: AgriState) -> AgriState:
    user_id = state["user_id"]
    query = state.get("query", "Which government schemes am I eligible for?")
    language = state.get("language", "en")

    profile = fetch_farmer_profile(user_id)
    location = profile.get("location", {})

    # Search MongoDB scheme collection
    schemes = search_schemes.invoke(
        {
            "query": query,
            "state": location.get("state", ""),
            "crop_types": profile.get("primary_crops", []),
            "land_acres": profile.get("farm_size_acres", 0),
        }
    )

    # Check eligibility for top matches
    eligible = [s for s in schemes if check_eligibility(s, profile)]

    # RAG fallback if DB result is thin
    sources = ["MongoDB schemes collection"]
    context_chunks = []
    if len(eligible) < 2:
        rag_results = rag_search.invoke({"query": f"government scheme {query}", "top_k": 4})
        context_chunks = [r["text"] for r in rag_results]
        sources += [r["source"] for r in rag_results]

    scheme_str = "\n".join(
        f"- {s.get('name')}: {s.get('description', '')[:200]}"
        for s in eligible[:5]
    )

    prompt = f"""{_SYSTEM_PROMPT.format(language=language)}

Farmer Profile:
- Location: {location.get('district')}, {location.get('state')}
- Crops: {', '.join(profile.get('primary_crops', []))}
- Farm Size: {profile.get('farm_size_acres', 0)} acres

Query: {query}

Eligible Schemes:
{scheme_str or 'No exact matches found in database.'}

Additional Knowledge:
{chr(10).join(context_chunks)}

Guidance:"""

    response = generate_text(
        prompt,
        "Scheme search completed. Review eligibility, required documents, and official application links before applying.",
        history=state.get("history", ""),
    )

    logger.info("SchemeAgent: user=%s eligible_count=%d", user_id, len(eligible))

    return {
        **state,
        "farmer_profile": profile,
        "retrieved_context": context_chunks,
        "sources": sources,
        "agent_response": response,
        "confidence": 0.82,
        "tool_outputs": {"matched_schemes": eligible},
    }
