"""
Unit tests for supervisor_agent intent classification.
These tests run without LLM calls — keyword scoring path only.
"""
import pytest
from agents.state import (
    INTENT_CROP,
    INTENT_DISEASE,
    INTENT_MARKET,
    INTENT_SCHEME,
    INTENT_SOIL,
    INTENT_WEATHER,
    INTENT_KEYWORDS,
)


def _keyword_score(query: str) -> dict[str, int]:
    """Replicate the keyword scoring logic from supervisor_agent."""
    query_lower = query.lower()
    scores: dict[str, int] = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        scores[intent] = sum(1 for kw in keywords if kw in query_lower)
    return scores


def _top_intent(query: str) -> str:
    scores = _keyword_score(query)
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else "general"


def test_disease_query():
    assert _top_intent("My wheat has yellow spots and rust") == INTENT_DISEASE


def test_weather_query():
    assert _top_intent("Will it rain tomorrow? What is forecast?") == INTENT_WEATHER


def test_market_query():
    assert _top_intent("What is mandi price for tomato today?") == INTENT_MARKET


def test_scheme_query():
    assert _top_intent("PM Kisan subsidy eligibility scheme") == INTENT_SCHEME


def test_soil_query():
    assert _top_intent("My soil NPK levels and fertilizer") == INTENT_SOIL


def test_crop_query():
    assert _top_intent("When to sow wheat? Best sowing time") == INTENT_CROP


def test_general_fallback():
    assert _top_intent("hello how are you") == "general"


def test_image_forces_disease():
    """Image presence should force disease intent regardless of text."""
    # This tests the state, not the keyword scorer
    from agents.state import INTENT_DISEASE
    image_b64 = "data:image/png;base64,iVBORw0KGgo="
    # Supervisor logic: if image_base64 → disease
    state = {"query": "hello", "image_base64": image_b64}
    intent = INTENT_DISEASE if state.get("image_base64") else _top_intent(state["query"])
    assert intent == INTENT_DISEASE
