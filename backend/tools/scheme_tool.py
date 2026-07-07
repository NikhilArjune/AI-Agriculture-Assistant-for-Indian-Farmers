import asyncio
import logging

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def search_schemes(query: str, state: str = "", crop_types: list = None, land_acres: float = 0) -> list[dict]:
    """Search MongoDB government_schemes collection for matching schemes.

    Returns list of scheme dicts matching the query and farmer profile.
    """
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(_async_search(query, state, crop_types or [], land_acres))
    except Exception as exc:
        logger.error("SchemeTool: search failed: %s", exc)
        return []


async def _async_search(query: str, state_name: str, crop_types: list, land_acres: float) -> list[dict]:
    from models.scheme import GovernmentScheme

    filters = [GovernmentScheme.is_active == True]

    if state_name:
        # Match central schemes + state-specific
        pass

    schemes = await GovernmentScheme.find(*filters).limit(20).to_list()

    # Simple keyword relevance scoring
    q_lower = query.lower()
    scored = []
    for s in schemes:
        score = sum(1 for word in q_lower.split() if word in s.name.lower() or word in s.description.lower())
        if score > 0:
            scored.append((score, s.model_dump(mode="json")))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in scored[:10]]


def check_eligibility(scheme: dict, profile: dict) -> bool:
    """Check if a farmer profile meets a scheme's eligibility criteria."""
    eligibility = scheme.get("eligibility", {})
    land = profile.get("farm_size_acres", 0)
    crops = set(profile.get("primary_crops", []))
    state = profile.get("location", {}).get("state", "")

    # Land size check
    min_land = eligibility.get("min_land_acres")
    if min_land and land < min_land:
        return False

    # Crop type check
    allowed_crops = set(eligibility.get("crop_types", []))
    if allowed_crops and not crops.intersection(allowed_crops):
        return False

    # State check
    allowed_states = set(eligibility.get("states", []))
    if allowed_states and state not in allowed_states:
        return False

    return True
