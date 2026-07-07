from typing import Annotated, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgriState(TypedDict):
    # Identity
    user_id: str                        # MongoDB ObjectId of the farmer
    session_id: str                     # Conversation session (Redis checkpointer key)

    # Query
    query: str                          # Raw farmer query text
    language: str                       # Detected language code: hi, en, te, ta, mr, pa, bn, kn
    intent: str                         # Classified intent label from supervisor
    history: str                        # Formatted recent conversation turns (for LLM context)

    # Agent tracking
    active_agent: str                   # Name of agent currently handling the request

    # Input media
    image_base64: Optional[str]         # Base64 encoded image (disease detection)

    # Context
    farmer_profile: dict                # Full farmer profile fetched from MongoDB
    retrieved_context: list[str]        # RAG chunks returned by rag_tool
    tool_outputs: dict                  # Raw outputs from all tool calls (keyed by tool name)

    # Response
    agent_response: str                 # Final structured response text
    confidence: float                   # Response confidence score (0.0–1.0)
    requires_human_help: bool           # True when confidence < 0.6 → KVK escalation
    sources: list[str]                  # RAG citation list (document names + chunk refs)

    # Conversation history (LangGraph manages message state)
    messages: Annotated[list, add_messages]


# Intent labels used by the Supervisor Agent
INTENT_CROP = "crop"
INTENT_DISEASE = "disease"
INTENT_WEATHER = "weather"
INTENT_MARKET = "market"
INTENT_SCHEME = "scheme"
INTENT_SOIL = "soil"
INTENT_NOTIFICATION = "notification"
INTENT_GENERAL = "general"

VALID_INTENTS = {
    INTENT_CROP,
    INTENT_DISEASE,
    INTENT_WEATHER,
    INTENT_MARKET,
    INTENT_SCHEME,
    INTENT_SOIL,
    INTENT_NOTIFICATION,
    INTENT_GENERAL,
}

# Routing keywords used by supervisor for fast pre-classification
INTENT_KEYWORDS: dict[str, list[str]] = {
    INTENT_CROP: [
        "crop", "sowing", "harvest", "seed", "variety", "nursery",
        "rotation", "transplant", "germination", "kharif", "rabi", "zaid",
        "fasal", "beej", "kheti", "ugana",
    ],
    INTENT_DISEASE: [
        "disease", "spot", "wilt", "blight", "fungus", "pest", "insect",
        "symptom", "leaf", "yellow", "rot", "rust", "mildew", "aphid",
        "bimari", "keeda", "rog", "image", "photo", "upload",
    ],
    INTENT_WEATHER: [
        "weather", "rain", "rainfall", "irrigation", "temperature", "forecast",
        "flood", "drought", "fog", "frost", "heat", "cold", "monsoon",
        "mausam", "baarish", "sinchai",
    ],
    INTENT_MARKET: [
        "price", "mandi", "market", "sell", "rate", "enam", "agmarknet",
        "kab beche", "bhav", "dam", "trend", "hold",
    ],
    INTENT_SCHEME: [
        "scheme", "subsidy", "loan", "insurance", "pm-kisan", "pmfby",
        "kcc", "fasal bima", "sarkar", "yojana", "help", "government",
    ],
    INTENT_SOIL: [
        "soil", "npk", "ph", "fertilizer", "urea", "dap", "potash",
        "nutrient", "deficiency", "organic", "compost", "mitti", "khad",
    ],
    INTENT_NOTIFICATION: [
        "alert", "notify", "reminder", "push", "sms", "whatsapp",
    ],
}
