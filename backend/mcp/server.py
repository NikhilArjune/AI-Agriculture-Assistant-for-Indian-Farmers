"""
FastMCP server exposing Krishi Sahayak AI resources.
Run standalone: python -m mcp.server
"""
import logging

from fastmcp import FastMCP

logger = logging.getLogger(__name__)

mcp = FastMCP(
    name="krishi-sahayak",
    version="1.0.0",
    description="AI Agriculture Assistant MCP server for Indian farmers",
)


# --- Resources ---

@mcp.resource("agri://crop-calendar/{crop}/{state}")
async def crop_calendar_resource(crop: str, state: str) -> str:
    """Sowing and harvesting calendar for a crop in a given Indian state."""
    from tools.crop_tool import get_crop_calendar
    result = get_crop_calendar.invoke({"crop_name": crop, "state": state})
    return str(result)


@mcp.resource("agri://market-prices/{commodity}/{district}/{state}")
async def market_prices_resource(commodity: str, district: str, state: str) -> str:
    """Current mandi prices for a commodity in a district."""
    from tools.market_tool import get_mandi_prices
    result = get_mandi_prices.invoke({"commodity": commodity, "district": district, "state": state})
    return str(result)


@mcp.resource("agri://weather/{lat}/{lng}")
async def weather_resource(lat: str, lng: str) -> str:
    """Current weather forecast and farming advisory."""
    from tools.weather_tool import get_weather_forecast
    result = get_weather_forecast.invoke({"lat": float(lat), "lng": float(lng)})
    return str(result)


@mcp.resource("agri://schemes/{state}")
async def schemes_resource(state: str) -> str:
    """Active government schemes for farmers in a state."""
    from tools.scheme_tool import search_schemes
    result = search_schemes.invoke({"state": state, "crop_types": [], "query": ""})
    return str(result)


@mcp.resource("agri://soil-advisory/{crop}/{soil_type}")
async def soil_advisory_resource(crop: str, soil_type: str) -> str:
    """Soil and fertilizer advisory for a crop type."""
    from tools.soil_tool import analyze_soil
    inputs = {"crop_name": crop, "soil_type": soil_type, "ph_level": None, "nitrogen": None, "phosphorus": None, "potassium": None}
    result = analyze_soil.invoke({"soil_inputs": inputs, "crop_name": crop})
    return str(result)


@mcp.resource("agri://knowledge/{query}")
async def knowledge_resource(query: str) -> str:
    """RAG-based knowledge retrieval from agricultural documents."""
    from tools.rag_tool import rag_search
    results = rag_search.invoke({"query": query, "top_k": 5})
    texts = [r["text"] for r in results if isinstance(r, dict)]
    return "\n\n".join(texts)


@mcp.resource("agri://farmer-profile/{user_id}")
async def farmer_profile_resource(user_id: str) -> str:
    """Farmer profile data for a given user ID."""
    from tools.profile_tool import fetch_farmer_profile
    profile = fetch_farmer_profile(user_id)
    return str(profile)


# --- Tools (callable by external MCP clients) ---

@mcp.tool()
async def ask_agriculture_question(question: str, language: str = "en") -> str:
    """Answer any agriculture question using the full LangGraph agent pipeline."""
    from agents.graph import get_graph_with_checkpointer
    from agents.state import AgriState
    import uuid

    state = AgriState(
        user_id="mcp_client",
        session_id=str(uuid.uuid4()),
        query=question,
        language=language,
        intent="",
        active_agent="",
        image_base64=None,
        farmer_profile={},
        retrieved_context=[],
        tool_outputs={},
        agent_response="",
        confidence=0.0,
        requires_human_help=False,
        sources=[],
        messages=[],
    )
    graph = await get_graph_with_checkpointer()
    result = await graph.ainvoke(state, config={"configurable": {"thread_id": state["session_id"]}})
    return result["agent_response"]


if __name__ == "__main__":
    import asyncio
    mcp.run()
