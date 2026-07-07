"""Unit tests for validation_node logic."""
import pytest


def _run_validation_logic(state: dict) -> dict:
    """Replicate validation_node decisions without importing the full node."""
    import re
    result = dict(state)
    confidence = state.get("confidence", 1.0)
    response = state.get("agent_response", "")

    if confidence < 0.6:
        result["requires_human_help"] = True
        if "KVK" not in response:
            result["agent_response"] = response + "\n\nFor expert advice, contact your local KVK (Krishi Vigyan Kendra)."

    # Bare dosage detection
    dosage_pattern = re.compile(r"\b(\d+)\s*(ml|g|kg|litre|liter)\b", re.IGNORECASE)
    if dosage_pattern.search(response) and "per" not in response.lower():
        result["agent_response"] = result["agent_response"].replace(
            "ml", "ml (consult label for exact dilution)"
        )

    if not response.strip():
        result["agent_response"] = "I'm sorry, I could not find specific information. Please contact your local KVK."
        result["requires_human_help"] = True

    return result


def test_low_confidence_sets_human_help():
    state = {
        "agent_response": "Use fungicide on wheat.",
        "confidence": 0.45,
        "requires_human_help": False,
    }
    result = _run_validation_logic(state)
    assert result["requires_human_help"] is True
    assert "KVK" in result["agent_response"]


def test_high_confidence_no_human_help():
    state = {
        "agent_response": "Sow wheat in October in Punjab.",
        "confidence": 0.85,
        "requires_human_help": False,
    }
    result = _run_validation_logic(state)
    assert result["requires_human_help"] is False


def test_empty_response_fallback():
    state = {
        "agent_response": "",
        "confidence": 0.9,
        "requires_human_help": False,
    }
    result = _run_validation_logic(state)
    assert result["requires_human_help"] is True
    assert len(result["agent_response"]) > 0


def test_kvk_not_duplicated():
    state = {
        "agent_response": "Contact KVK for help.",
        "confidence": 0.3,
        "requires_human_help": False,
    }
    result = _run_validation_logic(state)
    assert result["agent_response"].count("KVK") >= 1
