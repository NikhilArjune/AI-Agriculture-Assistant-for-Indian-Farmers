import logging

from agents.state import AgriState
from services.llm_service import generate_text
from tools.market_tool import get_mandi_prices, get_price_trend
from tools.profile_tool import fetch_farmer_profile

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are Krishi Sahayak, a market price advisor for Indian farmers.
Use only the live mandi price rows below. Do not invent prices.
Give:
1. Current min, max, and modal price range
2. Best mandi among the returned rows
3. Sell now or wait advice with short reasoning

Respond in the farmer's language ({language}). Plain text only."""


def run_market_agent(state: AgriState) -> AgriState:
    user_id = state["user_id"]
    query = state.get("query", "What are the current mandi prices?")
    language = state.get("language", "en")

    profile = fetch_farmer_profile(user_id)
    requested = state.get("tool_outputs", {})
    commodity = requested.get("commodity") or (profile.get("primary_crops") or [""])[0]
    location = profile.get("location", {})
    district = requested.get("district") or location.get("district", "")
    state_name = requested.get("state") or location.get("state", "")

    price_result = get_mandi_prices.invoke(
        {"commodity": commodity, "district": district, "state": state_name}
    )
    trend = get_price_trend.invoke(
        {"commodity": commodity, "district": district, "days": 30}
    )

    source_status = price_result.get("_source_status", "unknown")
    records = price_result.get("records", [])
    market_prices = [_to_price_entry(record, source_status) for record in records]

    if not market_prices:
        response = (
            f"No live AGMARKNET mandi price records were found for {commodity.title()} "
            f"in {district}, {state_name}. Source status: {source_status}. "
            "Please try a nearby district, another commodity, or check the official AGMARKNET/eNAM portal."
        )
    else:
        price_str = "\n".join(
            f"- {p['mandi_name']}: min={p['min_price']}, max={p['max_price']}, "
            f"modal={p['modal_price']} Rs/quintal, date={p['price_date']}"
            for p in market_prices
        )
        prompt = f"""{_SYSTEM_PROMPT.format(language=language)}

Commodity: {commodity}
Location: {district}, {state_name}
Query: {query}
Source: {source_status}
Trend: {trend.get('trend', 'unknown')}

Live Mandi Prices:
{price_str}

Advice:"""
        best = max(market_prices, key=lambda item: item["modal_price"])
        fallback = (
            f"Live AGMARKNET data found for {commodity.title()} in {district}, {state_name}. "
            f"Best modal price shown is Rs. {best['modal_price']} per quintal at {best['mandi_name']}. "
            "Compare transport cost and quality grade before selling."
        )
        response = generate_text(prompt, fallback, history=state.get("history", ""))

    logger.info(
        "MarketAgent: user=%s commodity=%s district=%s state=%s source=%s rows=%d",
        user_id,
        commodity,
        district,
        state_name,
        source_status,
        len(market_prices),
    )

    return {
        **state,
        "farmer_profile": profile,
        "retrieved_context": [],
        "sources": [source_status],
        "agent_response": response,
        "confidence": 0.88 if source_status == "live_agmarknet" else 0.2,
        "tool_outputs": {
            **requested,
            "market_prices": market_prices,
            "raw_market_price": price_result,
            "trend": trend,
        },
    }


def _to_price_entry(record: dict, source_status: str) -> dict:
    return {
        "mandi_name": record.get("market") or "Unknown Mandi",
        "min_price": float(record.get("min") or 0),
        "max_price": float(record.get("max") or 0),
        "modal_price": float(record.get("modal") or 0),
        "unit": "quintal",
        "price_date": record.get("date") or "",
        "source_status": source_status,
    }
