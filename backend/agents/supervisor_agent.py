import logging
import re

from agents.state import AgriState, INTENT_GENERAL, INTENT_KEYWORDS, VALID_INTENTS

logger = logging.getLogger(__name__)


def _matches(keyword: str, query: str) -> bool:
    """Whole-word match so 'heat' does not match inside 'wheat', etc."""
    return re.search(rf"(?<!\w){re.escape(keyword)}(?!\w)", query) is not None


def _keyword_classify(query: str) -> str | None:
    q = query.lower().strip()
    if q in {"hi", "hello", "hey", "hii", "namaste", "namaskar"}:
        return INTENT_GENERAL

    scores: dict[str, int] = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if _matches(kw, q))
        if score > 0:
            scores[intent] = score
    if not scores:
        return None
    return max(scores, key=lambda k: scores[k])


def run_supervisor(state: AgriState) -> AgriState:
    query = state.get("query", "")
    image = state.get("image_base64")
    existing_intent = state.get("intent", "")

    agent_map = {
        "crop": "crop_agent",
        "disease": "disease_agent",
        "weather": "weather_agent",
        "market": "market_agent",
        "scheme": "scheme_agent",
        "soil": "soil_agent",
        "notification": "notification_agent",
        "general": "rag_agent",
    }

    if existing_intent in VALID_INTENTS:
        logger.info("Supervisor: using preset intent=%s", existing_intent)
        return {
            **state,
            "intent": existing_intent,
            "active_agent": agent_map.get(existing_intent, "rag_agent"),
        }

    if image:
        logger.info("Supervisor: image detected; intent=disease")
        return {**state, "intent": "disease", "active_agent": "disease_agent"}

    intent = _keyword_classify(query) or INTENT_GENERAL
    logger.info("Supervisor: query=%r; intent=%s", query[:60], intent)
    return {**state, "intent": intent, "active_agent": agent_map.get(intent, "rag_agent")}
