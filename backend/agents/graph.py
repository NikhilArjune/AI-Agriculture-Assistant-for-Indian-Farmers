import logging
from functools import lru_cache

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from agents.state import (
    AgriState,
    INTENT_CROP,
    INTENT_DISEASE,
    INTENT_GENERAL,
    INTENT_MARKET,
    INTENT_NOTIFICATION,
    INTENT_SCHEME,
    INTENT_SOIL,
    INTENT_WEATHER,
)
from core.config import settings

logger = logging.getLogger(__name__)


# ── Node imports (imported lazily to avoid circular deps at module load) ──

def _supervisor(state: AgriState) -> AgriState:
    from agents.supervisor_agent import run_supervisor
    return run_supervisor(state)


def _crop_agent(state: AgriState) -> AgriState:
    from agents.crop_agent import run_crop_agent
    return run_crop_agent(state)


def _disease_agent(state: AgriState) -> AgriState:
    from agents.disease_agent import run_disease_agent
    return run_disease_agent(state)


def _weather_agent(state: AgriState) -> AgriState:
    from agents.weather_agent import run_weather_agent
    return run_weather_agent(state)


def _market_agent(state: AgriState) -> AgriState:
    from agents.market_agent import run_market_agent
    return run_market_agent(state)


def _scheme_agent(state: AgriState) -> AgriState:
    from agents.scheme_agent import run_scheme_agent
    return run_scheme_agent(state)


def _soil_agent(state: AgriState) -> AgriState:
    from agents.soil_agent import run_soil_agent
    return run_soil_agent(state)


def _rag_agent(state: AgriState) -> AgriState:
    from agents.rag_agent import run_rag_agent
    return run_rag_agent(state)


def _notification_agent(state: AgriState) -> AgriState:
    from agents.notification_agent import run_notification_agent
    return run_notification_agent(state)


def _validation_node(state: AgriState) -> AgriState:
    from agents.validation_node import run_validation
    return run_validation(state)


def _translation_node(state: AgriState) -> AgriState:
    from agents.translation_node import run_translation
    return run_translation(state)


# ── Routing function ─────────────────────────────────────────────────

def _route_intent(state: AgriState) -> str:
    intent = state.get("intent", INTENT_GENERAL)
    routes = {
        INTENT_CROP: "crop_agent",
        INTENT_DISEASE: "disease_agent",
        INTENT_WEATHER: "weather_agent",
        INTENT_MARKET: "market_agent",
        INTENT_SCHEME: "scheme_agent",
        INTENT_SOIL: "soil_agent",
        INTENT_NOTIFICATION: "notification_agent",
        INTENT_GENERAL: "rag_agent",
    }
    return routes.get(intent, "rag_agent")


# ── Graph builder ────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    graph = StateGraph(AgriState)

    # Nodes
    graph.add_node("supervisor", _supervisor)
    graph.add_node("crop_agent", _crop_agent)
    graph.add_node("disease_agent", _disease_agent)
    graph.add_node("weather_agent", _weather_agent)
    graph.add_node("market_agent", _market_agent)
    graph.add_node("scheme_agent", _scheme_agent)
    graph.add_node("soil_agent", _soil_agent)
    graph.add_node("rag_agent", _rag_agent)
    graph.add_node("notification_agent", _notification_agent)
    graph.add_node("validation_node", _validation_node)
    graph.add_node("translation_node", _translation_node)

    # Entry point
    graph.set_entry_point("supervisor")

    # Supervisor → agent (conditional routing)
    graph.add_conditional_edges(
        "supervisor",
        _route_intent,
        {
            "crop_agent": "crop_agent",
            "disease_agent": "disease_agent",
            "weather_agent": "weather_agent",
            "market_agent": "market_agent",
            "scheme_agent": "scheme_agent",
            "soil_agent": "soil_agent",
            "notification_agent": "notification_agent",
            "rag_agent": "rag_agent",
        },
    )

    # All agents → validation → translation → END
    for agent in (
        "crop_agent",
        "disease_agent",
        "weather_agent",
        "market_agent",
        "scheme_agent",
        "soil_agent",
        "rag_agent",
        "notification_agent",
    ):
        graph.add_edge(agent, "validation_node")

    graph.add_edge("validation_node", "translation_node")
    graph.add_edge("translation_node", END)

    return graph


@lru_cache(maxsize=1)
def get_compiled_graph():
    """Return the compiled LangGraph. Cached at process level."""
    graph = build_graph()
    compiled = graph.compile()
    logger.info("LangGraph compiled successfully.")
    return compiled


# In-memory checkpointer (no Redis needed — data lost on restart)
_memory_checkpointer = MemorySaver()


async def get_graph_with_checkpointer():
    """Return graph compiled with in-memory checkpointer for session persistence."""
    graph = build_graph()
    compiled = graph.compile(checkpointer=_memory_checkpointer)
    return compiled
