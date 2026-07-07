import logging
import re

from agents.state import AgriState

logger = logging.getLogger(__name__)

_CONFIDENCE_THRESHOLD = 0.6
_KVK_RECOMMENDATION = (
    "\n\nNote: For more accurate advice specific to your field conditions, "
    "please consult your local Krishi Vigyan Kendra (KVK) officer."
)

# Dosage patterns that must have units — e.g. "50 kg" not just "50"
_BARE_DOSAGE_RE = re.compile(r"\b(\d+)\s+(?!kg|g|ml|litre|liter|gram|quintal|ton|percent|%)")


def _has_bare_dosage(text: str) -> bool:
    return bool(_BARE_DOSAGE_RE.search(text))


def run_validation(state: AgriState) -> AgriState:
    response = state.get("agent_response", "")
    confidence = state.get("confidence", 1.0)
    requires_help = False

    # 1. Low confidence → append KVK recommendation
    if confidence < _CONFIDENCE_THRESHOLD:
        response = response + _KVK_RECOMMENDATION
        requires_help = True
        logger.warning(
            "ValidationNode: low confidence=%.2f for user=%s → KVK flag set",
            confidence, state.get("user_id"),
        )

    # 2. Hallucination guard — bare numbers without units in advisory context
    if _has_bare_dosage(response):
        logger.warning(
            "ValidationNode: possible bare dosage detected for user=%s",
            state.get("user_id"),
        )
        # Don't block response, but flag it
        requires_help = True

    # 3. Empty response fallback
    if not response.strip():
        response = (
            "I was unable to generate a response for your query. "
            "Please try rephrasing or contact your local KVK officer."
        )
        requires_help = True
        logger.error("ValidationNode: empty response for user=%s", state.get("user_id"))

    return {**state, "agent_response": response, "requires_human_help": requires_help}
